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

Status: Active

The current repository provides contributor guidance, a reusable domain harness,
project bookkeeping, and a canonical roadmap. It does not yet implement a CLI,
Python API, schemas, validators, or data generation.

The active foundation milestone must:

- select and pin one official CMS synthetic baseline release and target schema
  year
- define the RKB evidence-bundle and snapshot contract
- select the canonical schema language and runtime validation approach
- define minimum provenance, field, record, relational, and temporal constraints
- specify the first deterministic scenarios and expected analytic outputs
- resolve licensing, source-data redistribution, and artifact publication rules

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
