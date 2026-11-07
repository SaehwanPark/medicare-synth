"""Confront paper B (Drye unplanned admission rates) as out-of-domain.

Exact Evidence IR execution must refuse. A diagnostic MVP O1 quantity
P(IP | diabetes) is computed only to illustrate non-equivalence — never as a
Drye replication or Medicare finding.
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
  DRYE_FINDING_ID,
  FIXTURES_ROOT,
  PARQUET_DIR,
  REPORTS_DIR,
)


def _load_tables(parquet_dir: Path) -> dict[str, pl.DataFrame]:
  return {
    p.stem: pl.read_parquet(p)
    for p in sorted(parquet_dir.glob("*.parquet"))
  }


def _p_ip_given_diabetes(tables: dict[str, pl.DataFrame]) -> dict:
  """Diagnostic MVP O1 binary risk among diabetes — not Drye's estimand."""
  cc = tables["mbsf_chronic_conditions"]
  ip = tables["inpatient_claims"]
  diab = cc.filter(pl.col("sp_diabetes").is_in(["1", "2"])).select("bene_id")
  n_diab = diab.height
  if n_diab == 0:
    return {
      "n_diabetes": 0,
      "n_with_ip": 0,
      "p_ip_given_diabetes": None,
      "unit": "binary_annual_risk",
    }
  ip_ids = ip.select("bene_id").unique()
  n_ip = diab.join(ip_ids, on="bene_id", how="inner").height
  return {
    "n_diabetes": n_diab,
    "n_with_ip": n_ip,
    "p_ip_given_diabetes": round(n_ip / n_diab, 6),
    "unit": "binary_annual_risk",
  }


def main() -> int:
  finding = load_finding(
    FIXTURES_ROOT
    / "evidence_ir"
    / "lit02_drye_admission_rate_unsupported.json"
  )
  assert finding.finding_id == DRYE_FINDING_ID

  calibrated = _load_tables(PARQUET_DIR / "calibrated_to_a")
  ir_report = execute_finding(finding, calibrated)
  diagnostic = _p_ip_given_diabetes(calibrated)

  exact_refused = (not ir_report.executable) or bool(ir_report.errors)
  payload = {
    "finding_id": finding.finding_id,
    "paper": "Drye et al. Med Care (LIT-02)",
    "evidence_estimate": finding.result.estimate,
    "evidence_unit": finding.result.unit,
    "exact_ir_execution": ir_report.model_dump(mode="json"),
    "exact_estimand_refused": exact_refused,
    "diagnostic_mvp_o1": diagnostic,
    "non_equivalence_gaps": list(finding.comparability.gaps),
    "interpretation": [
      "Drye reports acute *unplanned* admissions per 100 person-years.",
      "MVP O1 is binary all-cause IP claim presence in the reference year.",
      "Do not compare diagnostic P(IP|diabetes) numerically to 41.4/100 PY.",
      "Out-domain under Andes prevalence calibration: utilization free params "
      "were not fit to Drye (and cannot be, given schema gaps).",
      "Synthetic quantities are not Medicare findings.",
    ],
  }
  REPORTS_DIR.mkdir(parents=True, exist_ok=True)
  out = REPORTS_DIR / "out_domain_b.json"
  out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
  print(f"wrote {out}")
  print(
    "B exact refused",
    exact_refused,
    "| diagnostic P(IP|diabetes)",
    diagnostic.get("p_ip_given_diabetes"),
  )
  return 0 if exact_refused else 3


if __name__ == "__main__":
  raise SystemExit(main())
