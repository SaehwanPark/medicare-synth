# Phase 2 — LIT-03 formalization (Milestone B)

**Status:** Complete for Phase 2 formalization/execution
**Finding ID:** `lit03-mmwr-diabetes-prevalence-2015`
**Inventory:** LIT-03
**Fixture:** [`fixtures/lit03_mmwr_diabetes_prevalence_2015.json`](fixtures/lit03_mmwr_diabetes_prevalence_2015.json)
**Machine report:** [`reports/phase2/lit03_comparison.json`](../../reports/phase2/lit03_comparison.json)

## Source anchors

| Item | Value |
| --- | --- |
| Citation | Andes LJ, Li Y, Srinivasan M, Benoit SR, Gregg E, Rolka DB. *Diabetes Prevalence and Incidence Among Medicare Beneficiaries — United States, 2001–2015.* MMWR. 2019;68(43):961–966 |
| URL | https://www.cdc.gov/mmwr/volumes/68/wr/mm6843a2.htm |
| PDF | https://www.cdc.gov/mmwr/volumes/68/wr/pdfs/mm6843-H.pdf |
| Anchor | Abstract / Results: 2015 overall prevalence **31.6%** among Medicare FFS beneficiaries aged ≥68 years |
| Uncertainty | Text: margin of error &lt;0.02% for all estimates (near-census claims); IR records SE upper bound 0.0002 |

## Estimand

Crude prevalence of diagnosed diabetes among eligible Medicare FFS beneficiaries
in index year 2015: \(\hat p = 0.316\).

Source diabetes definition: multi-year inpatient/outpatient ICD claims algorithm
(not MBSF `sp_diabetes`). Source enrollment: Parts A+B for all 60 months of a
5-year window centered on the index year (or until death).

## Compatibility (explicit)

| Gap | Handling |
| --- | --- |
| Year 2015 vs MVP context 2021 | `YEAR-TRANSPORT` warning; `transport_required=true` |
| Age ≥68 vs MVP generation ≥65 | Eligibility uses evidence minimum 68 |
| 60-month continuous A+B vs Option B | `FFS-CUSTOM` → Option B approximation |
| Claims algorithm vs `sp_diabetes` | `ALG-APPROX` → `mbsf_sp_diabetes_v1` |

Role: **`diagnostic`**. Accepted for Phase 2 IR formalization only—not a Phase 3
calibration target or holdout freeze.

## Execution (synthetic comparison)

Against a Phase 1 known-truth world (`n=8000`, `seed=42`,
`diabetes_prevalence=0.316`):

| Quantity | Value |
| --- | --- |
| Evidence estimate | 0.316 |
| Synthetic estimate (age≥68 eligible) | ≈ 0.318 |
| Absolute difference | ≈ 0.002 |
| Eligible N | 7057 |

Reproducible via:

```python
from medicare_synth.evidence_ir import load_finding, execute_finding, package_fixtures_dir
from medicare_synth.synthesis import ConditionalWorldParams, generate_diabetes_ip_world

finding = load_finding(package_fixtures_dir() / "lit03_mmwr_diabetes_prevalence_2015.json")
world = generate_diabetes_ip_world(ConditionalWorldParams(
  n_beneficiaries=8000, seed=42,
  diabetes_prevalence=0.316,
  p_ip_given_diabetes=0.20,
  p_ip_given_no_diabetes=0.08,
))
report = execute_finding(finding, world.tables())
```

**Non-claim:** Agreement on a synthetic world does not validate Medicare
representativeness or authorize publishing synthetic prevalence as a Medicare
finding.

## Negative control

[`fixtures/lit02_drye_admission_rate_unsupported.json`](fixtures/lit02_drye_admission_rate_unsupported.json)
encodes LIT-02-shaped unplanned admission rates. The compiler emits
`PLANNED-ADMISSION` and refuses execution rather than silently substituting
all-cause O1.
