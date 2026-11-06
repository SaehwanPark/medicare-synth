"""Behavioral tests for Phase 1 conditional synthesizer and benchmarks."""

from __future__ import annotations

import pytest

from medicare_synth.expansion import HorizontalExpander, TabDatSynthAdapter
from medicare_synth.synthesis import (
  ConditionalWorld,
  ConditionalWorldParams,
  estimate_world_relationships,
  generate_diabetes_ip_world,
  relationships_within_tolerance,
  split_bene_ids,
  unique_support_ratio,
)
from medicare_synth.validation import RelationalValidator


def _mvp_params(**overrides: object) -> ConditionalWorldParams:
  base: dict[str, object] = {
    "n_beneficiaries": 8000,
    "seed": 2021,
    "diabetes_prevalence": 0.28,
    "p_ip_given_diabetes": 0.35,
    "p_ip_given_no_diabetes": 0.12,
    "hf_prevalence": 0.1,
    "recovery_tolerance": 0.03,
  }
  base.update(overrides)
  return ConditionalWorldParams.model_validate(base)


def test_generate_world_is_deterministic():
  params = _mvp_params(n_beneficiaries=200)
  a = generate_diabetes_ip_world(params)
  b = generate_diabetes_ip_world(params)
  assert a.beneficiary_summary.equals(b.beneficiary_summary)
  assert a.mbsf_chronic_conditions.equals(b.mbsf_chronic_conditions)
  assert a.inpatient_claims.equals(b.inpatient_claims)
  assert a.mbsf_base_enrollment.equals(b.mbsf_base_enrollment)


def test_different_seeds_change_outputs():
  a = generate_diabetes_ip_world(_mvp_params(n_beneficiaries=300, seed=1))
  b = generate_diabetes_ip_world(_mvp_params(n_beneficiaries=300, seed=2))
  assert not a.mbsf_chronic_conditions.equals(b.mbsf_chronic_conditions)


def test_generated_world_passes_structural_validation():
  world = generate_diabetes_ip_world(_mvp_params(n_beneficiaries=500, seed=7))
  report = RelationalValidator().validate_slice(
    bene_df=world.beneficiary_summary,
    inpatient_df=world.inpatient_claims,
    mbsf_cc_df=world.mbsf_chronic_conditions,
    mbsf_base_df=world.mbsf_base_enrollment,
  )
  assert report.is_valid, [f.message for f in report.findings]


def test_option_b_enrollment_and_age_floor():
  world = generate_diabetes_ip_world(
    _mvp_params(n_beneficiaries=100, seed=3, reference_year=2021)
  )
  base = world.mbsf_base_enrollment
  assert (base["bene_hi_cvrage_tot_mons"] == 12).all()
  assert (base["bene_smi_cvrage_tot_mons"] == 12).all()
  assert (base["bene_hmo_cvrage_tot_mons"] == 0).all()
  ages = (
    world.params.reference_year
    - world.beneficiary_summary["bene_birth_dt"].dt.year()
  )
  assert (ages >= 65).all()


def test_hf_prevalence_controllable():
  world = generate_diabetes_ip_world(
    _mvp_params(n_beneficiaries=5000, seed=4, hf_prevalence=0.2)
  )
  cc = world.mbsf_chronic_conditions
  rate = cc.filter(cc["sp_chf"].is_in(["1", "2"])).height / cc.height
  assert abs(rate - 0.2) <= 0.03


def test_primary_relationships_recover_within_tolerance():
  params = _mvp_params()
  world = generate_diabetes_ip_world(params)
  estimates = estimate_world_relationships(world)
  checks = relationships_within_tolerance(
    estimates, params, check_held_out_no_diabetes=True
  )
  assert all(checks.values()), checks


def test_recovery_across_multiple_seeds():
  """Contract gate must hold across seeds, not a single lucky draw."""
  failures = 0
  for seed in range(20):
    params = _mvp_params(seed=seed, n_beneficiaries=8000)
    world = generate_diabetes_ip_world(params)
    checks = relationships_within_tolerance(
      estimate_world_relationships(world),
      params,
      check_held_out_no_diabetes=True,
    )
    if not all(checks.values()):
      failures += 1
  assert failures == 0, f"recovery failed for {failures}/20 seeds"


def test_held_out_relationship_recovers_within_tolerance():
  """R3 recovered on holdout partition (LLN on known truth, not model fit)."""
  params = _mvp_params(n_beneficiaries=10000, seed=99)
  world = generate_diabetes_ip_world(params)
  estimation_ids, holdout_ids = split_bene_ids(world, holdout_fraction=0.4)

  est_part = estimate_world_relationships(world, estimation_ids)
  primary = relationships_within_tolerance(
    est_part, params, check_held_out_no_diabetes=False
  )
  assert primary["diabetes_prevalence"]
  assert primary["p_ip_given_diabetes"]

  holdout_est = estimate_world_relationships(world, holdout_ids)
  holdout_checks = relationships_within_tolerance(
    holdout_est, params, check_held_out_no_diabetes=True
  )
  assert holdout_checks["p_ip_given_no_diabetes"]


def test_empty_bene_ids_returns_zero_estimates():
  world = generate_diabetes_ip_world(_mvp_params(n_beneficiaries=50, seed=1))
  est = estimate_world_relationships(world, [])
  assert est.n_beneficiaries == 0
  assert est.diabetes_prevalence == 0.0


def test_empty_stratum_fails_tolerance_not_false_pass():
  params = _mvp_params(
    n_beneficiaries=200,
    seed=2,
    diabetes_prevalence=1.0,
    p_ip_given_no_diabetes=0.5,
  )
  world = generate_diabetes_ip_world(params)
  checks = relationships_within_tolerance(
    estimate_world_relationships(world),
    params,
    check_held_out_no_diabetes=True,
  )
  assert checks["p_ip_given_no_diabetes"] is False


def test_split_requires_nonempty_partitions():
  world = generate_diabetes_ip_world(_mvp_params(n_beneficiaries=2, seed=0))
  with pytest.raises(ValueError, match="empty partition"):
    split_bene_ids(world, holdout_fraction=0.4)


def test_conditional_generator_has_full_unique_support():
  world = generate_diabetes_ip_world(_mvp_params(n_beneficiaries=250, seed=5))
  assert unique_support_ratio(world) == 1.0


def test_horizontal_clone_fails_statistical_support_benchmark():
  """Cloning preserves seed prevalence exactly and cannot retarget it."""
  seed_world = generate_diabetes_ip_world(
    _mvp_params(
      n_beneficiaries=20,
      seed=11,
      diabetes_prevalence=0.5,
      p_ip_given_diabetes=0.8,
      p_ip_given_no_diabetes=0.1,
      hf_prevalence=0.0,
    )
  )
  seed_prev = estimate_world_relationships(seed_world).diabetes_prevalence

  expander = HorizontalExpander(seed=11)
  cloned_tables = expander.expand_subgraph(seed_world.tables(), scale_factor=50)
  cloned = ConditionalWorld(
    params=seed_world.params,
    beneficiary_summary=cloned_tables["beneficiary_summary"],
    mbsf_base_enrollment=cloned_tables["mbsf_base_enrollment"],
    mbsf_chronic_conditions=cloned_tables["mbsf_chronic_conditions"],
    inpatient_claims=cloned_tables["inpatient_claims"],
  )
  cloned_prev = estimate_world_relationships(cloned).diabetes_prevalence
  assert abs(cloned_prev - seed_prev) < 1e-12
  target = 0.2
  assert abs(cloned_prev - target) > 0.15

  controlled = generate_diabetes_ip_world(
    _mvp_params(
      n_beneficiaries=2000,
      seed=11,
      diabetes_prevalence=target,
      p_ip_given_diabetes=0.8,
      p_ip_given_no_diabetes=0.1,
    )
  )
  controlled_prev = estimate_world_relationships(controlled).diabetes_prevalence
  assert abs(controlled_prev - target) <= 0.03
  assert unique_support_ratio(controlled) == 1.0


def test_tabdat_adapter_ignores_diabetes_column_values():
  """Builtin TabDat features are index/seed math even if CC flags are present."""
  import polars as pl

  world = generate_diabetes_ip_world(_mvp_params(n_beneficiaries=40, seed=8))
  with_flag = world.beneficiary_summary.join(
    world.mbsf_chronic_conditions.select(["bene_id", "sp_diabetes"]),
    on="bene_id",
  )
  adapter = TabDatSynthAdapter()
  featured = adapter.synthesize_table(
    with_flag, target_columns=["SYN_RISK_SCORE"], seed=8
  )
  flipped = with_flag.with_columns(
    pl.when(pl.col("sp_diabetes") == "0")
    .then(pl.lit("1"))
    .otherwise(pl.lit("0"))
    .alias("sp_diabetes")
  )
  featured_flipped = adapter.synthesize_table(
    flipped, target_columns=["SYN_RISK_SCORE"], seed=8
  )
  assert featured["SYN_RISK_SCORE"].to_list() == featured_flipped[
    "SYN_RISK_SCORE"
  ].to_list()
