"""Replicate paper A (Andes MMWR diabetes prevalence) on calibrated Parquet.

Loads calibrated tables, executes the Evidence IR finding, and records
alignment vs the published 31.6% estimate. Not a Medicare finding.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src") not in sys.path:
  sys.path.insert(0, str(_REPO / "src"))

from medicare_synth.evidence_ir import execute_finding, load_finding  # noqa: E402

from _paths import (  # noqa: E402
  ANDES_ABS_TOL,
  ANDES_FINDING_ID,
  FIXTURES_ROOT,
  PARQUET_DIR,
  REPORTS_DIR,
)


def _load_tables(parquet_dir: Path) -> dict[str, pl.DataFrame]:
  return {
    p.stem: pl.read_parquet(p)
    for p in sorted(parquet_dir.glob("*.parquet"))
  }


def main() -> int:
  finding = load_finding(
    FIXTURES_ROOT
    / "evidence_ir"
    / "lit03_mmwr_diabetes_prevalence_2015.json"
  )
  assert finding.finding_id == ANDES_FINDING_ID

  baseline = _load_tables(PARQUET_DIR / "baseline")
  calibrated = _load_tables(PARQUET_DIR / "calibrated_to_a")

  base_report = execute_finding(finding, baseline)
  cal_report = execute_finding(finding, calibrated)

  aligned = (
    cal_report.executable
    and cal_report.absolute_difference is not None
    and abs(cal_report.absolute_difference) <= ANDES_ABS_TOL
  )
  payload = {
    "finding_id": finding.finding_id,
    "paper": "Andes MMWR 2019 (LIT-03)",
    "evidence_estimate": finding.result.estimate,
    "abs_tolerance": ANDES_ABS_TOL,
    "baseline": base_report.model_dump(mode="json"),
    "calibrated": cal_report.model_dump(mode="json"),
    "in_domain_aligned": aligned,
    "notes": [
      "Eligibility: age ≥68, Option B A+B approximation.",
      "Algorithm: MBSF sp_diabetes approximates Andes claims definition.",
      "Synthetic agreement is not a Medicare finding.",
    ],
  }
  REPORTS_DIR.mkdir(parents=True, exist_ok=True)
  out = REPORTS_DIR / "in_domain_a.json"
  out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
  print(f"wrote {out}")
  print(
    "A calibrated estimate",
    cal_report.synthetic_estimate,
    "diff",
    cal_report.absolute_difference,
    "aligned",
    aligned,
  )
  return 0 if aligned else 2


if __name__ == "__main__":
  raise SystemExit(main())
