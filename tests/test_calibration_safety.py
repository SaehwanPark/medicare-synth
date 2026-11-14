"""Regression contracts for calibrated selection, solver and weights."""

from __future__ import annotations

import polars as pl
import pytest

import medicare_synth.calibration as calibration
from medicare_synth.calibration import (
  CalibrationError,
  calibrate_generator_params,
  calibrate_reweight,
  discrepancy_for_findings,
  load_default_corpus,
)
from medicare_synth.evidence_corpus import PartitionName, load_partition_findings
from medicare_synth.synthesis import ConditionalWorldParams, generate_diabetes_ip_world
from medicare_synth.worlds import default_baseline_params


def test_one_sweep_does_not_claim_false_convergence() -> None:
  corpus, _ = load_default_corpus()
  world = generate_diabetes_ip_world(default_baseline_params(n_beneficiaries=6000, seed=42))
  result = calibrate_reweight(world.tables(), corpus, max_iterations=1, tolerance=1e-6)
  assert any(abs(r.absolute_difference or 0.0) > 1e-6 for r in result.after.rows)
  assert result.diagnostics.converged is False
  assert not result.diagnostics.infeasible


def test_incomplete_candidate_cannot_win() -> None:
  corpus, _ = load_default_corpus()
  base = ConditionalWorldParams(
    n_beneficiaries=80, seed=3, diabetes_prevalence=0.42,
    hf_prevalence=0.25, p_ip_given_diabetes=0.85, p_ip_given_no_diabetes=0.04,
  )
  result = calibrate_generator_params(
    base, corpus, diabetes_values=(0.0, 0.42), hf_values=(0.12,), ip_diab_values=(0.85,)
  )
  assert result.fitted_params.diabetes_prevalence != 0.0
  assert any(not point.eligible for point in result.search_trace)


def test_fit_never_loads_holdout_or_diagnostic(monkeypatch: pytest.MonkeyPatch) -> None:
  corpus, _ = load_default_corpus()
  original = calibration.load_partition_findings

  def calibration_only(corpus, partition, **kwargs):
    assert partition == PartitionName.CALIBRATION
    return original(corpus, partition, **kwargs)

  monkeypatch.setattr(calibration, "load_partition_findings", calibration_only)
  result = calibrate_generator_params(
    default_baseline_params(n_beneficiaries=500, seed=42), corpus,
    diabetes_values=(0.277,), hf_values=(0.12,), ip_diab_values=(0.13,),
  )
  assert result.fitted_params


@pytest.mark.parametrize("defect", ["missing", "duplicate", "nan", "inf", "negative", "extra"])
def test_invalid_weights_are_never_silently_joined(defect: str) -> None:
  corpus, _ = load_default_corpus()
  world = generate_diabetes_ip_world(default_baseline_params(n_beneficiaries=100, seed=42))
  tables = world.tables()
  findings = load_partition_findings(corpus, PartitionName.CALIBRATION)
  weights = tables["beneficiary_summary"].select("bene_id").with_columns(pl.lit(1.0).alias("weight"))
  if defect == "missing":
    weights = weights.slice(1)
  elif defect == "duplicate":
    weights = pl.concat([weights, weights.head(1)])
  elif defect == "extra":
    weights = pl.concat([weights, pl.DataFrame({"bene_id": ["extra"], "weight": [1.0]})])
  else:
    bad = {"nan": float("nan"), "inf": float("inf"), "negative": -1.0}[defect]
    weights = weights.with_row_index().with_columns(
      pl.when(pl.col("index") == 0).then(pl.lit(bad)).otherwise(pl.col("weight")).alias("weight")
    ).drop("index")
  with pytest.raises(CalibrationError, match="weight"):
    discrepancy_for_findings(tables, findings, partition=PartitionName.CALIBRATION, weights=weights)
