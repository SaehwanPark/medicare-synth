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
