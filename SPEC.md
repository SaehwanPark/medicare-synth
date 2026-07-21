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
- **Part D Prescription Drug Event (PDE) Domain Extension**: Implemented `PrescriptionDrugEventRecord` domain model, updated source manifest and RKB evidence snapshot with Part D variables/constraints (`PDE_ID`, `SRVC_DT`, `PROD_SRVC_ID`, `QTY_DSPNSD_NUM`, `DAYS_SUPLY_NUM`, `PTNT_PAY_AMT`, `TOT_RX_CST_AMT`, `VAL_NUM_01`), extended `RelationalValidator` with `check_pde_field_constraints`, updated `ScenarioCompiler` and added `invalid_pde_days_supply` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **Skilled Nursing Facility (SNF) Claims Domain Extension**: Implemented `SkilledNursingFacilityClaimRecord` domain model, updated source manifest and RKB evidence snapshot with SNF variables/constraints (`CLM_ADMSN_DT`, `NCH_BENE_DSCHRG_DT`, `CLM_UTLZTN_DAY_CNT`, `NCVD_DAYS_CNT`, `CLM_PMT_AMT`, `VAL_SNF_01`), extended `RelationalValidator` with `check_snf_field_constraints`, updated `ScenarioCompiler` and added `invalid_snf_utilization_days` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **Home Health Agency (HHA) Claims Domain Extension**: Implemented `HomeHealthAgencyClaimRecord` domain model, updated source manifest and RKB evidence snapshot with HHA variables/constraints (`CLM_ADMSN_DT`, `NCH_BENE_DSCHRG_DT`, `CLM_UTLZTN_DAY_CNT`, `CLM_HHA_LUPA_IND`, `VAL_HHA_01`), extended `RelationalValidator` with `check_hha_field_constraints`, updated `ScenarioCompiler` and added `invalid_hha_utilization_days` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **Durable Medical Equipment (DME) Claims Domain Extension**: Implemented `DurableMedicalEquipmentClaimRecord` domain model, updated source manifest and RKB evidence snapshot with DME variables/constraints (`DME_LINE_ITEM_COUNT`, `LINE_CMS_TYPE_SRVC_CD`, `VAL_DME_01`), extended `RelationalValidator` with `check_dme_field_constraints`, updated `ScenarioCompiler` and added `invalid_dme_line_item_count` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **Hospice Claims Domain Extension**: Implemented `HospiceClaimHeaderRecord` domain model, updated source manifest and RKB evidence snapshot with Hospice variables/constraints (`HOSPICE_TERMINAL_DIAG_CD`, `VAL_HOSPICE_01`), extended `RelationalValidator` with `check_hospice_field_constraints`, updated `ScenarioCompiler` and added `invalid_hospice_utilization_days` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **MBSF Chronic Conditions Segment Domain Extension**: Implemented `MBSFChronicConditionsRecord` domain model, updated source manifest and RKB evidence snapshot with MBSF CC variables/constraints (`SP_ALZHMD`, `SP_CHF`, `SP_CHRNKIDN`, `SP_CNCR`, `SP_DIABETES`, `SP_ISCHDMT`, `SP_STRKETIA`, `VAL_MBSF_01`), extended `RelationalValidator` with `check_mbsf_cc_field_constraints`, updated `ScenarioCompiler` and added `invalid_mbsf_chronic_condition_indicator` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **MBSF Cost & Use Segment Domain Extension**: Implemented `MBSFCostAndUseRecord` domain model, updated source manifest and RKB evidence snapshot with MBSF Cost & Use variables/constraints (`BENE_MDCR_PAY_AMT`, `BENE_TOT_PAY_AMT`, `BENE_IP_DDCTBL_AMT`, `BENE_CVRD_DYS_CNT`, `VAL_MBSF_CU_01`), extended `RelationalValidator` with `check_mbsf_cu_field_constraints`, updated `ScenarioCompiler` and added `invalid_mbsf_cost_use_payment` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **MBSF Part D Characteristics Segment Domain Extension**: Implemented `MBSFPartDRecord` domain model, updated source manifest and RKB evidence snapshot with MBSF Part D variables/constraints (`PTD_CNTRCT_ID_01`, `PTD_PBP_ID_01`, `PTD_SGNT_CD_01`, `RDS_IND_01`, `LI_COST_SHRH_GRP_CD_01`, `BENE_PTD_TRCC_AMT`, `BENE_PTD_MOOP_AMT`, `VAL_MBSF_D_01`), extended `RelationalValidator` with `check_mbsf_d_field_constraints`, updated `ScenarioCompiler` and added `invalid_mbsf_part_d_contract` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **MBSF Base / Enrollment Segment Domain Extension**: Implemented `MBSFBaseEnrollmentRecord` domain model, updated source manifest and RKB evidence snapshot with MBSF Base variables/constraints (`BENE_HI_CVRAGE_TOT_MONS`, `BENE_SMI_CVRAGE_TOT_MONS`, `BENE_HMO_CVRAGE_TOT_MONS`, `BENE_PTD_CVRAGE_TOT_MONS`, `MDCR_ENTLMT_BUYIN_IND_01`, `DUAL_STUS_CD_01`, `VAL_MBSF_BASE_01`), extended `RelationalValidator` with `check_mbsf_base_field_constraints`, updated `ScenarioCompiler` and added `invalid_mbsf_base_coverage_months` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **MBSF Other Chronic Conditions Segment Domain Extension**: Implemented `MBSFOtherChronicConditionsRecord` domain model, updated source manifest and RKB evidence snapshot with MBSF Other Chronic variables/constraints (`SP_ARTHGLAU`, `SP_ASTHMA`, `SP_ATRIALF`, `SP_HYPERL`, `SP_HYPERT`, `SP_HYPOT`, `SP_OSTEOP`, `VAL_MBSF_OC_01`), extended `RelationalValidator` with `check_mbsf_oc_field_constraints`, updated `ScenarioCompiler` and added `invalid_mbsf_other_chronic_condition_indicator` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **MBSF National Death Index (NDI) Segment Domain Extension**: Implemented `MBSFNDIRecord` domain model, updated source manifest and RKB evidence snapshot with MBSF NDI variables/constraints (`NDI_MATCH_IND`, `NDI_DIUSE_CD`, `VAL_MBSF_NDI_01`), extended `RelationalValidator` with `check_mbsf_ndi_field_constraints`, updated `ScenarioCompiler` and added `invalid_mbsf_ndi_match_indicator` scenario fixture, and updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and CLI subcommands.
- **CLI Subcommand Extensions**: Added `catalog`, `diff`, `profile`, `export-ci`, and `audit` subcommands to `src/medicare_synth/cli.py`.
- **Adoption & Maintenance Test Suite**: Added unit test suite in `tests/test_mbsf_ndi.py` (124 total passing unit tests).







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
