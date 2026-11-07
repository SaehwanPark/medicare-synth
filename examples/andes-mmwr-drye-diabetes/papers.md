# Papers A and B

## Shared topic

Diabetes among Medicare fee-for-service elderly beneficiaries — prevalence
(A) and acute hospitalization utilization (B).

## Paper A — in-domain calibration target

| Field | Value |
| --- | --- |
| Citation | Andes LJ, Li Y, Srinivasan M, Benoit SR, Gregg E, Rolka DB. Diabetes Prevalence and Incidence Among Medicare Beneficiaries — United States, 2001–2015. *MMWR*. 2019;68(43):961–966. |
| URL | https://www.cdc.gov/mmwr/volumes/68/wr/mm6843a2.htm |
| Estimand | Crude diagnosed-diabetes prevalence among eligible Medicare FFS |
| Point estimate | **31.6%** (2015 overall) |
| Population | FFS, age ≥68, multi-year Parts A+B window |
| Inventory | LIT-03 |
| Example role | **Calibration** (example-local corpus; not a change to frozen MVP corpus v1) |

MVP approximation: MBSF `sp_diabetes`, Option B full-year A+B, age ≥68 at
execution. Year transport 2015 → 2021 context is explicit.

## Paper B — out-domain evaluation

| Field | Value |
| --- | --- |
| Citation | Drye EE, et al. Risk-standardized acute admission rates among patients with diabetes and heart failure. *Med Care* (PMC5356461). |
| URL | https://pmc.ncbi.nlm.nih.gov/articles/PMC5356461/ |
| Estimand | Crude national **acute unplanned** admission rate among diabetes cohort |
| Point estimate | **41.4 per 100 person-years** (2012 diabetes cohort) |
| Inventory | LIT-02 |
| Example role | **Excluded / diagnostic only** — planned-admission + person-time rate unsupported on MVP schema |

### Why B is out of domain

1. Source excludes planned admissions (~12% of stays); MVP O1 is all-cause
   claim presence.
2. Source is events per person-year; MVP O1 is binary annual risk.
3. Year 2012 → 2021 transport required.
4. Evidence IR fixture
   `lit02-drye-diabetes-unplanned-admission-rate-2012` is **non-executable**
   by design (corpus excluded partition).

The example still computes MVP `P(IP | diabetes)` as a **non-equivalent**
diagnostic quantity and records the gaps—never as a Drye replication.
