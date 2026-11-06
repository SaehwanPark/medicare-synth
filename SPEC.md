# SPEC

## Past

- Defined Medicare-Synth as a provenance-backed compiler for contemporary
  Medicare synthetic datasets and research fixtures, with official CMS synthetic
  claims as the empirical baseline and structural validity as the first quality
  bar.
- Completed the validation-first foundation: pinned CMS 2021 baseline and RKB
  evidence snapshots; Pydantic v2 + Polars/PyArrow contracts; relational,
  temporal, administrative, and accounting validators; deterministic scenarios;
  release export; vertical/horizontal expansion; scenario catalog; schema diff;
  limitations/audit profiles; bounded 2022 PUF beneficiary/carrier path; and a
  newcomer docs portal. Detail lives in `CHANGELOG.md`.
- Adopted the
  [evidence-calibrated research playground proposal](docs/medicare_synth_evidence_calibrated_playground_proposal.md)
  as the next program direction (2026-11-06).

## Present

### Structural foundation

Status: Complete

Active contracts agents and contributors must respect:

- **Baseline:** CMS 2021 Synthetic Claims (`CMS-2021-SYN-CLAIMS`), schema year
  2021; additive 2022 PUF path limited to beneficiary + carrier.
- **Provenance statuses:** preserved, normalized, re-keyed, derived, imputed,
  synthesized, externally calibrated, scenario-generated.
- **Evidence snapshots:** immutable RKB JSON under `data/rkb_snapshots/`.
- **Validation:** field/record (Pydantic), relational/temporal/administrative/
  accounting (Polars); findings never silently repair baseline anomalies.
- **Determinism:** pinned manifests and seeds reproduce releases; no hidden
  wall-clock or environment state in the functional core.
- **Licensing:** Apache-2.0 code; CMS synthetic data acquired via checksummed
  manifests into ignored `data/`, not stored in git.

Out of scope for the foundation (still true):

- historical CCW layouts before 2021 as a supported default
- claims of population representativeness or clinical validity
- opaque generative models where transparent methods suffice
- production-scale cohorts outside validation-first constraints

### Evidence-calibrated research playground

Status: Active — Phase 0 (feasibility and evidence scouting)

**Mission:** generate structurally valid, contextually plausible synthetic
Medicare worlds so researchers can prototype and stress-test methods before
restricted-data access. Published CMS aggregates and Medicare-only study
findings are **contextual constraints**, not a license to reconstruct real
beneficiaries or publish synthetic estimates as Medicare findings.

**MVP research context (proposed):** 2021 Original Medicare FFS, age 65+,
explicit Parts A/B enrollment and managed-care handling, chronic
disease → hospitalization (diabetes and/or heart failure as candidate
condition families). Exact cohort, algorithms, and table subset are Phase 0
decisions.

**Near-term capability targets:**

| Capability | Intent |
| --- | --- |
| Evidence IR | Typed, reviewed finding objects: population, time, eligibility, variables, estimand, uncertainty, role, governance |
| Estimand compiler | Eligibility → derivation → estimator → compatibility report → comparison |
| Synthesis contract | Coherent beneficiary subgraphs with controllable conditional relationships (beyond index/seed fixtures) |
| Calibration ladder | A none → B reweight → C conditional generation; prove A–C before hierarchical methods |
| Multi-world releases | Shared evidence constraints; documented variation in underidentified dimensions |
| Evaluation | Hard structural gates + graded evidence agreement + held-out + research-utility benchmarks |
| Agent assist | Discovery/extraction/formalization help with human approval gates; engines run without agents |

**Non-goals (program-wide):** recover individuals or the full real joint;
treat literature match as representativeness; autonomous adoption of extracted
facts; MA/FFS silent conflation; one universal synthetic Medicare distribution.

Verification rule unchanged: every decision cites evidence, states assumptions,
and is reflected in `ARCHITECTURE.md` and `ROADMAP.md`. No synthesis or release
may claim calibrated fidelity before applicable constraints and tests exist.

## Future

Ordered program (see `ROADMAP.md` for exit gates):

0. Feasibility memo, MVP context, initial evidence inventory.
1. Verified synthesizer with genuine conditional support and known-truth tests.
2. Evidence IR + executable estimand language.
3. Frozen, reviewed MVP evidence corpus (train / holdout / diagnostic).
4. Calibration engine + reviewable agent orchestration (engines independent of agents).
5. Calibrated MVP worlds and release manifests.
6. Held-out and research-utility evaluation; go/no-go.
7. Incremental context and literature expansion with regression of prior worlds.

Open product decisions (do not invent silently): exact 2021 FFS cohort rules;
minimal table/algorithm set; primary outcome family; Evidence IR v0.1 estimand
breadth; transport rules for older-year studies; workflow-utility benchmark.
