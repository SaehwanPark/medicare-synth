# CHANGELOG

## Unreleased

### Added

- Implemented `AuditEngine` and `AuditReport` in `src/medicare_synth/audit.py` providing relational join coverage, k-anonymity privacy scoring, and column nullity/uniqueness metrics.
- Exposed `audit` subcommand in `src/medicare_synth/cli.py` (`medicare-synth audit --scenario <name> --output-dir <path>`).
- Added unit test suite in `tests/test_audit.py` (44 total passing unit tests).
- Configured explicit `[build-system]` with `hatchling` backend and `tool.uv.package = true` in `pyproject.toml`.
- Strongly typed `ScenarioCatalog._CATALOG` with `ScenarioEntry` instances, achieving 0 Pyright static type errors.
- Cleaned unused imports across source and test files (`diff.py`, `profile.py`, `test_catalog.py`, `test_diff.py`).

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
- Implemented `ProvenanceStatus` enum in `src/medicare_synth/models.py` tracking 8 field-level lineage categories.
- Created `ScenarioCompiler` in `src/medicare_synth/scenarios.py` compiling 5 named deterministic scenario fixtures into Polars DataFrames.
- Created `BaselineNormalizer` in `src/medicare_synth/normalizer.py` for type-casting raw records to Polars DataFrames with provenance annotations.
- Created unified `medicare-synth` CLI in `src/medicare_synth/cli.py` supporting `validate`, `scenario`, and `manifest` subcommands.
- Registered `[project.scripts] medicare-synth = "medicare_synth.cli:main"` in `pyproject.toml`.
- Added 12 new unit tests across `tests/test_scenarios.py`, `tests/test_normalizer.py`, and `tests/test_cli.py` (26 total passing tests).
- Completed Milestone 3 (Executable Model and Validation) across all deliverables.
- Implemented `ReleaseExporter`, `ReleaseManifest`, `FileReleaseEntry`, and `FidelityProfile` in `src/medicare_synth/release.py`.
- Supported multi-format export of dataset tables to CSV and Parquet formats with automatic SHA256 checksum calculation.
- Automated release bundle metadata generation (`release_manifest.json`, `validation_report.json`, `fidelity_profile.json`, `sql_reference_schema.sql`).
- Exposed `export` subcommand in `medicare-synth` CLI (`src/medicare_synth/cli.py`).
- Added package top-level exports in `src/medicare_synth/__init__.py`.
- Added unit test suite in `tests/test_release.py` (29 total passing unit tests).
- Completed Milestone 4 (Validation-First Release) across all deliverables.
- Implemented `TabDatSynthAdapter` and `VerticalExpander` in `src/medicare_synth/expansion.py` providing evidence-graded vertical feature synthesis.
- Implemented `HorizontalExpander` in `src/medicare_synth/expansion.py` providing connected-subgraph scaling with deterministic re-keying.
- Exposed `expand` subcommand in `medicare-synth` CLI (`src/medicare_synth/cli.py`).
- Added unit test suite in `tests/test_expansion.py` (33 total passing unit tests).
- Resolved linter warnings (`ruff`) and static type-checking issues (`pyright`).
- Completed Milestone 5 (Expansion and Scenarios) across all deliverables.
- Implemented `ScenarioCatalog` and `export_ci_fixtures` in `src/medicare_synth/catalog.py` for structured metadata and lightweight CI test fixtures.
- Implemented `SchemaDiffer` and `DiffReport` in `src/medicare_synth/diff.py` for annual snapshot schema diffing.
- Implemented `LimitationsProfile` and `LimitationsProfiler` in `src/medicare_synth/profile.py` for explicit 6-category limitations disclosure.
- Exposed `catalog`, `diff`, `profile`, and `export-ci` subcommands in `src/medicare_synth/cli.py`.
- Added executable cross-language reference examples in `examples/python_reference.py` and `examples/sql_reference.sql`.
- Added unit test suites in `tests/test_catalog.py`, `tests/test_diff.py`, and `tests/test_profile.py` (40 total passing unit tests).
- Completed Milestone 6 (Adoption and Maintenance) across all deliverables.




### Changed

- Replaced placeholder package metadata with the project description.
