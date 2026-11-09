# ROADMAP

Canonical milestones, ordering, outputs, and exit criteria.

## Strategic realignment — 2026-11-08

Adopt the [November 8 audit](docs/audits/audit-for-project-realignement-20261108.md)
as planning input: evolve toward a **literature-constrained, continually
calibrated shared Medicare-like population model**. Versioned model state is
the central asset; datasets are reproducible materializations, and specialized
worlds are explicit derivatives. A shared reference is not a uniquely identified
or universally representative Medicare distribution.

This is a documentation-only adoption, not implementation or fresh validation.
Phases 0–5 remain historical deliveries. Phase 6 independent evaluation remains
active, with correctness hardening required before renewed convergence or
release-fidelity claims. Static audit findings are tracked below; stored reports
and frozen corpus v1 are not rewritten. Current canonical documents supersede
the older proposal wherever strategy or ordering differs.

- Strategic design for the next program:
  [`docs/medicare_synth_evidence_calibrated_playground_proposal.md`](docs/medicare_synth_evidence_calibrated_playground_proposal.md)
- Earlier product motivation:
  [`docs/medicare-synth-project-proposal_20260720.md`](docs/medicare-synth-project-proposal_20260720.md)
- Agent goal prompt: [`docs/goal.md`](docs/goal.md)

## Completed foundation (milestones 0–13)

Status: Complete

Delivered: repository harness and bookkeeping; pinned CMS 2021 baseline and RKB
snapshots; Pydantic/Polars validation stack; scenarios, normalizer, release
export; vertical/horizontal expansion; catalog/diff/profile/audit; Part D and
institutional claim families plus MBSF segments with field validators; bounded
2022 PUF beneficiary/carrier slice; claim-line and enrollment indicator
expansions; newcomer docs portal and GitHub Pages.

Those remain the structural substrate. They do **not** imply that the current
generator has learned realistic conditional distributions or that every listed
table is ready for a calibrated longitudinal research context.

## Evidence-calibrated playground

### Phase 0 — Feasibility and evidence scouting

Status: Complete (2026-11-06)

Outputs (under [`docs/phase0/`](docs/phase0/)):

- generator/capability gap notes for the MVP context
  ([capability-gaps.md](docs/phase0/capability-gaps.md))
- pinned 2021 Original Medicare FFS cohort and required fields
  ([mvp-cohort-and-fields.md](docs/phase0/mvp-cohort-and-fields.md))
- initial inventory of CMS aggregates and Medicare-only findings
  ([evidence-inventory.md](docs/phase0/evidence-inventory.md))
- feasibility memo and draft MVP specification
  ([feasibility-memo.md](docs/phase0/feasibility-memo.md),
  [draft-mvp-specification.md](docs/phase0/draft-mvp-specification.md))

Pinned MVP context: `mvp-2021-om-ffs-diabetes-ip` — 2021 Original Medicare
FFS, age 65+, diabetes (`sp_diabetes`) → all-cause inpatient hospitalization,
HF (`sp_chf`) as stratifier. Decision: **proceed** to Phase 1.

Exit criteria:

- at least one population/condition/utilization analysis is expressible with
  available or reasonably implementable fields — **met**
- no known fatal comparability issue is ignored — **met** (CCW 27→30, year
  transport, MA exclusion options, all-cause vs DX-specific admissions, and
  overlapping CCW sources documented)

### Phase 1 — Establish and verify the synthesizer

Status: Complete (2026-11-06)

Outputs:

- synthesizer contract with independently testable conditional generation
  ([synthesizer-contract.md](docs/phase1/synthesizer-contract.md);
  `medicare_synth.synthesis`)
- baseline benchmark suite and known-truth reference worlds
  (`tests/test_synthesis.py`; `generate_diabetes_ip_world`)
- generator capability report and limitations
  ([capability-report.md](docs/phase1/capability-report.md))

Exit criteria:

- pinned inputs/seeds reproduce outputs; structural checks pass — **met**
- held-out synthetic ground-truth relationships recover within declared
  tolerances — **met** (R3 on holdout; `max(0.03, 3.5·SE)`; multi-seed at n≥8000)
- generated data show genuine statistical support (not clone-only variation)
  — **met** (clone-only cannot retarget prevalence; conditional synthesizer can)

### Phase 2 — Evidence IR and executable study language

Status: Complete (2026-11-06)

Outputs:

- Evidence IR schema/versioning; vocabulary for concepts and estimands
  ([evidence-ir-schema.md](docs/phase2/evidence-ir-schema.md);
  `medicare_synth.evidence_ir`, `schema_version: "0.1"`)
- parser/validator/compiler with compatibility reports
- source-to-estimand tests and sample fixtures
  ([fixtures/](docs/phase2/fixtures/); `tests/test_evidence_ir.py`)
- optional draft extraction with source anchors (review required;
  `draft_finding_from_fields`)
- end-to-end LIT-03 formalization
  ([lit03-formalization.md](docs/phase2/lit03-formalization.md);
  [capability-report.md](docs/phase2/capability-report.md))

Exit criteria:

- a human-reviewed real Medicare-only finding formalizes, executes against a
  compatible synthetic dataset, and compares reproducibly; errors are explicit
  — **met** (LIT-03 Andes MMWR 2015 diabetes prevalence 31.6%; diagnostic role;
  explicit year/age/FFS/algorithm gaps; LIT-02 planned-admission refusal)

### Phase 3 — Curate and freeze the MVP evidence corpus

Status: Complete (2026-11-06)

Outputs:

- versioned evidence registry with eligibility/compatibility grades
  (`medicare_synth.evidence_corpus`;
  [corpus-freeze.md](docs/phase3/corpus-freeze.md))
- train / held-out / diagnostic partitions and checksums
  (`mvp-2021-om-ffs-diabetes-ip-corpus-v1`; 3 calibration + 1 holdout)
- exclusion/conflict rationales retained (not deleted)
  (excluded: LIT-02, MMD condition-hosp; diagnostic: CMS-AGG-05 HF algorithm shift)

Exit criteria:

- active findings are executable or transparently approximated — **met**
- partitions are frozen and reviewer-approved before calibration tuning — **met**
  (`frozen=true`, reviewer `phase3-corpus-freeze`)

### Phase 4 — Calibration engine and agent harness

Status: Complete (2026-11-06)

Outputs:

- reweighting + generator-parameter calibration APIs with diagnostics
  (`medicare_synth.calibration`;
  [calibration-engine.md](docs/phase4/calibration-engine.md))
- synthetic known-truth calibration experiments
  ([capability-report.md](docs/phase4/capability-report.md);
  `reports/phase4/known_truth_experiment.json`)
- agent role contracts and review gates; deterministic run manifests
  ([agent-roles.md](docs/phase4/agent-roles.md); `CalibrationRunManifest`)

Exit criteria:

- controlled simulations improve predeclared targets without invalidating
  records — **met** (Level B weights-only IPF; Level C param search;
  structural gates pass)
- pipeline runs fully without agents; dependence/uncertainty assumptions
  visible — **met**

### Phase 5 — MVP calibration

Status: Complete — see `docs/phase5/`

Outputs:

- reference world plus controlled alternative worlds — **met**
  (`mvp-2021-om-ffs-diabetes-ip-worlds-v1`: reweight + generator +
  alternate free background IP)
- training fit / discrepancy reports, manifests, limitations, examples —
  **met** (`reports/phase5/`, `configs/worlds/`)
- evaluation freeze (hard gates + graded metrics; holdout evaluate-only) —
  **met** (`medicare_synth.evaluation`)

Exit criteria:

- hard structural gates pass; no known degenerate statistical behavior —
  **met**
- meaningful improvement on predeclared contextual metrics — **met**
  (calibration MAE improved on all three worlds)
- underidentified dimensions documented honestly — **met**

### Phase 6 — Independent evaluation

Status: Active

Outputs:

- held-out evaluation protocol and report
- research-workflow and synthetic-truth benchmarks
- go / no-go release decision and issue backlog, including audit caveats

Exit criteria:

- predefined thresholds met, or limitations + no-go recorded
- no indefinite retuning against the same holdout set
- Phase 7A correctness findings resolved before affirmative convergence or
  calibrated-release claims; evaluate historical artifacts as historical, and
  identify any corrected rerun separately rather than overwriting them
- held-out measurements already exposed during candidate search are disclosed;
  any fresh independent evaluation evidence or partition change requires human
  approval, not relabeling the existing holdout as untouched

### Phase 7 — Population-model transition

Status: Planned — replaces generic context/literature expansion

Order: **A → B → C → D → E → F**. A can proceed alongside Phase 6 protocol
work; it gates affirmative Phase 6 release claims. B and C culminate in the
bounded joint + inferential MVP below. Do not collect a large literature corpus
or promise a large calibrated download before that feasibility gate. D proves
version-to-version updating; E generalizes derived worlds; F expands only after
the earlier gates pass. Each stage requires a separately scoped implementation
and human approval of evidence/estimands; this roadmap authorizes no code now.

#### 7A — Correctness hardening

Likely boundaries: `calibration.py`, Evidence IR eligibility, evaluation and
world manifests; existing `tests/test_calibration.py` / evaluation tests.

Required outputs and acceptance:

- **Full-sweep IPF convergence:** after each complete sweep, reevaluate every
  approved target on the final weights; report convergence only when all
  residuals satisfy the declared tolerance. Include coupled constraints where a
  later rake disturbs an earlier one, iteration exhaustion, and infeasibility.
- **No silent missing-target success:** unsupported/undefined approved targets,
  empty eligible cohorts, or absent support produce explicit failure or unmet
  status. A lower MAE on only the computable subset is not success; report target
  coverage and per-target status alongside any aggregate score.
- **Population alignment:** use each finding's executable eligibility and
  denominator consistently in fitting, convergence, and reporting. Discrepancy
  reporting already filters eligible cohorts; full-frame IPF is still a gap.
  Verify restricted age/enrollment/sex cohorts and conditional denominators.
- **Weighted artifact semantics:** Level B remains records + beneficiary weights
  with ESS/weight diagnostics and weighted-analysis requirements. Do not label
  unchanged tables as an ordinary calibrated sample. Any later resampling is a
  separate, validated materialization with its own provenance.
- **Holdout isolation:** remove candidate-by-candidate holdout evaluation; freeze
  candidate selection on calibration evidence before reporting approved
  evaluation results. Record prior exposure and forbid tuning from those results.
- Preserve historical reports; issue versioned corrected runs with explicit
  differences. Structural, determinism, and corpus-mutation gates still apply.

Exit: all approved constraints are accounted for, no failure is hidden by a
summary metric, and convergence agrees with final per-target residuals.

#### 7B — Inferential Evidence IR and executable analyses

Extend `evidence_ir.py` and its schema/compiler/report contracts, preserving
v0.1 fixtures or providing an explicit versioned migration. Support crude RR,
RD, and OR first, then one reviewed **adjusted logistic-regression** analysis.
The estimator field must dispatch a supported analysis or refuse it explicitly,
not merely store a label while executing a different calculation.

Executable contracts must specify population/program/year/enrollment,
eligibility, exposure/outcome algorithms and timing, follow-up, effect scale,
covariate coding/reference levels/transformations/interactions, estimator,
study-design requirements (including weights/matching/censoring where relevant),
uncertainty, provenance, and exact/approximate/non-executable compatibility.
Marginal and conditional effects and differing adjustment sets are not
interchangeable (including OR/HR noncollapsibility). Unsupported designs and
missing analysis variables must fail explicitly.

Exit: a human-reviewed real Medicare finding executes the declared analysis
reproducibly, with source anchors, compatibility gaps and uncertainty; known-truth
and failure cases cover empty strata, separation/nonconvergence, and unsupported
estimators. Literature adjusted ORs are compared with estimates fitted on
synthetic data, never assigned directly as generator coefficients.

#### 7C — Richer joint synthesizer and inferential calibration MVP

Extend the transparent MVP generator (`synthesis.py`) to represent joint
age/sex/diabetes/HF/inpatient relationships, including diabetes–HF comorbidity
and declared interactions where supported. Prefer an interpretable modular
conditional model to an opaque network. Do not invent relationships from absent
evidence or assume coefficient equality across generating and analysis models.

Exit: the bounded MVP below simultaneously evaluates marginal, conditional,
and adjusted-association targets under deterministic seeds and hard structural
gates. Capacity limits, conflicting constraints and Monte Carlo error are
reported rather than concealed by optimization.

#### 7D — Versioned continual calibration

Add a reviewed evidence-registry update path and immutable population-model
state: model ID/version, parent, parameters/structure, cohort definitions,
source/compiler/generator versions, evidence checksums/roles, seeds, objective,
calibration history and evaluation results. Preserve old corpus/model versions;
warm-start a new model from its parent against a newly frozen evidence version.

Before optimization, classify evidence relationships as compatible, overlapping,
transport-dependent, contradictory, or superseded. Human review chooses shared
constraints, context-only constraints, exclusions or alternative worlds; do not
automatically average incompatible years, populations or algorithms.

Use a declared evidence-discrepancy + preservation + structural objective:
account for uncertainty and source dependence (e.g. covariance or source
clusters), and keep structural invariants hard where appropriate. Missing
uncertainty/dependence information needs an explicit approved policy, not an
assumption of independent equally precise findings. Penalties and tolerances
are predeclared; no tuning against holdout.

Exit: adding reviewed evidence creates a reproducible child model, reevaluates
**all** prior active constraints, and records per-target drift, conflict,
supersession and justified regressions. Preservation does not mean satisfying
obsolete evidence forever; unapproved degradation blocks promotion. Parent
releases remain reproducible and a rejected child cannot mutate them.

#### 7E — Shared base and derived worlds

Separate immutable base-model releases from materialized datasets (pinned model,
population, size, seed, export version) and derivative world versions:

- **Cohort-conditioned world:** samples a declared conditional population from
  the base without introducing new evidence or silently changing parameters.
- **Locally calibrated world:** starts from a pinned base, adds approved
  purpose-specific evidence, and records local parameter/constraint deltas.
- **Scenario/alternative world:** labels weakly identified assumptions and
  sensitivity departures explicitly, rather than implying new empirical facts.

Exit: identical pins reproduce each artifact; local calibration cannot mutate
the base or sibling worlds; lineage and weighted vs unweighted semantics survive
export. Current MVP presets are retained, not relabeled as this general system.

#### 7F — Scaling and independent evaluation across contexts

Expand to Poisson/event-rate models, then survival/Cox, then matching,
propensity-score weighting and subgroup interactions only as their time,
censoring, sampling and analysis semantics become executable. Additional
conditions, years, longitudinal paths, and large materializations are separate
compatible contexts, not automatic transport of the 2021 MVP.

Exit: context-specific independent evidence and workflow benchmarks meet
predeclared gates, previous model/world versions remain reproducible, and
multi-world sensitivity and limitations accompany scaled releases. Larger
samples reduce simulation noise, not underidentification or evidence bias.

## First implementation experiment after hardening: joint + inferential MVP

Keep `mvp-2021-om-ffs-diabetes-ip` (2021 FFS, age 65+, Option B). First scope
and approve one compatible adjusted-OR source and the required variables; stop
if no source supports the declared analysis without unapproved transport or
unavailable fields. The audit's illustrative OR/HR values are **not** targets.

Required observable outcomes for 7B–7C:

1. Retain and reevaluate existing diabetes/HF prevalence and diabetes inpatient
   risk constraints from frozen corpus v1; any additions use a new reviewed
   corpus version without changing the v1 holdout.
2. Add supported diabetes–HF comorbidity and age/sex inpatient-risk relationships
   with reviewed evidence or explicitly labeled simulation assumptions.
3. Execute one real literature adjusted logistic analysis on generated data;
   calibrate its estimated OR together with the approved earlier constraints.
4. Compare before/after per-target coverage, discrepancy, structural validity,
   uncertainty/Monte Carlo variation and all previous constraints under
   predeclared tolerances; no unsupported target may disappear from success.
5. Record go/no-go, model-capacity/estimator/conflict failures and remaining free
   dimensions. This proves a bounded feasibility slice, not continual learning
   or general Medicare fidelity; parent-to-child preservation is the 7D gate.

## Near-term vertical slice (before full parallelization)

1. ~~Select one 2021 FFS 65+ chronic → hospitalization context.~~ **Done (Phase 0):**
   diabetes → all-cause IP; see `docs/phase0/`.
2. ~~Audit the minimal dependency graph of tables/fields.~~ **Done (Phase 0).**
3. ~~Prove generator controllability on synthetic ground truth.~~ **Done (Phase 1).**
4. ~~Formalize one finding end-to-end (source → IR → execution → report).~~
   **Done (Phase 2):** LIT-03 → Evidence IR → synthetic comparison; see
   `docs/phase2/`.
5. ~~Prepare ~3 public calibration targets + 1 independent diagnostic/holdout.~~
   **Done (Phase 3):** corpus v1 frozen; see `docs/phase3/`.
6. ~~Implement reweighting before advanced calibration.~~ **Done (Phase 4):**
   Level B IPF reweight + Level C generator-param search; see `docs/phase4/`.
7. ~~Produce 2–3 worlds with shared targets and different weak assumptions.~~
   **Done (Phase 5):** see `docs/phase5/`.
8. ~~Freeze evaluation gates before iterative fitting.~~ **Done (Phase 5).**
9. Independent held-out / research-utility evaluation and go/no-go (Phase 6).
