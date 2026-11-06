# Phase 0 — Generator and capability gaps (MVP context)

**Status:** Complete for Phase 0 scouting (2026-11-06)
**MVP context:** 2021 Original Medicare FFS, age 65+, diabetes (± heart
failure) → all-cause inpatient hospitalization
**Code basis:** `src/medicare_synth/{models,expansion,scenarios,validation,catalog}.py`

This note characterizes what Medicare-Synth can support today for the MVP
research context. It is **not** a claim that current fixtures match Medicare
distributions.

## 1. Summary judgment

| Layer | Status for MVP |
| --- | --- |
| Structural tables / joins | **Sufficient** for a thin beneficiary–enrollment–CC–inpatient slice |
| Cohort eligibility fields | **Partially sufficient**; annual HMO/Parts A–B months exist; monthly panels are stubbed |
| Chronic exposure flags | **Present** (`sp_diabetes`, `sp_chf`) with `{"0","1","2"}` domain |
| Hospitalization outcome | **Present as claim presence / dates / DRG / payment**; **no** inpatient principal diagnosis |
| Conditional synthesis | **Absent** — index/seed fixture math + subgraph cloning only |
| Calibration / Evidence IR | **Absent** (provenance enum recognizes `EXTERNALLY_CALIBRATED` only) |

**Implication:** Phase 0 exit is met for *expressibility* of one
population/condition/utilization analysis on available or reasonably
implementable fields. Phase 1 must still prove genuine conditional generation
before calibration can claim statistical support.

## 2. What works today

### 2.1 Relevant domain tables (of 19)

MVP **core**: `beneficiary_summary`, `mbsf_base_enrollment`,
`mbsf_chronic_conditions`, `inpatient_claims`.

MVP **supporting**: `mbsf_ffs_utilization` (`ip_adm_cnt` annual proxy),
`mbsf_part_c` (MA months for FFS exclusion), `mbsf_other_chronic_conditions`
(comorbid context), `mbsf_cost_and_use`, `mbsf_ndi` (death censoring).

Out of MVP core: Part D / PDE, SNF/HHA/DME/hospice, carrier/outpatient (useful
later for diagnosis-based algorithms or ambulatory utilization).

### 2.2 Expressible analysis (structural)

On fixtures or generated tables that preserve the same grains:

1. Restrict to age ≥ 65 via `bene_birth_dt` vs reference year end (2021-12-31).
2. Restrict to Original Medicare FFS-like enrollment via
   `bene_hi_cvrage_tot_mons`, `bene_smi_cvrage_tot_mons`,
   `bene_hmo_cvrage_tot_mons` / `bene_ma_cvrage_tot_mons` (exact rule TBD in
   draft MVP spec; annual totals are available).
3. Define diabetes / HF exposure from `sp_diabetes` / `sp_chf` (CCW-style
   indicators; treat code semantics as evidence-bound, not clinical truth).
4. Define all-cause IP hospitalization as ≥1 `inpatient_claims` row with
   `clm_admsn_dt` in the reference year (or use `ip_adm_cnt` as an annual
   summary alternative).
5. Compare hospitalization rates (or binary occurrence) by diabetes flag,
   optionally stratified by sex (`bene_sex_ident_cd`) or HF comorbidity.

This is enough for Evidence IR prototyping and known-truth synthesizer tests.
It is **not** enough for diagnosis-coded preventable diabetes admissions without
schema work.

### 2.3 Validation substrate

Relational validators already cover CC indicator domains, IP admit≤discharge,
DRG format, Parts A/B month totals, and (when columns are present) monthly
buy-in / dual / HMO indicator / entitlement-reason domains. Structural hard
gates can remain in place for calibrated worlds.

## 3. Gaps ranked by MVP impact

### Critical for calibrated research worlds (Phase 1+)

1. **No conditional generator.** `TabDatSynthAdapter` fills features as
   `(row_index * (seed + col_idx + 1) % 100) / 10.0`. `HorizontalExpander`
   clones subgraphs and suffixes keys. Neither produces
   `P(hospitalization | diabetes, age, enrollment)`.
2. **No Evidence IR / estimand compiler / calibration engine.** Only the
   provenance status name exists.

### High — needed for honest FFS cohort fidelity

3. **Enrollment thinness.** Models expose buy-in / dual for month `_01` only;
   validators expect `_01`–`_12`. `hmo_ind_*` and `entlmt_rsn_*` are
   validator-only (not in Pydantic models / scenarios). Strict “no MA month”
   definitions used in many CMS analyses need the monthly HMO panel.
4. **Age is derived only.** No `age_at_end_ref_yr`; fixtures include under-65
   `BENE_003`. Cohort filters must be explicit in analysis code.
5. **RKB coverage for CC diabetes/HF variable metadata is incomplete** relative
   to OC entries — do not treat RKB as complete field documentation for MVP
   exposures.

### Medium — limits estimand family, not Phase 0 feasibility

6. **No inpatient principal / secondary diagnosis fields** on
   `InpatientClaimHeaderRecord` (carrier/OP have `icd_dgns_cd1`). Blocks
   condition-specific admission rates and DRG–ICD coherence checks.
7. **`ncvd_days_cnt`, discharge status, admission type** are validator-aware
   but absent from the IP model / scenarios.
8. **Geography** (`bene_state_cd` / `bene_county_cd`) not in beneficiary model;
   blocks county-level MMD-style targets without schema extension.
9. **`valid_chronic_subgroup` scenario** filters by beneficiary ID, not by
   condition algorithm — teaching fixture only.

### Low for MVP (defer)

10. Part D insulin exposure stratification, provider networks, ACO attribution,
    readmission episode construction, multi-year lookbacks for incident
    diabetes.

## 4. What “reasonably implementable” means here

Phase 0 treats the following as **in scope to implement later**, not blockers
to feasibility:

| Gap | Reasonable next step | Phase |
| --- | --- | --- |
| Conditional synthesis contract | Parameterized beneficiary-level draws with linked claims | 1 |
| Monthly HMO / buy-in panels | Extend `MBSFBaseEnrollmentRecord` + fixtures | 1–2 |
| IP principal diagnosis | Add ICD fields aligned with baseline Syn Claims | 1–2 |
| Age-at-year-end helper | Derived column or analysis helper, not necessarily stored | anytime |
| Evidence IR v0.1 | Typed finding objects for prevalence + rate estimands | 2 |

## 5. Non-gaps (do not over-interpret)

- Breadth of 19 tables does **not** imply each is ready for calibration.
- Passing structural validators does **not** imply contextual realism.
- `EXTERNALLY_CALIBRATED` provenance does **not** imply a calibration engine.
- CMS Syn Claims baseline ages/flags are **synthetic**; matching them is not a
  fidelity target for literature calibration.

## 6. Exit relevance

Phase 0 requires that at least one meaningful analysis be expressible. The
diabetes → all-cause IP hospitalization contrast on age-65+ FFS-like enrollment
meets that bar with **existing core fields**, provided enrollment rules and
indicator semantics are documented and comparability issues (see
[evidence-inventory.md](evidence-inventory.md)) are not ignored.
