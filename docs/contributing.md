---
title: "Contributor guide"
description: "Make a focused change, keep project-state documents aligned, and verify the Medicare-Synth repository before handoff."
permalink: /contributing/
---

# Contributor guide

Medicare-Synth favors small, reviewable slices with explicit evidence and
deterministic tests. Start by identifying whether a change affects a domain
contract, a public CLI/API, release claims, or only wording and presentation.

## Local workflow

```shell
git switch main
git pull --ff-only
git switch -c feat/<short-description>
uv sync
```

Use a `fix/` or `refactor/` prefix when that better describes the slice. Keep
unrelated work out of the branch.

## Verification gates

Run the checks that match the change. For a full repository gate:

```shell
uv run pytest
uv run basedpyright
uv run ruff check .
uv sync --dry-run
git diff --check
```

Generated data belongs in ignored `data/` or `dist/` directories. Do not add
raw CMS files, secrets, or environment-specific output to a commit.

## Documentation changes

Keep these canonical files synchronized when a change affects their stated
contract:

- `SPEC.md` — completed, active, and planned technical specifications;
- `ARCHITECTURE.md` — component boundaries and data flow;
- `ROADMAP.md` — milestone status and exit criteria;
- `CHANGELOG.md` — user-visible history; and
- `LESSONS.md` — verified recurring setup or debugging traps only.

The [documentation portal](./) is the newcomer-facing layer. Prefer a
short guide there over making new users reconstruct a workflow from changelog
entries or source code.

## Pull requests

Before opening a PR, inspect the complete diff and report:

1. the task type and bounded slice;
2. files changed and behavior preserved;
3. tests/checks and their results;
4. documentation or project-state updates; and
5. deviations, deferred work, and remaining risks.

The repository’s autonomous workflow can exercise verification and, when
explicitly requested, stage, commit, push, open, and merge a PR:

```shell
uv run medicare-synth auto-workflow --all-checks --dry-run
```

Use the non-dry-run path only when the branch, commit message, PR body, and
merge authorization are understood.

## Domain and provenance changes

Changes to schemas, normalization, validation, generation, scenarios, release
artifacts, or public CLI/API behavior need evidence, focused behavioral tests,
and a review of relational and provenance boundaries. Read
[Data model &amp; grains](concepts/data-model/),
[Provenance &amp; validation](concepts/provenance-and-validation/), and the
[canonical project documents](reference/project-documents/) first.
