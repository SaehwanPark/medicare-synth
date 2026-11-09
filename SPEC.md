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
- Adopted the [November 8 realignment audit](docs/audits/audit-for-project-realignement-20261108.md)
  as strategic planning input (2026-11-08). The shared population-model direction
  below supersedes conflicting older proposal language; no code, evidence
  partitions, stored results, or validation status changed in this adoption.

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

### Literature-constrained population modeling and research playground

Status: Phases 0–5 historically delivered; Phase 6 independent evaluation active.
Phase 7 population-model transition is planned, not available functionality.

**Mission and intended direction:** Medicare-Synth is developing a
literature-constrained synthetic population modeling system that incrementally
calibrates a shared Medicare-like generative model against reviewed aggregate
and inferential findings. It is intended to support reproducible general-purpose
datasets and specialized research worlds for developing, validating, and
stress-testing study designs before restricted-data access. Current delivery is
the bounded evidence-calibrated MVP below, **not** that full future system.

Published CMS aggregates and Medicare-only findings are **contextual
constraints**, not a license to reconstruct beneficiaries or publish synthetic
estimates as Medicare findings. A shared reference model does not imply a unique,
identified real joint distribution, universal coverage, or representativeness.

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
[`docs/phase2/`](docs/phase2/). Draft extraction never auto-accepts. v0.1 supports
prevalence, binary risk and rate; nonempty adjustment sets are rejected. Stored
estimator labels do not yet provide general executable analysis dispatch.

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

### Audit constraints on current claims

The November 8 audit is static evidence, not a new test run. Phase 4/5 delivery
history remains intact, but stored `converged` flags and MAE improvement do not
resolve the following correctness and interpretation gaps:

- IPF checks residuals immediately after each rake, not all targets after a
  complete sweep. Final-weight residuals must govern convergence (planned 7A).
- Missing/unsupported targets are counted but omitted from computable-only MAE;
  approved-target coverage must gate success, not just the aggregate metric.
- Discrepancy reporting already uses Evidence IR eligibility; IPF still rakes
  the full beneficiary frame. Fit/report population alignment is incomplete.
- Level B leaves records unchanged: calibrated use requires weights and weighted
  analyses; it is not an ordinary unweighted calibrated dataset.
- Level C excludes holdout from its selection objective but computes it per
  candidate. Defer evaluation until candidate selection is frozen and disclose
  earlier exposure before asserting independent evaluation.
- Current HF generation is independent of diabetes, and age/sex do not drive
  clinical outcomes. General adjusted relationships and parent-model updates
  are not implemented.

These gaps gate renewed fidelity/convergence claims and any affirmative Phase 6
calibrated-release decision; fixes and corrected reports need a separate code
slice. No historical report or frozen corpus is silently repaired here.

**Non-goals (program-wide):** recover individuals or the full real joint;
treat literature match or increased literature volume as representativeness or
guaranteed convergence to Medicare truth; autonomous adoption of extracted
facts; MA/FFS or year/algorithm silent conflation; a uniquely correct universal
Medicare distribution. A versioned shared reference model **is** an intended
asset, alongside multiple plausible worlds for underidentified relationships.

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
7. Population-model transition, ordered **7A → 7B → 7C → 7D → 7E → 7F**:
   correctness hardening (alongside Phase 6, gating affirmative release claims);
   inferential IR; richer joint synthesizer; versioned continual calibration;
   shared base/derived worlds; scaling and context-specific evaluation.

### Planned population-model contracts (not implemented)

- **Model, dataset and world are distinct:** immutable base-model state owns
  parameters/relationships, cohort definitions, evidence versions, calibration
  history and evaluation. A materialized dataset pins model, population, sample
  size, seed and export version. A purpose-specific world pins a parent base and
  declares cohort conditioning, local calibration or scenario assumptions; local
  updates cannot change the base or sibling worlds.
- **Executable inferential evidence:** record eligibility, exposure/outcome and
  timing, effect scale, covariate coding/interactions/transformations, estimator,
  study design, uncertainty/dependence, compatibility and source anchors. Dispatch
  the declared supported estimator or refuse it; marginal vs conditional effects
  and different adjustment sets are not interchangeable. Roadmap order: crude
  RR/RD/OR → adjusted logistic → Poisson/rates → survival/Cox → complex designs.
- **Indirect inference:** apply the literature's executable analysis to generated
  data and compare its fitted effect with the reported estimate. A literature
  adjusted OR is not a generator coefficient. Compatibility may be exact,
  transparently approximate, or non-executable; unsupported targets cannot be
  optimized away or silently omitted.
- **Richer joint support:** begin with interpretable age/sex/diabetes/HF/IP
  conditional relationships, comorbidity and supported interactions, retaining
  structural/temporal hard gates and deterministic materialization.
- **Continual calibration:** preserve parent corpus/model versions, warm-start a
  child on a newly reviewed frozen corpus, and reevaluate every prior active
  constraint. Evidence discrepancy, preservation and structural terms are
  declared before fit; account for uncertainty and source dependence without
  pretending overlapping studies are independent. Structural invariants remain
  hard constraints where appropriate.
- **Evidence reconciliation:** classify compatible, overlapping,
  transport-dependent, contradictory and superseded findings before deciding
  whether they constrain the base, a local context or an alternative world.
  Human-approved revisions may supersede old constraints; unexplained regression
  blocks promotion. More literature need not improve realism.
- **Reproducibility and evaluation:** pin lineage, parameters/structure,
  source/compiler/generator versions, evidence roles/checksums, seeds, objective,
  diagnostics and before/after per-target results. Evaluate only after selection;
  independently assess each context and preserve multi-world sensitivity.

**First feasibility gate (7B–7C, after 7A):** retain the pinned 2021 FFS context;
reevaluate existing prevalence/IP-risk targets while adding diabetes–HF and
age/sex relationships plus one reviewed real-literature adjusted logistic OR.
Use new evidence versions, predeclared tolerances, explicit target coverage,
known-truth controls and structural gates. Stop if source semantics or model
capacity cannot support the analysis; the audit's example numbers are not
approved evidence. This experiment precedes bulk literature expansion. See
`ROADMAP.md` for outputs, failure cases and later parent-to-child update gates.

Open product decisions (do not invent silently): keep FFS Option B vs upgrade
to monthly Option C; whether to collapse `sp_*` codes `1`/`2`; person-time vs
full-year denominators for rate targets; whether to replace LIT-07 industry
utilization prior with an official O1-compatible aggregate in a **new** corpus
version; HF co-calibration weight vs prevalence-only; the first compatible adjusted-OR source and its coding/design contract;
objective/uncertainty/dependence policy and preservation tolerances; transport
rules for older-year studies; workflow-utility benchmark. The staged inferential
scope above is adopted, but individual estimands and implementation choices
still require review. Corpus v1 training targets and women-stratum
holdout are frozen in `docs/phase3/` — do not silently retarget holdout.
