"""Behavioral tests for Phase 4 calibration engine."""

from __future__ import annotations

import pytest

from medicare_synth.calibration import (
  AGENT_ROLE_CONTRACTS,
  AgentRole,
  CalibrationError,
  CalibrationLevel,
  agent_role_contract,
  assert_calibration_partition_only,
  build_run_manifest,
  calibrate_generator_params,
  calibrate_reweight,
  level_a_baseline,
  load_default_corpus,
  structural_valid,
)
from medicare_synth.evidence_corpus import PartitionName
from medicare_synth.synthesis import ConditionalWorldParams, generate_diabetes_ip_world


@pytest.fixture(scope="module")
def corpus_and_path():
  return load_default_corpus()


def test_agent_role_contracts_cover_calibration_operator() -> None:
  assert len(AGENT_ROLE_CONTRACTS) >= 7
  op = agent_role_contract(AgentRole.CALIBRATION_OPERATOR)
  assert any("holdout" in m for m in op.must_not)
  assert any("holdout" in a.lower() for a in op.requires_human_approval)


def test_refuse_fit_on_holdout(corpus_and_path) -> None:
  corpus, _ = corpus_and_path
  holdout_id = corpus.finding_ids(PartitionName.HOLDOUT)[0]
  with pytest.raises(CalibrationError, match="holdout"):
    assert_calibration_partition_only(corpus, [holdout_id])


def test_level_a_baseline_reports_calibration_and_holdout(corpus_and_path) -> None:
  corpus, _ = corpus_and_path
  world = generate_diabetes_ip_world(
    ConditionalWorldParams(
      n_beneficiaries=2000,
      seed=1,
      diabetes_prevalence=0.20,
      p_ip_given_diabetes=0.05,
      p_ip_given_no_diabetes=0.05,
      hf_prevalence=0.05,
    )
  )
  cal, hold = level_a_baseline(world.tables(), corpus)
  assert cal.mean_absolute_error is not None
  assert cal.mean_absolute_error > 0.02
  assert len(cal.rows) == 3
  assert len(hold.rows) == 1


def test_reweight_improves_calibration_mae(corpus_and_path) -> None:
  corpus, path = corpus_and_path
  world = generate_diabetes_ip_world(
    ConditionalWorldParams(
      n_beneficiaries=5000,
      seed=11,
      diabetes_prevalence=0.18,
      p_ip_given_diabetes=0.05,
      p_ip_given_no_diabetes=0.04,
      hf_prevalence=0.04,
    )
  )
  result = calibrate_reweight(world.tables(), corpus)
  assert result.before.mean_absolute_error is not None
  assert result.after.mean_absolute_error is not None
  assert result.after.mean_absolute_error < result.before.mean_absolute_error
  assert result.diagnostics.ess > 0
  assert result.diagnostics.min_weight > 0
  assert result.diagnostics.max_weight >= result.diagnostics.min_weight
  assert result.diagnostics.infeasible is False
  assert result.diagnostics.converged is True
  # Records unchanged: weight frame is separate; row counts match.
  assert result.weights.height == world.beneficiary_summary.height

  manifest = build_run_manifest(
    run_id="test-reweight",
    level=CalibrationLevel.B_REWEIGHT,
    corpus=corpus,
    corpus_path=path,
    seed=11,
    method_hyperparameters={"max_iterations": 40, "tolerance": 1e-6},
    diagnostics=result.diagnostics.model_dump(mode="json"),
    calibration_mae_before=result.before.mean_absolute_error,
    calibration_mae_after=result.after.mean_absolute_error,
    structural_valid_flag=structural_valid(world),
  )
  assert manifest.sha256() == manifest.sha256()
  assert "holdout" in " ".join(manifest.assumptions).lower()


def test_param_calibration_improves_without_using_holdout(corpus_and_path) -> None:
  corpus, path = corpus_and_path
  baseline = ConditionalWorldParams(
    n_beneficiaries=3000,
    seed=42,
    diabetes_prevalence=0.18,
    p_ip_given_diabetes=0.05,
    p_ip_given_no_diabetes=0.04,
    hf_prevalence=0.04,
  )
  result = calibrate_generator_params(
    baseline,
    corpus,
    diabetes_values=(0.18, 0.277, 0.32),
    hf_values=(0.04, 0.12),
    ip_diab_values=(0.05, 0.13),
  )
  assert result.improved_calibration is True
  assert result.fitted.mean_absolute_error is not None
  assert result.baseline.mean_absolute_error is not None
  assert result.fitted.mean_absolute_error < result.baseline.mean_absolute_error
  # Fitted params should move toward calibration magnitudes.
  assert abs(result.fitted_params.diabetes_prevalence - 0.277) <= abs(
    baseline.diabetes_prevalence - 0.277
  )
  fitted_world = generate_diabetes_ip_world(result.fitted_params)
  assert structural_valid(fitted_world)

  # Holdout is reported but was not an optimization target: search_trace MAEs
  # are calibration-only.
  assert all(isinstance(p.calibration_mae, float) for p in result.search_trace)
  manifest = build_run_manifest(
    run_id="test-params",
    level=CalibrationLevel.C_GENERATOR_PARAMS,
    corpus=corpus,
    corpus_path=path,
    seed=42,
    method_hyperparameters={
      "diabetes_values": [0.18, 0.277, 0.32],
      "hf_values": [0.04, 0.12],
      "ip_diab_values": [0.05, 0.13],
    },
    diagnostics={"n_search_points": len(result.search_trace)},
    calibration_mae_before=result.baseline.mean_absolute_error,
    calibration_mae_after=result.fitted.mean_absolute_error,
    holdout_mae_before=result.holdout_baseline.mean_absolute_error,
    holdout_mae_after=result.holdout_fitted.mean_absolute_error,
    structural_valid_flag=True,
    notes=("Holdout MAE reported only; not used in search objective.",),
  )
  assert manifest.holdout_finding_ids
  assert manifest.calibration_mae_after is not None
  assert manifest.calibration_mae_after < manifest.calibration_mae_before


def test_manifest_deterministic_checksum(corpus_and_path) -> None:
  corpus, path = corpus_and_path
  kwargs = dict(
    run_id="det",
    level=CalibrationLevel.A_NONE,
    corpus=corpus,
    corpus_path=path,
    seed=0,
    method_hyperparameters={},
    diagnostics={"ok": True},
    calibration_mae_before=0.1,
    calibration_mae_after=0.1,
  )
  a = build_run_manifest(**kwargs)
  b = build_run_manifest(**kwargs)
  assert a.model_dump() == b.model_dump()
  assert a.sha256() == b.sha256()
