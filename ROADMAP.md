# ROADMAP

This is the canonical source for implementation milestones, ordering, outputs,
and exit criteria. The dated
[project proposal](docs/medicare-synth-project-proposal_20260720.md) remains the
source for strategic motivation and broader product analysis.

## 0. Repository Foundation

Status: Complete

Outputs:

- contributor guidance and reusable foundation-slice harness
- specification, architecture, changelog, roadmap, and lessons bookkeeping
- contributor-first README and aligned package description

Exit criteria:

- harness roles, handoffs, review outcomes, and failure policy agree across all
  repository guidance
- current capabilities are distinguished from proposed capabilities
- repository structure and metadata checks pass

## 1. Foundation Decisions

Status: Active

Outputs:

- pinned official CMS synthetic baseline (CMS 2021 Synthetic Claims) and target schema year (2021) [Completed]
- RKB evidence-bundle contract and snapshot policy [Completed]
- canonical schema language and runtime validation decision (Pydantic v2 + Polars / PyArrow) [Completed]
- minimum validation constraint set (Field, Record, Relational, Temporal, Administrative) [Completed]
- first five scenarios with expected analytic outputs (3 valid, 2 invalid) [Completed]
- licensing, redistribution, and artifact publication policy

Exit criteria:

- each decision cites its evidence and records unresolved assumptions
- component boundaries and public contracts are reflected in the specification
  and architecture
- one representative vertical slice has concrete acceptance tests

## 2. Baseline and Evidence

Status: Planned

Outputs:

- checksummed source manifest and immutable raw baseline inventory
- pinned evidence snapshot for beneficiary, carrier, and outpatient files
- coverage and conflict report for required fields and relationships

Exit criteria:

- every required input has source, retrieval, version, and checksum provenance
- missing or conflicting evidence is explicit and blocks unsupported semantics

## 3. Executable Model and Validation

Status: Planned

Outputs:

- executable file-year schemas and provenance statuses
- canonical beneficiary, enrollment, claim, line, provider, and event model
- relation-level and column-level DAG contracts
- field, record, relational, temporal, administrative, and accounting validators

Exit criteria:

- selected baseline files normalize and round-trip preserved values
- validator findings distinguish invalid output, known baseline exceptions, and
  evidence ambiguity
- beneficiary, carrier, and outpatient relationships pass focused integration
  tests

## 4. Validation-First Release

Status: Planned

Outputs:

- versioned normalized baseline release in CSV and Parquet
- focused CLI and Python API for acquisition, inspection, normalization,
  validation, and export
- release manifest, validation report, fidelity profile, and known deviations

Exit criteria:

- fixed manifests and seeds reproduce checksummed outputs
- release claims are limited to properties supported by recorded validation
- reference workflows run in Python and SQL

## 5. Expansion and Scenarios

Status: Planned

Outputs:

- one evidence-graded vertical expansion proving `tabdat-synth` integration
- connected-subgraph horizontal expansion with deterministic re-keying
- five named valid and invalid scenarios with expected analytic results

Exit criteria:

- expansion preserves keys, temporal order, enrollment compatibility, and event
  coherence
- scenarios reproduce expected results and intentional failures deterministically

## 6. Adoption and Maintenance

Status: Planned

Outputs:

- curated teaching and CI fixtures, scenario catalog, and cross-language examples
- schema and evidence diff workflows for annual updates
- optional calibration and known-truth methods profiles where evidence supports
  them

Exit criteria:

- annual changes can be reviewed without silently changing prior releases
- every published profile states structural, relational, temporal, accounting,
  distributional, and inferential limitations
