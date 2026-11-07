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

Status: Active — Phases 0–5 complete; Phase 6 (independent evaluation) next

**Mission:** generate structurally valid, contextually plausible synthetic
Medicare worlds so researchers can prototype and stress-test methods before
restricted-data access. Published CMS aggregates and Medicare-only study
findings are **contextual constraints**, not a license to reconstruct real
beneficiaries or publish synthetic estimates as Medicare findings.

**MVP research context (pinned in Phase 0):**
`mvp-2021-om-ffs-diabetes-ip` — 2021 Original Medicare FFS, age 65+, full-year
Parts A/B with annual HMO/MA months = 0 (**FFS Option B** default; monthly
HMO panel / Option C is the fidelity upgrade), diabetes via `sp_diabetes` →
all-cause inpatient hospitalization; heart failure (`sp_chf`) as stratifier.
Detail: [`docs/phase0/`](docs/phase0/).

**Synthesizer (Phase 1):** `medicare_synth.synthesis.generate_diabetes_ip_world`
emits coherent MVP subgraphs with controllable diabetes prevalence and
`P(O1|diabetes)` / `P(O1|no diabetes)` under pinned seeds; structural
validators pass; held-out synthetic relationships recover within tolerance;
clone-only horizontal expansion is characterized as insufficient statistical
support. See [`docs/phase1/`](docs/phase1/). TabDat / horizontal expanders
remain structural tools only.

**Evidence IR (Phase 2):** `medicare_synth.evidence_ir` provides schema
`0.1` finding objects, vocabulary, parse/validate, compile (eligibility /
derivation / estimator + compatibility), and execute (reproducible comparison
reports). LIT-03 (Andes MMWR 2015 diabetes prevalence 31.6%) is formalized as a
reviewed **diagnostic** finding with explicit transport gaps; LIT-02-shaped
planned-admission rates are refused rather than silently approximated. See
[`docs/phase2/`](docs/phase2/). Draft extraction never auto-accepts.

**Evidence corpus (Phase 3):** `medicare_synth.evidence_corpus` freezes
`mvp-2021-om-ffs-diabetes-ip-corpus-v1` with checksummed calibration (3),
holdout (1; women diabetes prevalence stratum), diagnostic, and excluded
partitions. Active findings are executable or transparently approximated;
frozen corpora refuse mutation. See [`docs/phase3/`](docs/phase3/).

**Calibration (Phase 4):** `medicare_synth.calibration` provides Level A
baseline discrepancy, Level B beneficiary IPF reweighting (ESS/weight/
infeasibility diagnostics; records unchanged), and Level C generator-parameter
search against the **calibration** partition only. Holdout is evaluate-only.
Deterministic `CalibrationRunManifest` and typed `AGENT_ROLE_CONTRACTS` encode
review gates; engines run without agents. See [`docs/phase4/`](docs/phase4/).

**MVP calibrated worlds (Phase 5):** `medicare_synth.worlds` emits family
`mvp-2021-om-ffs-diabetes-ip-worlds-v1` (reweight reference, generator
reference, alternate free `P(IP|no diabetes)`) against shared frozen
calibration targets. `medicare_synth.evaluation` freezes hard structural /
holdout-isolation gates and graded metrics before further fitting. Identical
`analyze_world_moments` analysis runs in each world. See
[`docs/phase5/`](docs/phase5/).

**Near-term capability targets:**

| Capability | Intent |
| --- | --- |
| Evidence IR | **Delivered (v0.1)** — typed findings with population/time/eligibility/estimand/uncertainty/role/governance |
| Estimand compiler | **Delivered (v0.1 crude)** — eligibility → derivation → estimator → compatibility → comparison |
| Evidence corpus | **Delivered (v1 freeze)** — train/holdout/diagnostic/excluded registry with checksums |
| Calibration ladder | **Delivered A–C** — baseline / reweight / generator-param search; hierarchical methods still later |
| Multi-world releases | **Delivered (v1 family)** — shared targets; documented weak-assumption variation |
| Evaluation | **Freeze delivered (Phase 5)** — hard gates + graded metrics; Phase 6 owns independent claims |
| Agent assist | Discovery/extraction/formalization help with human approval gates; engines run without agents |

**Non-goals (program-wide):** recover individuals or the full real joint;
treat literature match as representativeness; autonomous adoption of extracted
facts; MA/FFS silent conflation; one universal synthetic Medicare distribution.

Verification rule unchanged: every decision cites evidence, states assumptions,
and is reflected in `ARCHITECTURE.md` and `ROADMAP.md`. No synthesis or release
may claim calibrated fidelity before applicable constraints and tests exist.

## Future

Ordered program (see `ROADMAP.md` for exit gates):

0. ~~Feasibility memo, MVP context, initial evidence inventory.~~ **Complete**
   (`docs/phase0/`).
1. ~~Verified synthesizer with genuine conditional support and known-truth
   tests.~~ **Complete** (`docs/phase1/`, `medicare_synth.synthesis`).
2. ~~Evidence IR + executable estimand language.~~ **Complete**
   (`docs/phase2/`, `medicare_synth.evidence_ir`).
3. ~~Frozen, reviewed MVP evidence corpus (train / holdout / diagnostic).~~
   **Complete** (`docs/phase3/`, `medicare_synth.evidence_corpus`).
4. ~~Calibration engine + reviewable agent orchestration (engines independent of
   agents).~~ **Complete** (`docs/phase4/`, `medicare_synth.calibration`).
5. ~~Calibrated MVP worlds and release manifests.~~ **Complete**
   (`docs/phase5/`, `medicare_synth.worlds`, `medicare_synth.evaluation`).
6. Held-out and research-utility evaluation; go/no-go.
7. Incremental context and literature expansion with regression of prior worlds.

Open product decisions (do not invent silently): keep FFS Option B vs upgrade
to monthly Option C; whether to collapse `sp_*` codes `1`/`2`; person-time vs
full-year denominators for rate targets; whether to replace LIT-07 industry
utilization prior with an official O1-compatible aggregate in a **new** corpus
version; HF co-calibration weight vs prevalence-only; Evidence IR estimand
breadth beyond v0.1 crude; transport rules for older-year studies;
workflow-utility benchmark. Corpus v1 training targets and women-stratum
holdout are frozen in `docs/phase3/` — do not silently retarget holdout.
