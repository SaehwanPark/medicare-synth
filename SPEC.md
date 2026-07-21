# SPEC

## Past

### Project proposal

- Defined Medicare-Synth as a provenance-backed compiler for contemporary
  Medicare synthetic datasets and research fixtures.
- Established the official CMS synthetic collection as the intended empirical
  baseline and structural validity as the initial quality priority.
- Recommended beneficiary enrollment, carrier, and outpatient files as the
  first release boundary.

## Present

### Foundation

Status: Complete

The current repository provides contributor guidance, a reusable domain harness,
project bookkeeping, pinned baseline specifications, canonical validation stack decisions, minimum constraint sets, deterministic scenario definitions, and licensing policies.

Completed Foundation Decisions:

- **Canonical Baseline Pinned**: CMS 2021 Synthetic Claims collection (`CMS-2021-SYN-CLAIMS`) with target schema year **2021** (CCW contemporary file layout).
- **First Release Scope**: Beneficiary Summary File (Beneficiary-Year grain), Carrier Claims File (Claim Line/Header grain), and Outpatient Claims File (Claim Line/Header grain).
- **Provenance Status Taxonomy**: Preserved, normalized, re-keyed, derived, imputed, synthesized, externally calibrated, and scenario-generated.
- **RKB Evidence Contract**: Immutable versioned JSON snapshots (`data/rkb_snapshots/rkb-v{MAJOR}.{MINOR}-{YYYYMMDD}.json`) capturing CCW variable definitions, data types, valid value sets, source URLs, and SHA256 checksums.
- **Canonical Schema & Validation Stack**: Hybrid approach using **Pydantic v2** (`pydantic`) for record-level contracts and scalar validation + **Polars** (`polars`) & **PyArrow** (`pyarrow`) for high-performance tabular relational validation, file I/O, and Parquet export.
- **Minimum Validation Constraint Set**: Formalized 5 validation categories: Field-level (type/format/value set), Record-level (uniqueness/nullability), Relational (foreign key `CLM_ID` -> `BENE_ID`), Temporal (`CLM_FROM_DT` <= `CLM_THRU_DT` <= Death Date), and Administrative (enrollment compatibility).
- **First Five Deterministic Scenarios**: Specified 3 valid baseline scenarios (`valid_baseline_cohort`, `valid_chronic_subgroup`, `valid_carrier_line_item`) and 2 intentional anomaly scenarios (`invalid_orphaned_claim`, `invalid_temporal_inversion`) with expected validator findings.
- **Licensing & Artifact Policy**: Codebase licensed under **Apache-2.0**. CMS synthetic data is public domain, acquired via manifest-based checksums rather than stored in git. Release artifacts package Parquet/CSV tables, Pydantic schemas, SHA256 manifests, validation reports, and fidelity profiles.

### Baseline and Evidence

Status: Complete

Completed Baseline and Evidence Deliverables:

- **Checksummed Source Manifest**: Defined `data/manifests/cms_2021_syn_claims_manifest.json` for CMS 2021 Synthetic Claims spanning Beneficiary Summary, Carrier Claims, and Outpatient Claims files.
- **Pinned RKB Evidence Snapshot**: Created `data/rkb_snapshots/rkb-v1.0-20211231.json` capturing CCW variable definitions, data types, formats, constraints, and valid value contracts.
- **Python Core Package**: Established `src/medicare_synth/` with Pydantic v2 validation models (`SourceManifest`, `FileManifest`, `RKBEvidenceSnapshot`, `VariableContract`, domain entity records).
- **Behavioral Test Suite**: Added 10 passing unit tests under `tests/` for manifest validation, checksum verification logic, evidence snapshot lookups, and domain record constraints.

### Executable Model and Validation

Status: Complete

Completed Executable Model & Validation Deliverables:

- **Validation Core Framework**: Created `src/medicare_synth/validation.py` establishing `Severity`, `FindingCategory`, `Finding`, and `ValidationReport` Pydantic models.
- **High-Performance Relational Validator**: Implemented Polars-backed `RelationalValidator` performing foreign key constraint checks (`CLM_ID` -> `BENE_ID`), temporal inversion detection (`CLM_FROM_DT` <= `CLM_THRU_DT`), and record key uniqueness (`REC-001`).
- **Provenance Status Taxonomy**: Added `ProvenanceStatus` enum (8 lineage statuses) in `src/medicare_synth/models.py`.
- **Deterministic Scenario Compiler**: Created `ScenarioCompiler` in `src/medicare_synth/scenarios.py` compiling 5 named scenarios (`valid_baseline_cohort`, `valid_chronic_subgroup`, `valid_carrier_line_item`, `invalid_orphaned_claim`, `invalid_temporal_inversion`).
- **Baseline Normalizer**: Implemented `BaselineNormalizer` in `src/medicare_synth/normalizer.py` for type-casting raw records to Polars DataFrames and tagging provenance.
- **Unified Release CLI**: Implemented `medicare-synth` CLI entry point in `src/medicare_synth/cli.py` with `validate`, `scenario`, `manifest` commands.
- **Comprehensive Unit Tests**: Added unit tests in `tests/test_scenarios.py`, `tests/test_normalizer.py`, and `tests/test_cli.py` (26 passing tests total).

### Validation-First Release

Status: Complete

Completed Validation-First Release Deliverables:

- **Release Bundle Exporter Framework**: Implemented `src/medicare_synth/release.py` providing `ReleaseExporter`, `ReleaseManifest`, `FileReleaseEntry`, and `FidelityProfile` Pydantic models.
- **Multi-Format Export Pipeline**: Added support for exporting normalized baseline tables and scenario fixtures to versioned CSV and Parquet files with automatic SHA256 checksum tracking.
- **Integrity & Fidelity Reporting**: Added automated generation of `release_manifest.json`, `validation_report.json`, `fidelity_profile.json`, and SQL DDL reference schema (`sql_reference_schema.sql`).
- **CLI Export Subcommand**: Expanded `medicare-synth` CLI entry point with `export` subcommand (`medicare-synth export --scenario <name> --output-dir <path> --format <csv|parquet|all>`).
- **Package API Integration**: Exposed `ReleaseExporter`, `ReleaseManifest`, and `FidelityProfile` at package top level in `src/medicare_synth/__init__.py`.
- **Release Test Suite**: Added 3 unit tests in `tests/test_release.py` covering multi-format exports, fidelity metrics, and CLI export command (29 passing unit tests total).

### Expansion and Scenarios

Status: Complete

Completed Expansion and Scenarios Deliverables:

- **TabDat-Synth Adapter & Vertical Expansion**: Implemented `TabDatSynthAdapter` and `VerticalExpander` in `src/medicare_synth/expansion.py` providing evidence-graded feature synthesis for within-table attributes with `SYNTHESIZED` provenance status while preserving relational keys and temporal invariants.
- **Connected-Subgraph Horizontal Expansion**: Implemented `HorizontalExpander` in `src/medicare_synth/expansion.py` performing deterministic connected-subgraph scaling and re-keying across beneficiary, carrier, and outpatient tables with `REKEYED` provenance status.
- **CLI Expansion Subcommand**: Added `expand` subcommand to `medicare-synth` CLI (`medicare-synth expand --mode <vertical|horizontal> --scenario <name> --scale <factor>`).
- **Expansion Unit Test Suite**: Added 4 unit tests in `tests/test_expansion.py` covering feature synthesis, horizontal scaling, relational validator compatibility, and CLI commands (33 total passing unit tests).

### Adoption and Maintenance

Status: Complete

Completed Adoption and Maintenance Deliverables:

- **Scenario Catalog & CI Fixture Exporter**: Created `src/medicare_synth/catalog.py` providing `ScenarioCatalog` and automated CI fixture export (`medicare-synth export-ci`).
- **Schema & Evidence Snapshot Diff Engine**: Created `src/medicare_synth/diff.py` establishing `SchemaDiffer` and `DiffReport` for comparing RKB evidence snapshots and preventing breaking schema changes during annual updates (`medicare-synth diff`).
- **Explicit Dataset Limitations Disclosure Profile**: Created `src/medicare_synth/profile.py` formalizing structural, relational, temporal, accounting, distributional, and inferential boundaries (`medicare-synth profile`).
- **Cross-Language Reference Examples**: Added `examples/python_reference.py` and `examples/sql_reference.sql` illustrating downstream Polars/DuckDB analytical queries on synthetic release artifacts.
- **Data Quality & Privacy Audit Suite**: Created `src/medicare_synth/audit.py` establishing `AuditEngine` and `AuditReport` for join coverage, k-anonymity privacy scoring, and column metrics.
- **CLI Subcommand Extensions**: Added `catalog`, `diff`, `profile`, `export-ci`, and `audit` subcommands to `src/medicare_synth/cli.py`.
- **Adoption & Maintenance Test Suite**: Added 11 unit tests across `tests/test_catalog.py`, `tests/test_diff.py`, `tests/test_profile.py`, and `tests/test_audit.py` (44 total passing unit tests).



Verification requires each decision to cite evidence, state assumptions, and be

reflected in `ARCHITECTURE.md` and `ROADMAP.md`. No synthesis or release may be
presented as verified before its applicable constraints and tests exist.

Out of scope for the foundation milestone:

- broad coverage of all CMS file families or historical layouts
- claims of population representativeness or clinical validity
- opaque generative models where rules or transparent conditional methods are
  sufficient
- production-scale generation before baseline normalization and validation

## Future

- Acquire, checksum, inventory, and preserve the selected CMS baseline and RKB
  evidence snapshot.
- Define executable schemas, canonical entities and events, relation and column
  DAGs, provenance statuses, and constraint reporting.
- Normalize and round-trip preserved baseline fields before adding synthesis.
- Publish a validation-first release for beneficiary, carrier, and outpatient
  structures.
- Add evidence-graded vertical expansion and relationally coherent horizontal
  expansion.
- Publish deterministic valid and invalid scenarios with expected results.
- Stabilize CLI and Python interfaces, cross-language examples, annual update
  workflows, and explicit fidelity profiles.
