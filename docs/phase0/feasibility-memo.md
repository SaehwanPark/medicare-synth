# Phase 0 — Feasibility memo

**Date:** 2026-11-06
**Decision:** **Proceed** to Phase 1 (synthesizer verification) with the pinned
MVP context below.
**Exit criteria:** Met — see §5.

## 1. Question

Is there a coherent first research context—and enough implementable
public/Medicare-only evidence—to justify hardening Evidence IR and calibration
design, without ignoring fatal comparability problems?

## 2. Recommended MVP context

**2021 Original Medicare FFS beneficiaries aged ≥65, with MBSF chronic-condition
diabetes indicator as primary exposure (heart failure as stratifier), and
all-cause inpatient hospitalization in the reference year as the primary
utilization outcome.**

Rationale:

- Aligns with the repository baseline schema year (`CMS-2021-SYN-CLAIMS`).
- Core tables and fields already exist for eligibility, exposure, and outcome
  ([mvp-cohort-and-fields.md](mvp-cohort-and-fields.md)).
- Official CMS products (especially MMD) and Medicare-only literature report
  related prevalence and admission-rate estimands
  ([evidence-inventory.md](evidence-inventory.md)).
- Avoids schema-blocked diagnosis-specific admission measures as the *first*
  estimand while documenting them as a later expansion.

## 3. Feasibility findings

### 3.1 Expressible analysis (required)

The following analysis can be stated and executed against structurally valid
synthetic tables that expose current MVP fields:

> Among synthetic beneficiaries mapped to the 2021 OM FFS age-65+ cohort rule
> (Option B), estimate `P(≥1 inpatient admission in 2021 | sp_diabetes ∈ {1,2})`
> versus `sp_diabetes = 0` (collapse of `1`/`2` is an implementable default,
> not a Phase 3 freeze), optionally stratified by `sp_chf` and sex.

Person-time variants (admissions per 100 beneficiary-years) are also
expressible if death and enrollment months define exposure time.

This satisfies the Phase 0 bar that **at least one** population / condition /
utilization analysis is expressible with available or reasonably implementable
fields.

### 3.2 Generator honesty

Current vertical/horizontal expansion does **not** provide controllable
conditional relationships ([capability-gaps.md](capability-gaps.md)). Phase 0
therefore concludes feasibility of the *context and evidence path*, not
readiness of the generator for calibrated releases. Phase 1 remains mandatory
before claiming statistical support.

### 3.3 Evidence sufficiency (scouting level)

- **Enough to start:** CMS MMD **prevalence** measures; CCW methodological
  guidance; at least one Medicare FFS diabetes admission-rate paper (Drye et
  al.) as a related person-time prior with documented estimand gaps vs O1.
  MMD condition-specific hospitalization rates are diagnostic until IP ICD
  exists.
- **Not enough to freeze:** Year mismatches, algorithm transitions (especially
  HF), dependent CCW-derived sources, and missing monthly MA panels for the
  strictest FFS definitions. These are tracked, not ignored.
- **Human gate:** No evidence item is approved for calibration by this memo.

### 3.4 Fatal comparability screen

| Candidate fatal issue | Assessment |
| --- | --- |
| Cannot define FFS-like cohort | **Not fatal** — annual HMO/Parts A–B months exist (Option B default); monthly panel (Option C) is a fidelity upgrade |
| Cannot define diabetes/HF | **Not fatal** — `sp_diabetes`, `sp_chf` present |
| Cannot define hospitalization | **Not fatal** — inpatient claims + optional `ip_adm_cnt` |
| Only DX-specific outcomes exist in literature | **Not fatal** — all-cause rates exist (LIT-02); DX-specific deferred |
| 27→30 CCW break silently invalidates all targets | **Not fatal if documented** — pin algorithm; prefer post-transition for HF; diabetes relatively stable in CCW impact study |
| Syn Claims fixtures mistaken for Medicare truth | **Process risk** — mitigated by explicit non-goal in SPEC / limitations |

No known fatal issue is ignored; residual risks are listed in §6.

## 4. What Phase 0 delivers (artifact map)

| Deliverable | Path |
| --- | --- |
| Capability gaps | [capability-gaps.md](capability-gaps.md) |
| Cohort + fields | [mvp-cohort-and-fields.md](mvp-cohort-and-fields.md) |
| Evidence inventory | [evidence-inventory.md](evidence-inventory.md) |
| Draft MVP specification | [draft-mvp-specification.md](draft-mvp-specification.md) |
| This memo | [feasibility-memo.md](feasibility-memo.md) |
| Offline persistence | `~/data/medicare-synth/phase0/` |

## 5. Exit criteria checklist

| Criterion | Status |
| --- | --- |
| ≥1 population/condition/utilization analysis expressible with available or reasonably implementable fields | **Met** (§3.1) |
| No known fatal comparability issue ignored | **Met** (§3.4, inventory §5) |

## 6. Residual risks for later phases

1. Option B FFS definition understates MA leakage relative to MMD “any MA month”
   exclusion until monthly `hmo_ind_*` (Option C) is modeled.
2. Transport from 2011–2015 literature to 2021 may dominate calibration error;
   prefer 2021 MMD extracts when pinning numeric targets.
3. Overlapping CCW-derived aggregates induce double-counting if treated as
   independent constraints.
4. Without IP ICD fields, the platform cannot validate condition-specific
   admission papers that many clinicians expect—communicate O1 scope clearly.
5. Agents must not treat this memo’s cited magnitudes as approved IR values.

## 7. Go / no-go for Phase 1

**Go.** Begin Phase 1 synthesizer contract and known-truth experiments against
the pinned MVP context. Do not start Phase 5 calibration fitting until Phases
1–3 gates pass.
