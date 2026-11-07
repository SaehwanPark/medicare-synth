"""Validate the tracked Markdown surface used to build the GitHub Pages site.

The Jekyll build catches template and Markdown syntax errors, but it does not
reliably catch a relative link that points at a missing source page. This small
standard-library check keeps the newcomer navigation and source links honest.
"""

from __future__ import annotations

import re
from pathlib import Path
import sys
from urllib.parse import urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
REQUIRED_PAGES = {
    "index.md",
    "researchers/index.md",
    "researchers/what-you-can-do.md",
    "researchers/diabetes-hospitalization-example.md",
    "researchers/getting-started.md",
    "researchers/understanding-the-data.md",
    "researchers/interpreting-results.md",
    "researchers/limitations.md",
    "researchers/faq.md",
    "ko/index.md",
    "ko/researchers/index.md",
    "ko/researchers/what-you-can-do.md",
    "ko/researchers/diabetes-hospitalization-example.md",
    "ko/researchers/getting-started.md",
    "ko/researchers/understanding-the-data.md",
    "ko/researchers/interpreting-results.md",
    "ko/researchers/limitations.md",
    "ko/researchers/faq.md",
    "developers/index.md",
    "developers/installation.md",
    "developers/first-run.md",
    "developers/cli.md",
    "developers/scenarios-and-validation.md",
    "developers/export-and-release.md",
    "developers/data-model.md",
    "developers/provenance-and-validation.md",
    "developers/calibrated-worlds.md",
    "developers/contributing.md",
    "developers/project-documents.md",
    "developers/documentation-maintenance.md",
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
PUBLISHED_ROOTS = (
    "researchers",
    "ko",
    "developers",
    "getting-started",
    "guides",
    "concepts",
    "reference",
)
LEGACY_FORWARDERS = {
    "getting-started/installation.md": "/developers/installation/",
    "getting-started/first-run.md": "/developers/first-run/",
    "guides/cli.md": "/developers/cli/",
    "guides/scenarios-and-validation.md": "/developers/scenarios-and-validation/",
    "guides/release-workflow.md": "/developers/export-and-release/",
    "concepts/data-model.md": "/developers/data-model/",
    "concepts/provenance-and-validation.md": "/developers/provenance-and-validation/",
    "reference/limitations.md": "/researchers/limitations/",
    "reference/project-documents.md": "/developers/project-documents/",
    "contributing.md": "/developers/contributing/",
}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LIQUID_PATH = re.compile(r"relative_url\s*\}\}")
LIQUID_TARGET = re.compile(r"href=\"\{\{\s*'([^']+)'\s*\|\s*relative_url")
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
PERMALINK = re.compile(r"^permalink:\s*[\"']?([^\"'\n]+)", re.MULTILINE)
LANG = re.compile(r"^lang:\s*[\"']?([A-Za-z-]+)", re.MULTILINE)
LANG_ALTERNATE = re.compile(r"^lang_alternate:\s*[\"']?([^\"'\s]+)", re.MULTILINE)


def page_paths() -> dict[str, Path]:
    """Return source Markdown pages keyed by their relative path."""
    site_roots = {Path(path) for path in REQUIRED_PAGES}
    site_roots.update(
        path
        for root in PUBLISHED_ROOTS
        for path in (SITE / root).rglob("*.md")
        for path in (path.relative_to(SITE),)
    )
    if (SITE / "index.md").exists():
        site_roots.add(Path("index.md"))
    if (SITE / "contributing.md").exists():
        site_roots.add(Path("contributing.md"))
    if (SITE / "404.md").exists():
        site_roots.add(Path("404.md"))
    return {
        relative.as_posix(): SITE / relative
        for relative in site_roots
        if (SITE / relative).exists()
    }


def front_matter(path: Path) -> str:
    """Return front matter or an empty string when a page has none."""
    match = FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    return match.group(1) if match else ""


def published_paths(pages: dict[str, Path]) -> dict[str, Path]:
    """Map each maintained source page to its generated Jekyll URL path."""
    paths: dict[str, Path] = {}
    for relative, page in pages.items():
        match = PERMALINK.search(front_matter(page))
        published = match.group(1).strip() if match else f"/{relative[:-3]}/"
        if not published.startswith("/"):
            published = f"/{published}"
        if not published.endswith("/") and not published.endswith(".html"):
            published = f"{published}/"
        paths[published] = page
    return paths


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


def published_target(
    page: Path, target: str, pages: dict[str, Path], published: dict[str, Path]
) -> Path | None:
    """Resolve a local link using the generated page URL, not source location."""
    clean_target = target.split("#", 1)[0].split("?", 1)[0]
    if not clean_target or is_external(clean_target):
        return None

    relative = next((relative for relative, source in pages.items() if source == page), None)
    if relative is None:
        return None
    page_path = next(
        path for path, source in published.items() if source == page
    )
    resolved = urlsplit(urljoin(f"https://site.invalid{page_path}", clean_target)).path
    if not resolved.startswith("/"):
        resolved = f"/{resolved}"
    return published.get(resolved)


def normalize_site_path(path: str) -> str:
    """Return a site path with a leading slash and a trailing slash."""
    path = path.strip()
    if path in {"", "/"}:
        return "/"
    if not path.startswith("/"):
        path = f"/{path}"
    if not path.endswith("/") and not path.endswith(".html"):
        path = f"{path}/"
    return path


def expected_language(relative: str) -> str | None:
    """Return the required page language for researcher-facing mirrors."""
    if relative == "index.md" or relative.startswith("researchers/"):
        return "en"
    if relative == "ko/index.md" or relative.startswith("ko/"):
        return "ko"
    return None


def published_path_for(page: Path, published: dict[str, Path]) -> str | None:
    """Return the generated URL path for a source page."""
    return next((path for path, source in published.items() if source == page), None)


def check_language_pairs(pages: dict[str, Path], published: dict[str, Path]) -> list[str]:
    """Require reciprocal English/Korean alternates on researcher-facing pages.

    English stays the default URL. Korean mirrors live under ``/ko/``. Developer
    pages stay English-only and are not part of the pair contract.
    """
    failures: list[str] = []
    published_by_source = {
        relative: published_path_for(page, published) for relative, page in pages.items()
    }
    for relative, page in sorted(pages.items()):
        required = expected_language(relative)
        if required is None:
            continue
        metadata = front_matter(page)
        lang_match = LANG.search(metadata)
        alternate_match = LANG_ALTERNATE.search(metadata)
        if lang_match is None:
            failures.append(f"{relative}: researcher page is missing lang")
            continue
        lang = lang_match.group(1)
        if lang != required:
            failures.append(f"{relative}: expected lang {required}, found {lang}")
        if alternate_match is None:
            failures.append(f"{relative}: researcher page is missing lang_alternate")
            continue
        alternate = normalize_site_path(alternate_match.group(1))
        if alternate not in published:
            failures.append(f"{relative}: lang_alternate has no published page {alternate}")
            continue
        own_path = published_by_source.get(relative)
        if own_path is None:
            failures.append(f"{relative}: missing published path for language pair")
            continue
        peer = published[alternate]
        peer_meta = front_matter(peer)
        peer_lang = LANG.search(peer_meta)
        peer_alternate = LANG_ALTERNATE.search(peer_meta)
        expected_peer = "ko" if required == "en" else "en"
        if peer_lang is None or peer_lang.group(1) != expected_peer:
            failures.append(
                f"{relative}: lang_alternate {alternate} is not a {expected_peer} page"
            )
        if peer_alternate is None or normalize_site_path(peer_alternate.group(1)) != own_path:
            failures.append(
                f"{relative}: lang_alternate {alternate} does not point back to {own_path}"
            )
    return failures


SHARED_CLAIM_ANCHORS = (
    "404",
    "572",
    "6,000",
    "27.7",
)


def strip_ko_prefix(path: str) -> str:
    """Map a Korean site path onto its English counterpart."""
    if path == "/ko/":
        return "/"
    if path.startswith("/ko/"):
        return f"/{path[len('/ko/'):]}"
    return path


def check_readme_languages() -> list[str]:
    """Require the root README pair to point at each other and at the Korean portal."""
    failures: list[str] = []
    readme = ROOT / "README.md"
    readme_ko = ROOT / "README.ko.md"
    if not readme_ko.exists():
        return ["missing README.ko.md"]
    english = readme.read_text(encoding="utf-8")
    korean = readme_ko.read_text(encoding="utf-8")
    if "README.ko.md" not in english:
        failures.append("README.md: missing link to README.ko.md")
    if "README.md" not in korean:
        failures.append("README.ko.md: missing link to README.md")
    if "/medicare-synth/ko/" not in korean:
        failures.append("README.ko.md: missing link to the Korean docs portal")
    if "/medicare-synth/ko/researchers/" not in korean:
        failures.append("README.ko.md: missing link to the Korean researcher hub")
    for anchor in SHARED_CLAIM_ANCHORS:
        if anchor in english and anchor not in korean:
            failures.append(f"README.ko.md: missing shared claim anchor {anchor}")
    return failures


def check_shared_claim_anchors(
    pages: dict[str, Path], published: dict[str, Path]
) -> list[str]:
    """Keep selected capability anchors identical across English/Korean pairs."""
    failures: list[str] = []
    published_by_source = {
        relative: published_path_for(page, published) for relative, page in pages.items()
    }
    source_by_published = {
        path: relative for relative, path in published_by_source.items() if path
    }
    for relative, page in sorted(pages.items()):
        if expected_language(relative) != "en":
            continue
        metadata = front_matter(page)
        alternate_match = LANG_ALTERNATE.search(metadata)
        if alternate_match is None:
            continue
        alternate = normalize_site_path(alternate_match.group(1))
        peer_relative = source_by_published.get(alternate)
        if peer_relative is None:
            continue
        english = page.read_text(encoding="utf-8")
        korean = pages[peer_relative].read_text(encoding="utf-8")
        for anchor in SHARED_CLAIM_ANCHORS:
            if anchor in english and anchor not in korean:
                failures.append(
                    f"{peer_relative}: missing shared claim anchor {anchor} "
                    f"(present in {relative})"
                )
    return failures


def check_layout_language_nav(layout_text: str) -> list[str]:
    """Require Korean nav destinations to mirror the English path set."""
    failures: list[str] = []
    targets = LIQUID_TARGET.findall(layout_text)
    english_paths = {
        target
        for target in targets
        if target == "/" or target.startswith(("/researchers/", "/developers/"))
    }
    korean_mapped = {
        strip_ko_prefix(target)
        for target in targets
        if target == "/ko/" or target.startswith("/ko/")
    }
    # Developer destinations appear in both shells without a /ko mirror.
    english_without_developers = {
        path for path in english_paths if not path.startswith("/developers/")
    }
    korean_without_developers = {
        path for path in korean_mapped if not path.startswith("/developers/")
    }
    if english_without_developers != korean_without_developers:
        missing_in_ko = sorted(english_without_developers - korean_without_developers)
        missing_in_en = sorted(korean_without_developers - english_without_developers)
        if missing_in_ko:
            failures.append(
                "layout: Korean nav is missing English researcher routes "
                f"{missing_in_ko}"
            )
        if missing_in_en:
            failures.append(
                "layout: English nav is missing Korean-mapped researcher routes "
                f"{missing_in_en}"
            )
    return failures


def layout_source_for(target: str) -> Path | None:
    """Resolve a layout navigation URL to a Markdown source page."""
    clean = target.strip("/")
    if not clean:
        candidate = SITE / "index.md"
        return candidate if candidate.exists() else None
    direct = SITE / f"{clean}.md"
    indexed = SITE / clean / "index.md"
    for candidate in (direct, indexed):
        if candidate.exists():
            return candidate
    return None


def check() -> list[str]:
    """Return human-readable documentation site failures."""
    failures: list[str] = []
    pages = page_paths()
    published = published_paths(pages)
    missing = sorted(REQUIRED_PAGES - pages.keys())
    failures.extend(f"missing required page: docs/{path}" for path in missing)

    seen_permalinks: dict[str, str] = {}
    for relative, page in sorted(pages.items()):
        text = page.read_text(encoding="utf-8")
        metadata = front_matter(page)
        if not metadata:
            failures.append(f"{relative}: missing YAML front matter")
        elif not re.search(r"^title:\s*.+$", metadata, re.MULTILINE):
            failures.append(f"{relative}: front matter is missing title")

        match = PERMALINK.search(metadata)
        if match:
            permalink = match.group(1).strip()
            if permalink in seen_permalinks:
                failures.append(
                    f"{relative}: duplicate permalink {permalink} "
                    f"(also {seen_permalinks[permalink]})"
                )
            else:
                seen_permalinks[permalink] = relative

        if relative in LEGACY_FORWARDERS:
            expected = LEGACY_FORWARDERS[relative]
            if expected not in text:
                failures.append(
                    f"{relative}: forwarder missing destination link {expected}"
                )
            if expected not in published:
                failures.append(
                    f"{relative}: forwarder destination has no published page {expected}"
                )

        for target in MARKDOWN_LINK.findall(text):
            if is_external(target):
                continue
            if target.startswith("mailto:"):
                continue
            source_page = source_target(page, target, pages)
            published_page = published_target(page, target, pages, published)
            if source_page is None and published_page is None:
                failures.append(f"{relative}: broken local link {target}")
            elif published_page is None:
                failures.append(f"{relative}: broken published link {target}")

    failures.extend(check_language_pairs(pages, published))
    failures.extend(check_readme_languages())
    failures.extend(check_shared_claim_anchors(pages, published))

    layout = SITE / "_layouts/default.html"
    if not layout.exists():
        failures.append("missing docs/_layouts/default.html")
    else:
        layout_text = layout.read_text(encoding="utf-8")
        for target in LIQUID_TARGET.findall(layout_text):
            if target == "/" or target.startswith("/assets/"):
                continue
            if layout_source_for(target) is None:
                failures.append(f"layout: navigation target has no source page {target}")
        if not LIQUID_PATH.search(layout_text):
            failures.append("layout: expected relative_url navigation links")
        if 'class="lang-switch"' not in layout_text:
            failures.append("layout: missing language switch")
        if "page.lang_alternate" not in layout_text:
            failures.append("layout: language switch must use page.lang_alternate")
        if "/ko/" not in layout_text:
            failures.append("layout: missing Korean researcher routes")
        failures.extend(check_layout_language_nav(layout_text))

    config = SITE / "_config.yml"
    if config.exists():
        config_text = config.read_text(encoding="utf-8")
        phase_dirs = sorted(
            path.name
            for path in SITE.iterdir()
            if path.is_dir() and path.name.startswith("phase")
        )
        for phase in phase_dirs:
            if phase not in config_text:
                failures.append(f"_config.yml: expected exclude entry for {phase}")
        # Keep a forward cushion for the next few phase folders before they exist.
        for phase in ("phase6", "phase7", "phase8", "phase9"):
            if phase not in config_text:
                failures.append(f"_config.yml: expected exclude entry for {phase}")

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
