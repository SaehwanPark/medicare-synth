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

Status: Complete

Outputs:

- pinned official CMS synthetic baseline (CMS 2021 Synthetic Claims) and target schema year (2021) [Completed]
- RKB evidence-bundle contract and snapshot policy [Completed]
- canonical schema language and runtime validation decision (Pydantic v2 + Polars / PyArrow) [Completed]
- minimum validation constraint set (Field, Record, Relational, Temporal, Administrative) [Completed]
- first five scenarios with expected analytic outputs (3 valid, 2 invalid) [Completed]
- licensing, redistribution, and artifact publication policy (Apache-2.0 / manifest-based redistribution) [Completed]

Exit criteria:

- each decision cites its evidence and records unresolved assumptions
- component boundaries and public contracts are reflected in the specification
  and architecture
- one representative vertical slice has concrete acceptance tests

## 2. Baseline and Evidence

Status: Complete

Outputs:

- checksummed source manifest and immutable raw baseline inventory [Completed]
- pinned evidence snapshot for beneficiary, carrier, and outpatient files [Completed]
- coverage and conflict report for required fields and relationships [Completed]

Exit criteria:

- every required input has source, retrieval, version, and checksum provenance
- missing or conflicting evidence is explicit and blocks unsupported semantics

## 3. Executable Model and Validation

Status: Complete

Outputs:

- executable file-year schemas and provenance statuses [Completed]
- canonical beneficiary, enrollment, claim, line, provider, and event model [Completed]
- relation-level and column-level DAG contracts [Completed]
- field, record, relational, temporal, administrative, and accounting validators [Completed]
- scenario compiler and normalizer pipeline [Completed]

Exit criteria:

- selected baseline files normalize and round-trip preserved values [Completed]
- validator findings distinguish invalid output, known baseline exceptions, and
  evidence ambiguity [Completed]
- beneficiary, carrier, and outpatient relationships pass focused integration
  tests [Completed]

## 4. Validation-First Release

Status: Complete

Outputs:

- versioned normalized baseline release in CSV and Parquet [Completed]
- focused CLI and Python API for acquisition, inspection, normalization,
  validation, and export [Completed]
- release manifest, validation report, fidelity profile, and known deviations [Completed]

Exit criteria:

- fixed manifests and seeds reproduce checksummed outputs [Completed]
- release claims are limited to properties supported by recorded validation [Completed]
- reference workflows run in Python and SQL [Completed]

## 5. Expansion and Scenarios

Status: Complete

Outputs:

- one evidence-graded vertical expansion proving `tabdat-synth` integration [Completed]
- connected-subgraph horizontal expansion with deterministic re-keying [Completed]
- five named valid and invalid scenarios with expected analytic results [Completed]

Exit criteria:

- expansion preserves keys, temporal order, enrollment compatibility, and event
  coherence [Completed]
- scenarios reproduce expected results and intentional failures deterministically [Completed]

## 6. Adoption and Maintenance

Status: Complete

Outputs:

- curated teaching and CI fixtures, scenario catalog, and cross-language examples [Completed]
- schema and evidence diff workflows for annual updates [Completed]
- optional calibration and known-truth methods profiles where evidence supports
  them [Completed]

Exit criteria:

- annual changes can be reviewed without silently changing prior releases [Completed]
- every published profile states structural, relational, temporal, accounting,
  distributional, and inferential limitations [Completed]
