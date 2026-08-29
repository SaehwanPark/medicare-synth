"""Validate the tracked Markdown surface used to build the GitHub Pages site.

The Jekyll build catches template and Markdown syntax errors, but it does not
reliably catch a relative link that points at a missing source page. This small
standard-library check keeps the newcomer navigation and source links honest.
"""

from __future__ import annotations

import re
from pathlib import Path
import sys
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
REQUIRED_PAGES = {
    "index.md",
    "getting-started/installation.md",
    "getting-started/first-run.md",
    "guides/cli.md",
    "guides/scenarios-and-validation.md",
    "guides/release-workflow.md",
    "concepts/data-model.md",
    "concepts/provenance-and-validation.md",
    "reference/limitations.md",
    "reference/project-documents.md",
    "contributing.md",
    "404.md",
}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LIQUID_PATH = re.compile(r"relative_url\s*\}\}")
LIQUID_TARGET = re.compile(r"href=\"\{\{\s*'([^']+)'\s*\|\s*relative_url")
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def page_paths() -> dict[str, Path]:
    """Return source Markdown pages keyed by their relative path."""
    site_roots = {Path(path) for path in REQUIRED_PAGES}
    site_roots.update(
        path
        for root in ("getting-started", "guides", "concepts", "reference")
        for path in (SITE / root).rglob("*.md")
        for path in (path.relative_to(SITE),)
    )
    return {
        relative.as_posix(): SITE / relative
        for relative in site_roots
        if (SITE / relative).exists()
    }


def front_matter(path: Path) -> str:
    """Return front matter or an empty string when a page has none."""
    match = FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    return match.group(1) if match else ""


def is_external(target: str) -> bool:
    """Return whether a Markdown target is not a local documentation link."""
    parsed = urlsplit(target)
    return bool(parsed.scheme or parsed.netloc) or target.startswith(("#", "{{"))


def source_target(page: Path, target: str, pages: dict[str, Path]) -> Path | None:
    """Resolve a local source link to a Markdown page when possible."""
    clean_target = target.split("#", 1)[0].split("?", 1)[0]
    if not clean_target or is_external(clean_target):
        return None

    if clean_target.startswith("/"):
        candidate = (SITE / clean_target.lstrip("/")).resolve()
    else:
        candidate = (page.parent / clean_target).resolve()

    if candidate.suffix == "":
        directory_page = candidate / "index.md"
        file_page = candidate.with_suffix(".md")
        for page_candidate in (directory_page, file_page):
            relative = (
                page_candidate.relative_to(SITE.resolve()).as_posix()
                if page_candidate.is_relative_to(SITE.resolve())
                else ""
            )
            if relative in pages:
                return pages[relative]
        return None
    elif candidate.suffix in {".html", ".htm"}:
        candidate = candidate.with_suffix(".md")

    site_root = SITE.resolve()
    relative = candidate.relative_to(site_root).as_posix() if candidate.is_relative_to(site_root) else ""
    return pages.get(relative)


def check() -> list[str]:
    """Return human-readable documentation site failures."""
    failures: list[str] = []
    pages = page_paths()
    missing = sorted(REQUIRED_PAGES - pages.keys())
    failures.extend(f"missing required page: docs/{path}" for path in missing)

    for relative, page in sorted(pages.items()):
        text = page.read_text(encoding="utf-8")
        metadata = front_matter(page)
        if not metadata:
            failures.append(f"{relative}: missing YAML front matter")
        elif not re.search(r"^title:\s*.+$", metadata, re.MULTILINE):
            failures.append(f"{relative}: front matter is missing title")

        for target in MARKDOWN_LINK.findall(text):
            if is_external(target):
                continue
            if target.startswith("mailto:"):
                continue
            if source_target(page, target, pages) is None:
                failures.append(f"{relative}: broken local link {target}")

    layout = SITE / "_layouts/default.html"
    if not layout.exists():
        failures.append("missing docs/_layouts/default.html")
    else:
        layout_text = layout.read_text(encoding="utf-8")
        for target in LIQUID_TARGET.findall(layout_text):
            if target == "/" or target.startswith("/assets/"):
                continue
            candidate = SITE / f"{target.strip('/')}.md"
            if not candidate.exists():
                failures.append(f"layout: navigation target has no source page {target}")
        if not LIQUID_PATH.search(layout_text):
            failures.append("layout: expected relative_url navigation links")

    return failures


def main() -> int:
    failures = check()
    if failures:
        print("Documentation site checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Documentation site checks passed ({len(page_paths())} Markdown pages).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
