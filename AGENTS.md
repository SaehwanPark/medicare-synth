# Repository Agents Guide

Keep this file short and repo-wide. Use the linked documents and harness for
task-specific detail.

## What

- Medicare-Synth builds provenance-backed, contemporary Medicare synthetic data
  and deterministic research fixtures.
- Canonical project state lives in `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`,
  and `CHANGELOG.md`.
- Repository-local skills live in `.agents/skills/`; inspectable harness
  handoffs live in ignored `_workspace/`.
- Temporary or archived datasets and related artifacts belong in ignored
  `data/`.

## Why

- Preserve official synthetic records and source evidence before deriving or
  generating data.
- Make Medicare file grain, provenance, relationships, and limitations explicit
  so synthetic fixtures do not create unsupported inferential confidence.
- Keep implementation reviewable through typed boundaries, pure transforms,
  deterministic outputs, and validation-first development.

## How

- Use `uv` for Python runtime and dependency workflows; use `uv add` rather than
  editing dependency declarations manually.
- Prefer static types, immutable values where practical, return-oriented error
  handling, and side effects at system boundaries.
- Use 2-space indentation unless a file format requires otherwise.
- For domain or release-affecting work, follow
  `docs/harness/medicare-synth/team-spec.md` and reconcile durable decisions into
  the canonical project documents.
- Keep comments focused on domain rationale, provenance, constraints, and other
  non-obvious invariants.
- Run `uv sync --dry-run` and `git diff --check` for the current documentation
  foundation. Add and run `pytest`, `basedpyright`, and `ruff` checks when those
  tools and source surfaces are configured.
- Record only verified recurring setup or debugging traps in `LESSONS.md`.
- If a required CLI is not found, use `command -v <tool>` before concluding it
  is unavailable.
