"""Tests for the preregistered Phase 6 analyst workflow."""

from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import polars as pl
import pytest

from medicare_synth.phase6 import analyze_workflow
from medicare_synth.synthesis import ConditionalWorldParams, generate_diabetes_ip_world


def _tables() -> dict[str, pl.DataFrame]:
  return generate_diabetes_ip_world(ConditionalWorldParams(
    n_beneficiaries=400, seed=11, diabetes_prevalence=0.3, hf_prevalence=0.2,
    p_ip_given_diabetes=0.2, p_ip_given_no_diabetes=0.04,
  )).tables()


def test_claim_duplication_does_not_duplicate_people() -> None:
  tables = _tables()
  result = analyze_workflow(tables)
  duplicated = dict(tables)
  duplicated["inpatient_claims"] = pl.concat([tables["inpatient_claims"]] * 2)
  assert analyze_workflow(duplicated) == result
  assert result["n_eligible"] == 400


def test_reference_year_and_weights() -> None:
  tables = _tables()
  later = dict(tables)
  later["inpatient_claims"] = later["inpatient_claims"].with_columns(
    pl.lit(date(2022, 1, 1)).alias("clm_admsn_dt")
  )
  assert analyze_workflow(later)["ip_risk"] == 0.0
  cc = tables["mbsf_chronic_conditions"]
  weights = cc.select("bene_id", pl.when(pl.col("sp_diabetes") == "1")
                      .then(2.0).otherwise(1.0).alias("weight"))
  raw = analyze_workflow(tables)
  weighted = analyze_workflow(tables, weights=weights)
  assert weighted["diabetes_prevalence"] > raw["diabetes_prevalence"]
  with pytest.raises(ValueError, match="weight"):
    analyze_workflow(tables, weights=weights.slice(1))


def test_committed_phase6_report_retains_protocol_and_gate_evidence() -> None:
  root = Path(__file__).resolve().parents[1]
  report = json.loads((root / "reports/phase6/engineering-evaluation-v1.json").read_text())
  protocol = root / "docs/phase6/protocol-v1.md"
  assert report["protocol_sha256"] == hashlib.sha256(protocol.read_bytes()).hexdigest()
  assert report["producer_commit"].startswith("2f36337")
  assert report["seeds"] == [11, 42, 73]
  assert report["disposition"]["engineering"] == "conditional-go"
  assert report["disposition"]["workflow_utility"] == "conditional-go"
  assert report["disposition"]["independent_fidelity"] == "no-go / insufficient evidence"
  for run in report["runs"]:
    assert run["baseline"]["n_eligible"] == 2000
    assert run["baseline_duplicate_claim_invariant"]
    assert run["background_risk_sensitivity_pass"]
    assert all(check["pass"] for check in run["known_truth"]["checks"].values())
    for world in run["worlds"].values():
      assert world["structural_valid"] and world["calibration_n_missing"] == 0
      assert world["duplicate_claim_invariant"]
      assert world["analyst"]["n_eligible"] == 2000
    weighted = run["worlds"]["mvp-w1-reweight-v2"]
    assert weighted["solver"]["converged"]
    assert all(row["status"] == "matched" and abs(row["absolute_difference"]) <= 1e-6
               for row in weighted["calibration_targets"])
  for path, expected in report["historical_report_sha256"].items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected


def test_runner_refuses_overwrite_and_historical_destination(tmp_path: Path) -> None:
  root = Path(__file__).resolve().parents[1]
  script = root / "scripts/phase6_evaluate_v1.py"
  existing = tmp_path / "existing.json"
  existing.write_text("preserve me")
  for output in (existing, root / "reports/phase5/not-a-new-run.json"):
    result = subprocess.run(
      [sys.executable, str(script), "--output", str(output)], capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "new file" in result.stderr
  assert existing.read_text() == "preserve me"
