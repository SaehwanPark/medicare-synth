# Repository Agents Guide

Keep this file short. Task detail lives in linked docs and skills.

## What

- Medicare-Synth: provenance-backed, structurally valid Medicare synthetic data
  and fixtures, expanding into an **evidence-calibrated research playground**.
- Canonical state: `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CHANGELOG.md`.
- Program direction: versioned, literature-constrained shared population model
  and derived research worlds (planned; see `SPEC.md` and `ROADMAP.md`).
  Audit: `docs/audits/audit-for-project-realignement-20261108.md`.
  Earlier design: `docs/medicare_synth_evidence_calibrated_playground_proposal.md`;
  current canonical state takes precedence.
- Active agent goal: `docs/goal.md`.
- Repo skills: `.agents/skills/`; harness:
  `docs/harness/medicare-synth/team-spec.md`; handoffs: ignored `_workspace/`.
- Raw/temp data: ignored `data/`.

## Why

- Preserve official synthetic sources and evidence before deriving or generating.
- Make grain, provenance, relationships, and limitations explicit—no unsupported
  inferential confidence from fixtures or literature matches.
- Calibration improves contextual plausibility for a declared research purpose;
  it does not recover real beneficiaries or authorize synthetic estimates as
  Medicare findings.
- Agents assist; humans approve evidence, estimands, holdouts, and calibrated
  releases. Engines must run without the harness.

## How

- `uv` for Python; `uv add` for dependencies.
- Prefer types, immutable values, return-oriented errors, effects at boundaries.
- 2-space indent unless a format requires otherwise.
- Domain/release work: follow the harness team-spec; reconcile durable decisions
  into canonical docs.
- Comments: domain rationale, provenance, constraints, non-obvious invariants.
- Public docs are researcher-first (`README.md`, `docs/index.md`,
  `docs/researchers/`); technical guides live under `docs/developers/`.
  Researcher pages and the root README also have a Korean mirror
  (`docs/ko/`, `README.ko.md`); English is the default. Every
  user-facing capability claim needs a code/test/report anchor; never present
  synthetic results as Medicare findings. See
  `docs/developers/documentation-maintenance.md`.
- Verify: `uv sync --dry-run`, `git diff --check`; when code changes, also
  `pytest`, `basedpyright`, `ruff` as configured; when docs/site pages change,
  `python3 scripts/check_documentation_site.py`.
- Record only verified recurring traps in `LESSONS.md`.
- Missing CLI: `command -v <tool>` before concluding unavailable.
