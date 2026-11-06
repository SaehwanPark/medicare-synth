# Phase 0 — Draft MVP specification

**Status:** Draft (2026-11-06) — guides Phases 1–3; not a release contract
**Authority:** Subordinate to `SPEC.md` / `ROADMAP.md` when they disagree after
sync; this document records Phase 0 choices in more detail.
**Parents:** [feasibility-memo.md](feasibility-memo.md),
[mvp-cohort-and-fields.md](mvp-cohort-and-fields.md),
[evidence-inventory.md](evidence-inventory.md)

## 1. Purpose

Specify the smallest evidence-calibrated playground MVP that can:

1. Emit structurally valid 2021 OM FFS–like beneficiary subgraphs.
2. Execute at least one reviewed external finding as a comparison report.
3. Later calibrate lightly (reweight → conditional generation) across a few
   worlds without claiming reconstruction of real Medicare beneficiaries.

## 2. Research context (pinned)

| Item | Specification |
| --- | --- |
| Name | `mvp-2021-om-ffs-diabetes-ip` |
| Year | 2021 |
| Program | Original Medicare FFS (Parts A and B); MA excluded per §3 |
| Age | ≥ 65 at end of year / death |
| Exposure | Diabetes: `sp_diabetes ∈ {1,2}` (collapse); HF stratifier `sp_chf` |
| Outcome | All-cause IP hospitalization (**O1**): ≥1 inpatient claim with admission in 2021 |
| Primary estimand (v0) | Risk or rate of O1 by diabetes status within the cohort |
| Non-goals | MA inference; DX-specific admissions; provider networks; Part D insulin strata; causal effects as Medicare findings |

## 3. Cohort rules (implementable default)

Until Phase 3 freezes alternatives:

1. `age_end_ref_yr >= 65` from `bene_birth_dt` and reference date 2021-12-31
   (or death date if earlier).
2. `bene_hi_cvrage_tot_mons == 12` and `bene_smi_cvrage_tot_mons == 12`
   (**full-year** A+B for prevalence-style denominators).
3. `bene_hmo_cvrage_tot_mons == 0` and, when available,
   `bene_ma_cvrage_tot_mons == 0` (**FFS Option A**).
4. Include decedents who meet enrollment rules until death when constructing
   person-time rates.

**Documented upgrades (not silent):** monthly HMO panel (Option C); person-time
denominators for rate estimands; distinguishing `sp_*` `1` vs `2`.

## 4. Minimal schema contract

### Required tables

`beneficiary_summary`, `mbsf_base_enrollment`, `mbsf_chronic_conditions`,
`inpatient_claims`.

### Required fields

As listed in [mvp-cohort-and-fields.md](mvp-cohort-and-fields.md) §4.1.

### First-class extensions expected in Phase 1–2 (reasonable implementability)

1. Monthly `hmo_ind_01`–`_12` (and ideally full buy-in / dual panels).
2. Inpatient principal diagnosis field(s) for later estimand classes.
3. Optional stored or derived `age_at_end_ref_yr`.
4. Synthesis interface that can set `P(O1 | diabetes, …)` without breaking keys
   or chronology.

### Explicitly out of MVP schema v0

County geography, PDE insulin, multi-year lookback claim rebuilds of CCW
algorithms, readmission episode tables.

## 5. Synthesis requirements (Phase 1 contract preview)

The synthesizer must, under pinned seeds:

1. Produce coherent beneficiary subgraphs that pass existing structural
   validators (hard gate).
2. Support controllable variation in diabetes prevalence and
   `P(O1 | diabetes)` on **synthetic known-truth** worlds.
3. Demonstrate that horizontal cloning alone is insufficient as a statistical
   sample (characterization already true; encode as benchmark).
4. Remain operable without the agent harness.

## 6. Evidence IR requirements (Phase 2 preview)

Support at least:

| Estimand type | Example |
| --- | --- |
| Prevalence | `P(diabetes = 1)` in cohort |
| Binary risk | `P(O1 = 1 \| diabetes)` |
| Rate | admissions per 100 person-years among diabetes+ |

Each IR object must carry: population, year, eligibility, variable definitions,
estimand, uncertainty (or explicit unknown), source anchors, compatibility
grade, and train/holdout/diagnostic role (assigned only after human review).

## 7. Initial evidence plan (not frozen)

See [evidence-inventory.md](evidence-inventory.md). Working intent:

- Prefer **CMS MMD 2021** age-filtered FFS extracts for prevalence and
  hospitalization marginals.
- Use **LIT-02**-class admission rates as a formalization exercise with
  explicit year-transport assumptions.
- Keep **CMS-AGG-05** as mandatory diagnostic for HF algorithm shifts.
- Freeze train/holdout only in Phase 3.

## 8. Calibration ladder (Phases 4–5 preview)

| Stage | Method | MVP expectation |
| --- | --- | --- |
| A | None (structural only) | Baseline discrepancy report |
| B | Beneficiary reweighting | Improve predeclared prevalence / risk targets; report ESS |
| C | Conditional generator parameters | Improve `P(O1 \| diabetes)` support when reweighting insufficient |

Hard structural gates never relax. Multiple worlds that share supported targets
but differ in weak assumptions are required (e.g. different residual
confounding or comorbidity dependence).

## 9. Evaluation gates (preview; freeze before fitting)

Hard:

- Schema / key / temporal / enrollment validators pass.
- Deterministic reproduction under pinned seeds/manifests.
- No silent MA/FFS or year conflation in reports.

Graded:

- Agreement with training evidence within yet-to-be-frozen tolerances.
- Held-out compatible evidence not used in fitting.
- Nondegeneracy (not clone-only; not near-deterministic O1).

## 10. Open decisions (human)

Copied from cohort note; blockers for Phase 3 freeze, not for Phase 1 start:

1. FFS Option A vs C as corpus default.
2. Collapse vs retain `sp_*` 1/2 distinction.
3. Exact numeric training targets and holdout partition.
4. Whether HF is co-calibrated or diagnostic-only.
5. Transport policy for evidence years ≠ 2021.

## 11. Success for the overall MVP (Milestone C orientation)

An investigator can generate reproducible structurally valid cohorts for
`mvp-2021-om-ffs-diabetes-ip`, see which published quantities constrain the
world, run the same diabetes→IP analysis across a few plausible worlds, and
carry code/design—not synthetic conclusions—into authorized real-data work.
