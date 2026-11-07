# Calibration comparison — Andes (A) vs Drye (B)

> **Disclaimer:** Synthetic agreement is **not** a Medicare finding. Do not
> cite these numbers as empirical results about Medicare beneficiaries.

## Setup

| Item | Value |
| --- | --- |
| Context | `mvp-2021-om-ffs-diabetes-ip` |
| Example corpus | `example-andes-mmwr-drye-v1` |
| N beneficiaries | 6000 |
| Seed | 42 |
| Method | Level C generator-parameter search |
| Paper A target | Andes MMWR 2015 diabetes prevalence **0.316** |
| Paper B | Drye unplanned admission rate **41.4 / 100 PY** (excluded) |

## Calibration ladder (paper A)

| Partition | MAE before | MAE after |
| --- | ---: | ---: |
| Calibration (Andes overall) | 0.11581042654 | 0.000398104265 |
| Holdout (Andes women stratum) | 0.092727272727 | 0.022545454545 |

Fitted `diabetes_prevalence` parameter: **0.316**.

Improved vs baseline: **True**. Structural validity:
**True**.

## In-domain replication (paper A)

| Quantity | Baseline | Calibrated |
| --- | ---: | ---: |
| Synthetic prevalence (age ≥68 eligible) | 0.20018957346 | 0.316398104265 |
| Absolute difference vs 0.316 | -0.11581042654 | 0.000398104265 |
| Eligible N | 5275 | 5275 |

Alignment gate: `|diff| ≤ 0.015` → **True**.

## Out-domain confrontation (paper B)

| Check | Result |
| --- | --- |
| Exact Evidence IR execution | refused = **True** |
| IR errors | ['finding role is excluded'] |
| Diagnostic MVP `P(IP \| diabetes)` | 0.07575 (binary annual risk) |
| Drye published magnitude | 41.4 per 100 person-years (unplanned) |

Gaps (non-equivalence): planned_vs_all_cause_admissions, person_time_vs_binary_risk, year_2012_vs_2021.

The diagnostic O1 quantity is **not** a Drye replication. Andes prevalence
calibration does not constrain utilization to Drye's person-time unplanned
rate, and the MVP schema cannot execute that estimand honestly.

## Disposition

- **Paper A:** aligned after Level C calibration.
- **Paper B:** out-of-domain by construction; exact path refused; diagnostic only.
- **Library note:** calibration discrepancy moments evaluate on each finding's
  Evidence IR eligible cohort so Andes age ≥68 execution matches fit metrics.

## Reproduce

```shell
uv run python examples/andes-mmwr-drye-diabetes/scripts/run_example.py
```
