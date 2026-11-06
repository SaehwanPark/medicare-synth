# ROADMAP

Canonical milestones, ordering, outputs, and exit criteria.

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
  (LIT-02 planned-admission; MMD condition-hosp; CMS-AGG-05 HF algorithm shift)

Exit criteria:

- active findings are executable or transparently approximated — **met**
- partitions are frozen and reviewer-approved before calibration tuning — **met**
  (`frozen=true`, reviewer `phase3-corpus-freeze`)

### Phase 4 — Calibration engine and agent harness

Status: Active

Outputs:

- reweighting + generator-parameter calibration APIs with diagnostics
- synthetic known-truth calibration experiments
- agent role contracts and review gates; deterministic run manifests

Exit criteria:

- controlled simulations improve predeclared targets without invalidating records
- pipeline runs fully without agents; dependence/uncertainty assumptions visible

### Phase 5 — MVP calibration

Status: Planned

Outputs:

- reference world plus a few controlled alternative worlds
- training fit / discrepancy reports, manifests, limitations, examples

Exit criteria:

- hard structural gates pass; no known degenerate statistical behavior
- meaningful improvement on predeclared contextual metrics
- underidentified dimensions documented honestly

### Phase 6 — Independent evaluation

Status: Planned

Outputs:

- held-out evaluation protocol and report
- research-workflow and synthetic-truth benchmarks
- go / no-go release decision and issue backlog

Exit criteria:

- predefined thresholds met, or limitations + no-go recorded
- no indefinite retuning against the same holdout set

### Phase 7 — Expand contexts

Status: Planned

Outputs:

- additional estimands/domains/years as separate compatible contexts
- regression of earlier worlds; versioned calibration profiles

Exit criteria:

- new contexts pass the same gates; prior releases remain reproducible

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
6. Implement reweighting before advanced calibration.
7. Produce 2–3 worlds with shared targets and different weak assumptions.
8. Freeze evaluation gates before iterative fitting.
