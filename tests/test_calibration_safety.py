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
  evaluate_frozen_params,
  load_default_corpus,
)
from medicare_synth.evidence_corpus import PartitionName, load_partition_findings
from medicare_synth.synthesis import ConditionalWorldParams, generate_diabetes_ip_world
from medicare_synth.worlds import default_baseline_params


def test_reweight_is_deterministic_across_polars_thread_counts() -> None:
  import os
  import subprocess
  import sys

  code = """
import hashlib, json
from medicare_synth.calibration import calibrate_reweight, load_default_corpus
from medicare_synth.synthesis import generate_diabetes_ip_world
from medicare_synth.worlds import default_baseline_params
corpus, _ = load_default_corpus()
world = generate_diabetes_ip_world(default_baseline_params(n_beneficiaries=6000, seed=42))
result = calibrate_reweight(world.tables(), corpus)
payload = {'weights': result.weights.sort('bene_id').to_dicts(),
           'after': result.after.model_dump(mode='json'),
           'diagnostics': result.diagnostics.model_dump(mode='json')}
print(hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest())
"""
  hashes = [
    subprocess.check_output(
      [sys.executable, "-c", code],
      env={**os.environ, "POLARS_MAX_THREADS": str(threads)}, text=True,
    ).strip()
    for threads in (1, 4)
  ]
  assert hashes[0] == hashes[1]


def test_one_sweep_does_not_claim_false_convergence() -> None:
  corpus, _ = load_default_corpus()
  world = generate_diabetes_ip_world(default_baseline_params(n_beneficiaries=6000, seed=42))
  result = calibrate_reweight(world.tables(), corpus, max_iterations=1, tolerance=1e-6)
  assert any(abs(r.absolute_difference or 0.0) > 1e-6 for r in result.after.rows)
  assert result.diagnostics.converged is False
  assert not result.diagnostics.infeasible
  assert result.diagnostics.solve_status == "exhausted"


def test_convergence_checks_every_final_residual() -> None:
  corpus, _ = load_default_corpus()
  world = generate_diabetes_ip_world(default_baseline_params(n_beneficiaries=6000, seed=42))
  result = calibrate_reweight(world.tables(), corpus, max_iterations=40, tolerance=1e-6)
  assert result.diagnostics.converged
  assert result.diagnostics.solve_status == "converged"
  assert all(row.status == "matched" and row.absolute_difference is not None
             and abs(row.absolute_difference) <= 1e-6 for row in result.after.rows)


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
  rejected = next(point for point in result.search_trace if not point.eligible)
  assert rejected.calibration_mae is None
  assert rejected.n_missing == 1
  assert any(row.status == "undefined" and row.reason for row in rejected.targets)


def test_fixed_background_override_cannot_select_an_incompatible_baseline() -> None:
  corpus, _ = load_default_corpus()
  base = ConditionalWorldParams(
    n_beneficiaries=1000, seed=42, diabetes_prevalence=0.277,
    hf_prevalence=0.12, p_ip_given_diabetes=0.13, p_ip_given_no_diabetes=0.04,
  )
  result = calibrate_generator_params(
    base, corpus, diabetes_values=(0.8,), hf_values=(0.8,), ip_diab_values=(0.8,),
    p_ip_given_no_diabetes=0.8,
  )
  assert result.fitted_params.p_ip_given_no_diabetes == 0.8
  assert result.fitted_params.diabetes_prevalence == 0.8


def test_nonfinite_target_is_unsupported() -> None:
  corpus, _ = load_default_corpus()
  finding = load_partition_findings(corpus, PartitionName.CALIBRATION)[0]
  bad = finding.model_copy(update={"result": finding.result.model_copy(update={"estimate": float("nan")})})
  world = generate_diabetes_ip_world(default_baseline_params(n_beneficiaries=100, seed=42))
  report = discrepancy_for_findings(world.tables(), [bad], partition=PartitionName.CALIBRATION)
  assert report.n_missing == 1
  assert report.mean_absolute_error is None
  assert report.rows[0].status == "unsupported"
  assert report.rows[0].reason and "finite" in report.rows[0].reason


def test_no_complete_candidate_refuses_selection() -> None:
  corpus, _ = load_default_corpus()
  base = default_baseline_params(n_beneficiaries=100, seed=42).model_copy(
    update={"diabetes_prevalence": 0.0}
  )
  with pytest.raises(CalibrationError, match="no candidate"):
    calibrate_generator_params(
      base, corpus, diabetes_values=(0.0,), hf_values=(0.12,), ip_diab_values=(0.13,)
    )


def test_changed_evaluation_entries_do_not_change_fit(tmp_path) -> None:
  import json
  import shutil
  from medicare_synth.evidence_corpus import sha256_file
  from medicare_synth.evidence_ir import package_fixtures_dir

  corpus, _ = load_default_corpus()
  root = tmp_path / "fixtures"
  shutil.copytree(package_fixtures_dir().parent, root)
  entries = []
  for entry in corpus.entries:
    if entry.partition in (PartitionName.HOLDOUT, PartitionName.DIAGNOSTIC):
      path = root / entry.relative_path
      raw = json.loads(path.read_text())
      raw["result"]["estimate"] = 0.999
      path.write_text(json.dumps(raw))
      entry = entry.model_copy(update={"sha256": sha256_file(path)})
    entries.append(entry)
  changed = corpus.model_copy(update={"entries": tuple(entries)})
  params = default_baseline_params(n_beneficiaries=300, seed=42)
  original = calibrate_generator_params(
    params, corpus, diabetes_values=(0.277,), hf_values=(0.12,), ip_diab_values=(0.13,)
  )
  modified = calibrate_generator_params(
    params, changed, fixtures_root=root,
    diabetes_values=(0.277,), hf_values=(0.12,), ip_diab_values=(0.13,)
  )
  assert original.fitted_params == modified.fitted_params
  assert original.fitted == modified.fitted


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


def test_changed_frozen_candidate_is_refused_before_holdout(monkeypatch: pytest.MonkeyPatch) -> None:
  corpus, _ = load_default_corpus()
  result = calibrate_generator_params(
    default_baseline_params(n_beneficiaries=500, seed=42), corpus,
    diabetes_values=(0.277,), hf_values=(0.12,), ip_diab_values=(0.13,),
  )
  changed = result.model_copy(update={"fitted_params": result.fitted_params.model_copy(
    update={"diabetes_prevalence": 0.0}
  )})
  original = calibration.load_partition_findings
  def no_holdout(corpus, partition, **kwargs):
    assert partition == PartitionName.CALIBRATION
    return original(corpus, partition, **kwargs)
  monkeypatch.setattr(calibration, "load_partition_findings", no_holdout)
  with pytest.raises(CalibrationError, match="frozen candidate"):
    evaluate_frozen_params(changed, corpus)


@pytest.mark.parametrize("defect", ["missing", "duplicate", "nan", "inf", "negative", "extra", "null", "overflow"])
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
  elif defect == "overflow":
    weights = weights.with_columns(pl.lit(1e308).alias("weight"))
  else:
    bad = {"nan": float("nan"), "inf": float("inf"), "negative": -1.0, "null": None}[defect]
    weights = weights.with_row_index().with_columns(
      pl.when(pl.col("index") == 0).then(pl.lit(bad)).otherwise(pl.col("weight")).alias("weight")
    ).drop("index")
  with pytest.raises(CalibrationError, match="weight"):
    discrepancy_for_findings(tables, findings, partition=PartitionName.CALIBRATION, weights=weights)


def test_unsupported_required_target_reports_complete_coverage(
  monkeypatch: pytest.MonkeyPatch,
) -> None:
  from medicare_synth.calibration import TargetCoverageError

  corpus, _ = load_default_corpus()
  original = calibration.load_corpus_finding
  target_id = corpus.finding_ids(PartitionName.CALIBRATION)[0]
  def incompatible(corpus, finding_id, **kwargs):
    finding = original(corpus, finding_id, **kwargs)
    if finding_id == target_id:
      return finding.model_copy(update={"analysis": finding.analysis.model_copy(
        update={"estimator": "logistic_regression"}
      )})
    return finding
  monkeypatch.setattr(calibration, "load_corpus_finding", incompatible)
  world = generate_diabetes_ip_world(default_baseline_params(n_beneficiaries=100, seed=42))
  with pytest.raises(TargetCoverageError) as error:
    calibrate_reweight(world.tables(), corpus)
  assert len(error.value.rows) == len(corpus.finding_ids(PartitionName.CALIBRATION))
  bad = next(row for row in error.value.rows if row.finding_id == target_id)
  assert bad.status == "unsupported" and bad.reason and "ESTIMATOR" in bad.reason


def test_partial_score_is_diagnostic_only() -> None:
  corpus, _ = load_default_corpus()
  params = default_baseline_params(n_beneficiaries=100, seed=42).model_copy(
    update={"diabetes_prevalence": 0.0}
  )
  findings = load_partition_findings(corpus, PartitionName.CALIBRATION)
  report = discrepancy_for_findings(
    generate_diabetes_ip_world(params).tables(), findings, partition=PartitionName.CALIBRATION
  )
  assert report.n_missing == 1
  assert report.mean_absolute_error is None
  assert report.diagnostic_subset_mae is not None
  assert any(row.status == "undefined" and row.reason for row in report.rows)


def test_reweight_refuses_subset_of_approved_targets() -> None:
  corpus, _ = load_default_corpus()
  world = generate_diabetes_ip_world(default_baseline_params(n_beneficiaries=100, seed=42))
  with pytest.raises(CalibrationError, match="all approved"):
    calibrate_reweight(world.tables(), corpus, finding_ids=corpus.finding_ids(PartitionName.CALIBRATION)[:1])


def test_zero_discrepancy_is_complete_not_missing() -> None:
  from medicare_synth.calibration import DiscrepancyReport, DiscrepancyRow

  row = DiscrepancyRow(
    finding_id="zero", evidence_estimate=0.0, synthetic_estimate=0.0,
    absolute_difference=0.0, partition=PartitionName.CALIBRATION,
  )
  report = DiscrepancyReport.from_rows([row])
  assert report.n_missing == 0
  assert report.mean_absolute_error == 0.0
  assert report.diagnostic_subset_mae == 0.0
