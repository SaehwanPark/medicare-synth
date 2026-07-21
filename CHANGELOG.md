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
- Created CMS 2021 Synthetic Claims baseline source manifest `data/manifests/cms_2021_syn_claims_manifest.json`.
- Created versioned RKB evidence snapshot contract `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Initialized core Python package `src/medicare_synth/` (`manifest.py`, `evidence.py`, `models.py`) with Pydantic v2 models.
- Added unit test suite under `tests/` with 10 passing tests for manifest verification, evidence snapshot lookups, and domain record constraints.
- Added `pytest` dev dependency to `pyproject.toml` and configured `pythonpath = ["src"]`.
- Completed Milestone 2 (Baseline and Evidence) across all deliverables.
- Implemented core validation framework in `src/medicare_synth/validation.py` (`Severity`, `FindingCategory`, `Finding`, `ValidationReport`).
- Added Polars-backed `RelationalValidator` supporting foreign key integrity (`CLM_ID` -> `BENE_ID`), temporal order (`CLM_FROM_DT` <= `CLM_THRU_DT`), and record uniqueness (`REC-001`).
- Added 4 unit tests in `tests/test_validation.py` covering normal validation and anomaly scenarios (`invalid_orphaned_claim`, `invalid_temporal_inversion`).



### Changed

- Replaced placeholder package metadata with the project description.
