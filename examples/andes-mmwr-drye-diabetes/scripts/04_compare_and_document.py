"""Assemble calibration comparison JSON and refresh COMPARISON.md."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src") not in sys.path:
  sys.path.insert(0, str(_REPO / "src"))

from _paths import ANDES_ABS_TOL, EXAMPLE_ROOT, REPORTS_DIR  # noqa: E402


def _load(name: str) -> dict:
  return json.loads((REPORTS_DIR / name).read_text(encoding="utf-8"))


def main() -> int:
  build = _load("build_and_calibrate.json")
  paper_a = _load("in_domain_a.json")
  paper_b = _load("out_domain_b.json")

  summary = {
    "example_id": "andes-mmwr-drye-diabetes",
    "paper_a_aligned": paper_a["in_domain_aligned"],
    "paper_b_exact_refused": paper_b["exact_estimand_refused"],
    "calibration_mae_before": build["calibration_before"]["mean_absolute_error"],
    "calibration_mae_after": build["calibration_after"]["mean_absolute_error"],
    "holdout_mae_before": build["holdout_before"]["mean_absolute_error"],
    "holdout_mae_after": build["holdout_after"]["mean_absolute_error"],
    "fitted_diabetes_prevalence": build["fitted_params"]["diabetes_prevalence"],
    "andes_calibrated_estimate": paper_a["calibrated"]["synthetic_estimate"],
    "andes_abs_diff": paper_a["calibrated"]["absolute_difference"],
    "drye_diagnostic_p_ip_given_diabetes": paper_b["diagnostic_mvp_o1"][
      "p_ip_given_diabetes"
    ],
    "disclaimer": (
      "Synthetic agreement is not a Medicare finding; do not publish these "
      "estimates as empirical results about beneficiaries."
    ),
  }
  REPORTS_DIR.mkdir(parents=True, exist_ok=True)
  (REPORTS_DIR / "comparison_summary.json").write_text(
    json.dumps(summary, indent=2) + "\n", encoding="utf-8"
  )

  md = f"""# Calibration comparison — Andes (A) vs Drye (B)

> **Disclaimer:** Synthetic agreement is **not** a Medicare finding. Do not
> cite these numbers as empirical results about Medicare beneficiaries.

## Setup

| Item | Value |
| --- | --- |
| Context | `mvp-2021-om-ffs-diabetes-ip` |
| Example corpus | `example-andes-mmwr-drye-v1` |
| N beneficiaries | {build["fitted_params"]["n_beneficiaries"]} |
| Seed | {build["fitted_params"]["seed"]} |
| Method | Level C generator-parameter search |
| Paper A target | Andes MMWR 2015 diabetes prevalence **0.316** |
| Paper B | Drye unplanned admission rate **41.4 / 100 PY** (excluded) |

## Calibration ladder (paper A)

| Partition | MAE before | MAE after |
| --- | ---: | ---: |
| Calibration (Andes overall) | {summary["calibration_mae_before"]} | {summary["calibration_mae_after"]} |
| Holdout (Andes women stratum) | {summary["holdout_mae_before"]} | {summary["holdout_mae_after"]} |

Fitted `diabetes_prevalence` parameter: **{summary["fitted_diabetes_prevalence"]}**.

Improved vs baseline: **{build["improved_calibration"]}**. Structural validity:
**{build["structural_valid"]}**.

## In-domain replication (paper A)

| Quantity | Baseline | Calibrated |
| --- | ---: | ---: |
| Synthetic prevalence (age ≥68 eligible) | {paper_a["baseline"]["synthetic_estimate"]} | {paper_a["calibrated"]["synthetic_estimate"]} |
| Absolute difference vs 0.316 | {paper_a["baseline"]["absolute_difference"]} | {paper_a["calibrated"]["absolute_difference"]} |
| Eligible N | {paper_a["baseline"]["n_eligible"]} | {paper_a["calibrated"]["n_eligible"]} |

Alignment gate: `|diff| ≤ {ANDES_ABS_TOL}` → **{paper_a["in_domain_aligned"]}**.

## Out-domain confrontation (paper B)

| Check | Result |
| --- | --- |
| Exact Evidence IR execution | refused = **{paper_b["exact_estimand_refused"]}** |
| IR errors | {paper_b["exact_ir_execution"].get("errors")} |
| Diagnostic MVP `P(IP \\| diabetes)` | {summary["drye_diagnostic_p_ip_given_diabetes"]} (binary annual risk) |
| Drye published magnitude | 41.4 per 100 person-years (unplanned) |

Gaps (non-equivalence): {", ".join(paper_b["non_equivalence_gaps"])}.

The diagnostic O1 quantity is **not** a Drye replication. Andes prevalence
calibration does not constrain utilization to Drye's person-time unplanned
rate, and the MVP schema cannot execute that estimand honestly.

## Disposition

- **Paper A:** {"aligned after Level C calibration" if paper_a["in_domain_aligned"] else "NOT aligned — investigate eligibility/moment mismatch or grid coverage"}.
- **Paper B:** out-of-domain by construction; exact path refused; diagnostic only.
- **Library note:** calibration discrepancy moments evaluate on each finding's
  Evidence IR eligible cohort so Andes age ≥68 execution matches fit metrics.

## Reproduce

```shell
uv run python examples/andes-mmwr-drye-diabetes/scripts/run_example.py
```
"""
  (EXAMPLE_ROOT / "COMPARISON.md").write_text(md, encoding="utf-8")
  print("wrote", REPORTS_DIR / "comparison_summary.json")
  print("wrote", EXAMPLE_ROOT / "COMPARISON.md")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
