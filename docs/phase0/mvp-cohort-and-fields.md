# Phase 0 — Candidate 2021 Original Medicare FFS cohort and fields

**Status:** Draft decision record for Phase 0 (2026-11-06)
**Companion:** [draft-mvp-specification.md](draft-mvp-specification.md),
[capability-gaps.md](capability-gaps.md)

Open product decisions remain explicit. Do not invent silent enrollment or
algorithm rules in generators or Evidence IR.

## 1. Pinned research context

| Dimension | Candidate decision | Notes / open items |
| --- | --- | --- |
| Program year | **2021** | Aligns with `CMS-2021-SYN-CLAIMS` baseline schema year |
| Program | **Original Medicare FFS** (Parts A and B) | Exclude Medicare Advantage / managed care |
| Age | **≥ 65** at end of reference year | Derived from `bene_birth_dt`; under-65 disabled/ESRD out of MVP |
| Index condition | **Diabetes** via MBSF CC `sp_diabetes` | Primary exposure |
| Comorbid condition | **Heart failure** via `sp_chf` | Secondary exposure / stratifier |
| Outcome | **All-cause inpatient hospitalization** in 2021 | ≥1 inpatient claim with admission in year; annual `ip_adm_cnt` as alternate grain |
| Geography | **National synthetic cohort** | No state/county requirement for MVP v0 |
| Drugs | **Out of MVP core** | Insulin stratification deferred |

**Primary analysis (expressibility target):** among 2021 OM FFS beneficiaries
aged ≥65, compare the probability (or rate) of ≥1 inpatient admission by
diabetes indicator, optionally stratified by heart-failure indicator and sex.

## 2. Cohort inclusion / exclusion (candidate rules)

These are **proposed** rules for later Evidence IR and synthesis contracts.
Human review is required before freezing a calibrated corpus (Phase 3).

### 2.1 Include when

1. Alive and observable for at least part of 2021 (death allowed; censor at
   `bene_death_dt` when constructing person-time rates).
2. Age ≥ 65 on 2021-12-31 (or on death date if earlier), computed from
   `bene_birth_dt`.
3. Part A coverage months ≥ threshold **and** Part B coverage months ≥
   threshold in 2021.
4. Managed-care months = 0 under the chosen FFS definition (below).
5. Present on required tables: beneficiary, MBSF base, MBSF CC; inpatient may
   be zero-row (no admission).

### 2.2 FFS / managed-care definition — open choice (must pick before Phase 3 freeze)

| Option | Rule using available fields | Pros | Cons |
| --- | --- | --- | --- |
| **A (recommended for MVP v0)** | `bene_hmo_cvrage_tot_mons == 0` and `bene_ma_cvrage_tot_mons == 0` (when Part C table present) | Implementable now with annual totals | Weaker than “any MA month” monthly panel used in many CMS studies |
| **B** | Full-year Parts A+B (`*_tot_mons == 12`) and HMO months == 0 | Matches many CCW “full-year FFS” denominators | Drops partial-year enrollees; may bias utilization |
| **C** | Monthly `hmo_ind_*` never indicates MA for months with A/B buy-in | Closest to MMD/CCW practice | Requires modeling monthly HMO indicators (gap today) |

**Phase 0 stance:** Document Option A as the **implementable default** for
prototype estimands; treat Option C as the **preferred fidelity target** once
monthly fields are first-class. Do not silently mix A/B/C across evidence
records.

### 2.3 Parts A/B coverage threshold — open choice

| Option | Rule | Use when |
| --- | --- | --- |
| **Full-year** | HI and SMI months == 12 | Aligning to many prevalence denominators |
| **Any-month** | HI and SMI months ≥ 1 | Maximizing N; weaker utilization rates |
| **Person-time** | Weight by covered months / 12 | Rate estimands with explicit exposure time |

**Phase 0 stance:** Prefer **full-year** for prevalence-style targets and
**person-time** for admission rates when evidence reports rates per
beneficiary-year. Record which rule each evidence item assumes.

### 2.4 Explicit exclusions

- Age < 65 (including disability-only under-65), unless a future context opts in.
- Beneficiaries with MA/HMO months under the chosen FFS rule.
- Analyses that require MA encounter data.
- Condition-specific (principal-diagnosis) admission measures until IP ICD
  fields exist.

## 3. Minimal dependency graph

```text
beneficiary_summary
        │
        ├── mbsf_base_enrollment          (Parts A/B/HMO months; buy-in stub)
        ├── mbsf_part_c                   (optional MA months cross-check)
        ├── mbsf_chronic_conditions       (sp_diabetes, sp_chf, …)
        ├── mbsf_ffs_utilization          (optional ip_adm_cnt)
        └── inpatient_claims              (0..N stays: dates, DRG, payment)
```

Optional later edges: `mbsf_other_chronic_conditions` (comorbidities),
`mbsf_ndi` (death cause), carrier/outpatient (algorithm rebuilds), PDE
(insulin).

## 4. Required fields inventory

### 4.1 Present in models / scenarios

| Purpose | Table | Field(s) | Status |
| --- | --- | --- | --- |
| ID | all | `bene_id` | Present |
| DOB / death | beneficiary | `bene_birth_dt`, `bene_death_dt` | Present |
| Sex / race | beneficiary | `bene_sex_ident_cd`, `bene_race_cd` | Present |
| Part A/B/HMO months | mbsf_base | `bene_hi_cvrage_tot_mons`, `bene_smi_cvrage_tot_mons`, `bene_hmo_cvrage_tot_mons` | Present |
| MA months | mbsf_part_c | `bene_ma_cvrage_tot_mons` | Present |
| Diabetes | mbsf_cc | `sp_diabetes` | Present (`0/1/2`) |
| Heart failure | mbsf_cc | `sp_chf` | Present (`0/1/2`) |
| Related CVD | mbsf_cc | `sp_ischdmt` | Present |
| IP stay | inpatient | `clm_id`, `clm_admsn_dt`, `nch_bene_dschrg_dt`, `clm_pmt_amt`, `clm_utlztn_day_cnt`, `clm_drg_cd` | Present |
| Annual IP count | mbsf_ffs | `ip_adm_cnt` | Present |
| Reference year | mbsf_* | `rfrnc_yr` | Present (default 2021) |

### 4.2 Validator-aware but not modeled / fixtured (must-generate or extend)

| Purpose | Expected fields | Gap |
| --- | --- | --- |
| Monthly FFS purity | `hmo_ind_01`–`_12` | Not in model |
| Monthly buy-in | `mdcr_entlmt_buyin_ind_01`–`_12` | Only `_01` in model |
| Dual status | `dual_stus_cd_01`–`_12` | Only `_01` in model |
| Entitlement reason | `entlmt_rsn_orig` / `entlmt_rsn_curr` | Validator-only |
| IP principal DX | `icd_dgns_cd1` / `prncpal_dgns_cd` | Missing on IP |
| Geography | `bene_state_cd`, `bene_county_cd` | Not in beneficiary model |
| Age at year end | derived or stored | Derive only |

### 4.3 Indicator semantics (do not invent)

CCW-style `sp_*` codes commonly use values such as `0` = not met,
`1`/`2` = met with differing claim-evidence patterns. Exact algorithm version
(27- vs 30-condition CCW, lookback years, claim types) must be pinned per
evidence record. Fixture values in scenarios are **teaching labels**, not CMS
algorithm outputs.

**MVP coding proposal:** treat `{1,2}` as “condition present” and `0` as
absent unless a specific evidence item requires distinguishing `1` vs `2`.

## 5. Outcome definitions

| ID | Definition | Fields | Expressible now? |
| --- | --- | --- | --- |
| **O1** | Binary: ≥1 IP claim with `clm_admsn_dt` in 2021 | inpatient | Yes |
| **O2** | Count of distinct IP claims in 2021 | inpatient | Yes |
| **O3** | Annual summary admissions | `ip_adm_cnt` | Yes (grain differs) |
| **O4** | Diabetes-principal admission | IP ICD | **No** — schema gap |
| **O5** | HF-related DRG set (e.g., MS-DRG 291–293 family) | `clm_drg_cd` | Partial — DRG present; mapping is an assumption |

**MVP default outcome:** **O1** (all-cause). Use O5 only as a diagnostic
sensitivity with explicit DRG list provenance.

## 6. Analysis expressibility checklist

- [x] Population filter (age, program year) expressible
- [x] FFS-like filter expressible under Option A
- [x] Diabetes exposure expressible
- [x] HF stratifier expressible
- [x] All-cause hospitalization expressible
- [ ] Monthly MA exclusion (Option C) without schema extension
- [ ] Diagnosis-specific hospitalization without IP ICD fields
- [ ] County-level MMD targets without geography fields

## 7. Decisions deferred (human gates)

1. Final FFS rule (A vs B vs C) for the frozen MVP evidence corpus.
2. Whether `sp_*` `1` vs `2` is collapsed.
3. Whether person-time or full-year denominators are default for rate targets.
4. Whether HF is co-primary exposure or only a stratifier.
5. Transport rules when calibrating to evidence years ≠ 2021.
