# ARCHITECTURE

Last Reviewed: 2026-11-06
Status: Active — structural core implemented; evidence-calibration components planned

## Current Repository

Implemented: Pydantic v2 domain schemas, checksummed source/evidence manifests,
Polars-backed validators, deterministic scenarios, normalizer, release export,
vertical/horizontal expansion, catalog/diff/profile/audit, bounded 2022 PUF
importer, CLI, and docs portal.

Planned (evidence-calibrated playground): Evidence IR, estimand compiler,
parameterized synthesis, calibration, multi-world configs, and evaluation.
Prefer narrow modules consistent with existing conventions; do not introduce a
large framework before Phase 1–2 experiments justify it.

## Component Boundaries

### Implemented

- **Source and evidence adapters** — pinned `CMS-2021-SYN-CLAIMS` and versioned
  RKB snapshots; additive 2022 PUF beneficiary/carrier path.
- **Executable specifications** — file-year schemas, grains, keys, null
  semantics, provenance statuses, documented constraints.
- **Canonical model** — beneficiaries, enrollment, providers, claims, lines,
  prescriptions, care events independent of export layout.
- **Normalization** — recoverable raw values and lineage into typed entities.
- **Validation** — field/record/relational/administrative/scenario findings;
  never silently repairs baseline anomalies.
- **Generation and expansion** — `TabDatSynthAdapter` / `VerticalExpander` and
  `HorizontalExpander` (deterministic re-keying). Treat current vertical path as
  structural/fixture synthesis until a conditional synthesizer contract is
  proven.
- **Scenario catalog, schema diff, limitations profile, audit** — teaching/CI
  fixtures, annual snapshot diffs, six-category limitation disclosures,
  join/privacy metrics.
- **Interfaces** — Python API and `medicare-synth` CLI emitting versioned
  tables, manifests, and reports.

### Planned

Responsibility sketch only; package layout may differ:

| Boundary | Role |
| --- | --- |
| **Evidence IR & registry** | Typed findings with provenance, population/time/eligibility, estimand, uncertainty, calibration vs holdout role, review status |
| **Estimand compiler** | IR → eligibility query, derivation plan, estimator, compatibility report, comparison result |
| **Synthesis protocol** | Parameterized generation of coherent beneficiary subgraphs with controllable conditionals |
| **Calibration** | Reweighting then generator-parameter fit; feasibility/ESS/support diagnostics; hard structural gate retained |
| **Worlds** | Versioned context presets and explicit underidentified scenario labels |
| **Evaluation** | Training/held-out evidence fit, synthetic known-truth, nondegeneracy, research-workflow utility |
| **Agent harness** | Assist discovery → extraction → formalization → review → runs; never mutate evidence values or holdout partitions unilaterally |
| **Release/provenance** | Package code, seeds, evidence-set hashes, calibration config, world assumptions, limitations |

Numerical and validation engines must remain fully operable **without** the
agent harness.

## Data Flow

### Structural path (implemented)

1. Pin sources, evidence snapshots, schemas, assumptions, checksums.
2. Translate documentation into reviewed executable specs; keep conflicts explicit.
3. Normalize official synthetic records with row/field lineage.
4. Validate before expansion.
5. Generate relation-level entities before dependent tables; columns in DAG order.
6. Validate generated data and scenarios.
7. Export versioned artifacts with manifests and limitation claims.

### Calibration path (planned)

```text
CMS baseline + schema evidence
        → structural synthesizer → candidate worlds
        → calibration engine ← reviewed Evidence IR ← CMS aggregates + studies
        → calibrated worlds
        → hard structural validation + evidence/held-out/utility reports
        → versioned multi-world releases
```

Beneficiary histories stay coherent subgraphs. Calibration may reweight or
adjust generator parameters; it must not independently corrupt enrollment,
death, and claim relationships.

## Core Invariants

- Official CMS synthetic material remains immutable source; normalized values
  stay traceable to recoverable raw values.
- Every field has a declared provenance status.
- Documentation is evidence, not automatic executable semantics; unresolved
  conflicts stay explicit.
- Relation-level generation precedes table-local column generation.
- Validation precedes broad synthesis; severities stay distinct.
- Deterministic manifests and seeds reproduce a release.
- Synthetic output supports development and testing—not unsupported inference
  about the Medicare population.
- Evidence-calibrated releases additionally require: reviewed evidence IDs and
  roles; frozen train/holdout partitions before fit; hard structural gates;
  honest underidentification and non-representativeness labels.
- Agents propose; humans approve evidence records, estimand implementations,
  transport assumptions, calibration targets, holdout changes, and public
  calibrated releases.

## External Boundaries

- RKB / ResDAC evidence artifacts under `data/rkb_snapshots/`.
- Optional `tabdat-synth` (or successor) behind a pinned synthesis interface
  after the conditional synthesizer contract exists.
- Public CMS aggregates and published Medicare-only literature enter only
  through the reviewed Evidence IR registry—not as ad-hoc numeric targets.
- Licensing: Apache-2.0 code; raw CMS data via manifest checksums into ignored
  `data/`.
- Docs portal: Markdown under `docs/`, GitHub Pages via
  `.github/workflows/pages.yml`.

Strategic design detail:
[`docs/medicare_synth_evidence_calibrated_playground_proposal.md`](docs/medicare_synth_evidence_calibrated_playground_proposal.md).
