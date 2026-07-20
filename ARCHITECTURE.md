# ARCHITECTURE

Last Reviewed: 2026-07-20
Status: Proposed

## Current Repository

The repository currently contains project and contributor documentation plus a
repo-local agent harness. No production package, public API, executable schema,
validator, or generated dataset exists yet. The component model below records
the intended boundaries that foundation decisions must confirm before code is
claimed to implement them.

## Proposed Components

- **Source and evidence adapters** acquire pinned CMS synthetic source material
  and consume versioned RKB evidence bundles without duplicating archival tools.
- **Executable specifications** own file-year schemas, grains, types, keys,
  null semantics, provenance statuses, and documented constraints.
- **Canonical model** represents beneficiaries, enrollment, providers, plans,
  claims, lines, prescriptions, and care events independently of export layout.
- **Normalization** preserves recoverable raw values and lineage while converting
  official baseline records into canonical typed entities.
- **Validation** evaluates field, record, relational, administrative, scenario,
  and distributional properties and reports findings without silently repairing
  baseline anomalies.
- **Generation** applies deterministic rules and transparent conditional models
  only after applicable validation gates pass.
- **Scenario compiler** creates small named valid and intentionally invalid
  fixtures with stable expected analytic outputs.
- **Interfaces and exporters** will expose a focused Python API and CLI and emit
  versioned CSV, Parquet, SQL fixtures, manifests, and fidelity reports.

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

- `rkb-rust` or `resdac-knowledge-base` supplies versioned evidence artifacts.
- `tabdat-synth` may supply within-table conditional synthesis through a pinned,
  stable interface after the validation-first core exists.
- Exact contracts, versions, schema technology, and artifact publication paths
  remain foundation decisions tracked in `ROADMAP.md`.
