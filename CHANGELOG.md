# CHANGELOG

## Unreleased

### Added

- Contributor-first README and repository-wide agent guidance.
- Portable Medicare foundation-slice harness with deterministic local handoffs
  and bounded domain review.
- Lightweight specification, architecture, roadmap, changelog, and lessons
  documents for project bookkeeping.
- Pinned CMS 2021 Synthetic Claims collection (`CMS-2021-SYN-CLAIMS`) as canonical baseline and 2021 CCW layout as target schema year.
- Defined 8-tag provenance status taxonomy for field-level lineage tracking.
- Established immutable RKB evidence bundle snapshot contract (`data/rkb_snapshots/`).
- Selected Pydantic v2 and Polars / PyArrow as canonical hybrid schema and validation runtime stack.
- Added `pydantic`, `polars`, and `pyarrow` core dependencies to `pyproject.toml`.
- Formalized 5-category minimum validation constraint set (Field, Record, Relational, Temporal, Administrative).
- Specified initial 5 deterministic scenarios (3 valid baseline fixtures, 2 intentional anomaly fixtures).
- Established Apache-2.0 open-source license, manifest-based raw data acquisition rules, and release artifact publication paths.
- Completed Milestone 1 (Foundation Decisions) across all 6 core deliverables.

### Changed

- Replaced placeholder package metadata with the project description.
