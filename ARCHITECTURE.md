# ARCHITECTURE

Last Reviewed: 2026-11-08 (static documentation realignment; no new test run)
Status: Structural core through Phase 5 MVP worlds delivered; Phase 6 independent
evaluation active; shared population-model architecture planned (Phase 7).
Audit source: [November 8 realignment](docs/audits/audit-for-project-realignement-20261108.md).

## Current Repository

Implemented: Pydantic v2 domain schemas, checksummed source/evidence manifests,
Polars-backed validators, deterministic scenarios, normalizer, release export,
vertical/horizontal expansion, catalog/diff/profile/audit, bounded 2022 PUF
importer, CLI, docs portal, Phase 1 conditional synthesizer
(`medicare_synth.synthesis`) for `mvp-2021-om-ffs-diabetes-ip` known-truth
worlds, Phase 2 Evidence IR (`medicare_synth.evidence_ir`) with parse /
validate / compile / execute against synthetic tables, Phase 3 frozen
evidence corpus (`medicare_synth.evidence_corpus`) with checksummed
calibration / holdout / diagnostic / excluded partitions, and Phase 4
calibration engine (`medicare_synth.calibration`) with Level A/B/C APIs,
run manifests, and agent role contracts, Phase 5 multi-world packaging
(`medicare_synth.worlds`) with shared-target family releases, and an
evaluation freeze (`medicare_synth.evaluation`) that keeps holdout/diagnostic
partitions evaluate-only.

Phase 0 (`docs/phase0/`) pinned the MVP context. Phase 1 (`docs/phase1/`)
proved controllable diabetes → IP conditionals with reproducibility, structural
gates, held-out recovery, and a clone-only negative control.
Phase 2 (`docs/phase2/`) formalized LIT-03 as a reviewed diagnostic finding and
refuses unsupported rate semantics (LIT-02 planned-admission) explicitly.
Phase 3 (`docs/phase3/`) freezes corpus v1 before calibration tuning.
Phase 4 (`docs/phase4/`) proves reweighting and generator-parameter search on
calibration targets without fitting holdout.
Phase 5 (`docs/phase5/`) packages reference + alternative worlds and freezes
evaluation gates without retuning against holdout.
`TabDatSynthAdapter` / horizontal re-keying remain structural fixtures only.
Next: Phase 6 independent held-out / research-utility evaluation, with Phase 7A
correctness hardening gating renewed convergence and calibrated-release claims.
The audit identified full-sweep IPF convergence, missing-target success,
fit/report population alignment and repeated holdout evaluation gaps. Existing
reports remain historical artifacts, not validation of those fixes. The current
generator does not encode joint age/sex/diabetes/HF effects, adjusted analysis,
or a general parent-to-child calibrated model state.
Prefer narrow modules and transparent conditional models; no large hierarchical
framework or opaque network is required by this design.

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
  `HorizontalExpander` (deterministic re-keying) for structural/fixture scaling;
  `generate_diabetes_ip_world` (`synthesis.py`) for Phase 1 conditional
  known-truth worlds (diabetes prevalence and O1 conditionals).
- **Evidence IR & estimand compiler** — `evidence_ir.py` FindingIR v0.1,
  vocabulary, load/validate, compile (eligibility/derivation/estimator +
  compatibility), execute comparison reports; optional sex-stratum filters;
  packaged fixtures under `medicare_synth/fixtures/evidence_ir/`. Distinct from
  RKB snapshot contracts in `evidence.py`.
- **Evidence corpus registry** — `evidence_corpus.py` frozen
  `mvp-2021-om-ffs-diabetes-ip-corpus-v1` with SHA-256 checksums, partition
  execute helpers, and mutation refusal when frozen; fixtures under
  `medicare_synth/fixtures/evidence_corpus/`.
- **Calibration engine** — `calibration.py` Level A baseline, Level B IPF
  reweighting (ESS/weight/infeasibility), Level C generator-parameter grid;
  discrepancy moments evaluate on each finding's Evidence IR eligible cohort,
  but IPF fitting still uses the full beneficiary frame; holdout fit refused
  (Level C nevertheless computes holdout per candidate); `CalibrationRunManifest`;
  `AGENT_ROLE_CONTRACTS` for review gates (engines agent-independent).
- **Worlds** — `worlds.py` versioned MVP family presets, emit API, identical
  downstream `analyze_world_moments`, release manifests/limitations;
  configs under `configs/worlds/`.
- **Evaluation freeze** — `evaluation.py` hard structural + holdout isolation
  gates, graded calibration MAE, reporting-only holdout MAE; immutable freeze
  before further fitting.
- **Scenario catalog, schema diff, limitations profile, audit** — teaching/CI
  fixtures, annual snapshot diffs, six-category limitation disclosures,
  join/privacy metrics.
- **Interfaces** — Python API and `medicare-synth` CLI emitting versioned
  tables, manifests, and reports.

### Planned

Responsibility sketch only; package layout may differ:

| Boundary | Role |
| --- | --- |
| **Correctness hardening (7A)** | Full-sweep residuals, approved-target coverage, fit/report cohort alignment, weights-only semantics and post-selection evaluation |
| **Analysis compiler (7B)** | Executable effect/covariate/design contracts, supported estimator dispatch, compatibility/refusal; adjusted logistic MVP |
| **Joint synthesis (7C)** | Transparent age/sex/diabetes/HF/IP conditionals, comorbidity and supported interactions |
| **Evidence registry + model state (7D)** | Versioned evidence relationships, immutable parent/child models, warm starts, preservation/conflict/regression reports |
| **Base/world/materialization (7E)** | Pinned shared base, cohort-conditioned/local/scenario derivatives, reproducible dataset sampling and lineage |
| **Scaling (7F)** | Additional estimators, longitudinal contexts and sample sizes only behind independent evaluation gates |
| **Evaluation (Phase 6)** | Independent held-out claims, synthetic known-truth, research-workflow utility, go/no-go |
| **Agent harness** | Contracts delivered in Phase 4; orchestration remains optional around engines |
| **Release/provenance** | Public calibrated release packaging still human-gated |

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

### Evidence IR path (implemented v0.1)

```text
Reviewed finding JSON
        → parse / validate FindingIR
        → compile → eligibility + derivation + estimator + compatibility
        → execute on synthetic tables → ComparisonReport
```

### Calibration path (implemented A/B/C)

```text
Frozen corpus (calibration partition)
        → Level A discrepancy baseline
        → Level B reweight (weights only) and/or
          Level C generator-parameter search
        → CalibrationRunManifest + diagnostics
        → holdout evaluated, never fit
```

Beneficiary histories stay coherent subgraphs. Level B does not mutate
records; Level C regenerates whole worlds under pinned seeds. Neither path may
use holdout findings as fit targets.

### Target population-model path (planned, not implemented)

```text
Reviewed evidence registry (immutable versions + relationships)
        → Evidence IR + executable analysis compiler
        → compatibility / conflict / transport approval
        → new frozen corpus + pinned parent model
        → joint generation + literature-analysis execution
        → continual calibration + all-prior-target regression checks
        → immutable child base-model candidate (not yet a public release)
              ├─ general-population materialization
              ├─ cohort-conditioned world → materialization
              ├─ locally calibrated child world → materialization
              └─ scenario / alternative world → materialization
        → post-selection independent evaluation + workflow/sensitivity reports
        → human promotion gate → approved model/world/dataset releases
```

This path extends rather than replaces the structural validators, Evidence IR,
frozen corpus machinery, calibration ladder and MVP worlds. Package names and
storage layout remain implementation choices, not APIs promised by this diagram.

#### Ownership and version boundaries

- **Evidence registry:** retain source anchors, extraction/review versions,
  executable analysis definitions, uncertainty and dependence metadata. Record
  compatible/overlapping/transport-dependent/contradictory/superseded links;
  review determines base vs local applicability or alternative-world routing.
  New evidence never mutates an already frozen corpus.
- **Analysis compiler/executor:** owns eligibility, denominator, variables and
  timing, scale, covariate coding/reference levels/interactions/transformations,
  estimator dispatch, design requirements (sampling, weighting, matching,
  censoring), and exact/approximate/non-executable compatibility. The fitting
  and reporting paths must use the same semantics. A stored estimator name is
  not sufficient; unsupported analyses are refused explicitly.
- **Joint generator:** owns interpretable conditional relationships and coherent
  beneficiary/claim subgraphs. It must express a relationship before calibration
  can learn it. A fitted literature effect is not a generator parameter.
- **Population-model state:** owns model ID/version/parent, structure/parameters,
  cohort definitions, source/compiler/generator versions, corpus checksums and
  roles, seeds, objective configuration, calibration history and evaluation.
  Versions are immutable; rejected children do not overwrite parent releases.
- **Continual calibrator:** warm-starts a child; executes declared analyses on
  simulations (indirect inference / simulation-based minimum distance); compares
  their estimates with evidence; reevaluates every prior active target. The
  objective separates evidence discrepancy, preservation and structural terms.
  Uncertainty and source dependence require an explicit policy; hard structural
  invariants are not negotiable penalties. Coverage failures, conflict and
  unapproved regression block success; justified supersession is recorded.
- **World derivation:** cohort conditioning introduces no new constraints; local
  calibration adds reviewed purpose-specific evidence to a pinned base; scenario
  worlds expose weak assumptions. Each child owns its deltas and cannot mutate
  the base or siblings. Current fixed presets are not yet this general layer.
- **Materialization/export:** pins model/world, population, size, seed and export
  version. Level B artifacts must retain weights and weighted-analysis semantics;
  any unweighted resampling needs separate validation/provenance. Larger samples
  reduce Monte Carlo noise, not uncertainty about unidentified relationships.
- **Evaluation/promotion:** freeze selection before holdout measurement, disclose
  prior exposure, and require human approval of new holdouts or released models.
  Report target coverage, per-target residual/drift and uncertainty, structural
  gates and workflow utility, not only aggregate MAE.

See `ROADMAP.md` 7A–7F for ordering and exit gates; `SPEC.md` defines intended
contracts. No schema, compiler, optimizer, model-state store or public API is
changed by this documentation adoption.

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
- A shared reference model is not a unique or representative real Medicare
  joint distribution. Multiple compatible worlds and sensitivity analyses remain
  necessary; additional literature need not monotonically improve realism.
- Model updates preserve parent artifacts and disclose justified target drift;
  local-world calibration cannot silently update the common base.
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
