# ARCHITECTURE

Last Reviewed: 2026-07-20
Status: Active Implementation

## Current Repository

The repository contains core Pydantic v2 domain schemas, source/evidence manifests,
and a Polars-backed relational validator framework (`src/medicare_synth/validation.py`).
The component model below records the implemented and planned boundaries.


## Proposed Components

- **Source and evidence adapters** acquire pinned `CMS-2021-SYN-CLAIMS` baseline material
  and consume versioned RKB evidence snapshots (`data/rkb_snapshots/rkb-v{MAJOR}.{MINOR}-{YYYYMMDD}.json`)
  without duplicating archival tools.
- **Executable specifications** own file-year schemas (defined via Pydantic v2 models), grains, types, keys,
  null semantics, provenance statuses, and documented constraints.
- **Canonical model** represents beneficiaries, enrollment, providers, plans,
  claims, lines, prescriptions, and care events independently of export layout.
- **Normalization** preserves recoverable raw values and lineage while converting
  official baseline records into canonical typed entities.
- **Validation** evaluates field (Pydantic), record, relational (Polars lazy frames), administrative, scenario,
  and distributional properties and reports findings without silently repairing
  baseline anomalies.
- **Generation and Expansion** applies deterministic rules, `TabDatSynthAdapter` vertical feature synthesis, and `HorizontalExpander` connected-subgraph scaling with deterministic re-keying after validation gates pass.
- **Scenario catalog & CI exporter** provides `ScenarioCatalog` for inspecting named fixtures (`valid_baseline_cohort`, `valid_chronic_subgroup`, `valid_carrier_line_item`, `invalid_orphaned_claim`, `invalid_temporal_inversion`, `invalid_inpatient_admission`, `invalid_pde_days_supply`, `invalid_snf_utilization_days`, `invalid_hha_utilization_days`, `invalid_dme_line_item_count`, `invalid_hospice_utilization_days`, `invalid_mbsf_chronic_condition_indicator`, `invalid_mbsf_cost_use_payment`, `invalid_mbsf_part_d_contract`, `invalid_mbsf_base_coverage_months`, `invalid_mbsf_other_chronic_condition_indicator`, `invalid_mbsf_ndi_match_indicator`, `invalid_mbsf_risk_adjustment_score`, `invalid_mbsf_part_c_contract`, `invalid_mbsf_ffs_utilization_count`) and automated `export-ci` generation.



- **Schema & evidence snapshot diff engine** (`SchemaDiffer`) compares RKB evidence snapshots or schema models to detect added, removed, and breaking field modifications (`medicare-synth diff`).
- **Limitations & dataset boundary profiler** (`LimitationsProfiler`) generates explicit 6-category disclosures covering structural, relational, temporal, accounting, distributional, and inferential boundaries (`limitations_profile.json`).
- **Data Quality & Privacy Audit Suite** (`AuditEngine`) evaluates relational join coverage, k-anonymity scores over quasi-identifiers, and column-level nullity/uniqueness metrics (`audit_report.json`).
- **Autonomous workflow automation** (`scripts/autonomous_workflow.py`) validates code state (linter, type checker, tests), stages, commits, pushes, creates Pull Requests via the GitHub CLI, and autonomously merges branches to main.
- **Interfaces and exporters** expose a focused Python API and `medicare-synth` CLI (`validate`, `scenario`, `manifest`, `export`, `expand`, `catalog`, `diff`, `profile`, `export-ci`, `audit`) emitting versioned CSV, Parquet, SQL reference queries (`examples/sql_reference.sql`), manifests, fidelity reports, audit reports, and limitations profiles.

These are responsibility boundaries, not an approved Python package layout.


## Data Flow

1. Pin source releases, evidence snapshots, schemas, assumptions, and checksums
  in a release manifest.
2. Translate source documentation into reviewed executable specifications while
  preserving conflicts and unknowns.
3. Normalize official synthetic records into canonical entities and events with
  row- and field-level lineage.
4. Validate the baseline before permitting vertical or horizontal expansion.
5. Generate relation-level entities and events before dependent tables; generate
  columns within each table in topological order.
6. Validate generated data and scenarios against schemas, relationships,
  temporal rules, accounting rules, and declared expected results.
7. Export versioned artifacts with manifests, validation reports, fidelity
  claims, and known deviations.

## Core Invariants

- The official CMS synthetic collection is preserved as immutable source
  material; normalized values remain traceable to recoverable raw values.
- Every field has a declared provenance status: preserved, normalized, re-keyed,
  derived, imputed, synthesized, externally calibrated, or scenario-generated.
- Documentation establishes evidence, not automatically executable semantics;
  unresolved conflicts remain explicit.
- Relation-level generation precedes table-local column generation so keys,
  cardinalities, and event coherence are not reconstructed from independent
  rows.
- Validation precedes broad synthesis and distinguishes errors, warnings,
  informational findings, baseline exceptions, and unresolved assumptions.
- Deterministic manifests and seeds reproduce a release; no hidden wall-clock,
  environment, or global state belongs in the functional core.
- Synthetic output supports development and testing, not unsupported inference
  about the Medicare population.

## External Boundaries

- `rkb-rust` or `resdac-knowledge-base` supplies versioned evidence artifacts (`data/rkb_snapshots/`).
- `tabdat-synth` may supply within-table conditional synthesis through a pinned,
  stable interface after the validation-first core exists.
- **Licensing**: Codebase licensed under Apache License 2.0 (`Apache-2.0`).
- **Data Redistribution**: Raw CMS synthetic data is public domain, acquired via CLI manifest checksum verification into ignored `data/` directories.
- **Artifact Publication**: Release bundles publish versioned Parquet/CSV tables, Pydantic schemas, SHA256 manifests, validation reports, and fidelity profiles.
