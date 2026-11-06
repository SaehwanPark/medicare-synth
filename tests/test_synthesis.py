"""Behavioral tests for Phase 1 conditional synthesizer and benchmarks."""

from __future__ import annotations

from medicare_synth.expansion import HorizontalExpander
from medicare_synth.synthesis import (
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
    "n_beneficiaries": 4000,
    "seed": 2021,
    "diabetes_prevalence": 0.28,
    "p_ip_given_diabetes": 0.35,
    "p_ip_given_no_diabetes": 0.12,
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
  world = generate_diabetes_ip_world(_mvp_params(n_beneficiaries=100, seed=3))
  base = world.mbsf_base_enrollment
  assert (base["bene_hi_cvrage_tot_mons"] == 12).all()
  assert (base["bene_smi_cvrage_tot_mons"] == 12).all()
  assert (base["bene_hmo_cvrage_tot_mons"] == 0).all()
  ages = (
    2021
    - world.beneficiary_summary["bene_birth_dt"].dt.year()
  )
  assert (ages >= 65).all()


def test_primary_relationships_recover_within_tolerance():
  params = _mvp_params()
  world = generate_diabetes_ip_world(params)
  estimates = estimate_world_relationships(world)
  checks = relationships_within_tolerance(
    estimates, params, check_held_out_no_diabetes=True
  )
  assert checks["diabetes_prevalence"]
  assert checks["p_ip_given_diabetes"]
  assert checks["p_ip_given_no_diabetes"]


def test_held_out_relationship_recovers_within_tolerance():
  """R3 P(O1|no diabetes) recovered on holdout partition within tolerance."""
  params = _mvp_params(n_beneficiaries=5000, seed=99)
  world = generate_diabetes_ip_world(params)
  estimation_ids, holdout_ids = split_bene_ids(world, holdout_fraction=0.4)
  assert len(estimation_ids) > 0 and len(holdout_ids) > 0

  # Primary recovery on estimation partition (R1/R2).
  est_part = estimate_world_relationships(world, estimation_ids)
  primary = relationships_within_tolerance(
    est_part, params, check_held_out_no_diabetes=False
  )
  assert primary["diabetes_prevalence"]
  assert primary["p_ip_given_diabetes"]

  # Held-out recovery of R3 on untouched holdout IDs.
  holdout_est = estimate_world_relationships(world, holdout_ids)
  assert (
    abs(holdout_est.p_ip_given_no_diabetes - params.p_ip_given_no_diabetes)
    <= params.recovery_tolerance
  )


def test_conditional_generator_has_full_unique_support():
  world = generate_diabetes_ip_world(_mvp_params(n_beneficiaries=250, seed=5))
  assert unique_support_ratio(world) == 1.0


def test_horizontal_clone_fails_statistical_support_benchmark():
  """Cloning preserves seed prevalence exactly and cannot retarget it.

  A conditional synthesizer targeting a *different* prevalence recovers it;
  clone-only expansion of a mismatched seed cannot.
  """
  seed_world = generate_diabetes_ip_world(
    _mvp_params(
      n_beneficiaries=20,
      seed=11,
      diabetes_prevalence=0.5,
      p_ip_given_diabetes=0.8,
      p_ip_given_no_diabetes=0.1,
    )
  )
  seed_prev = estimate_world_relationships(seed_world).diabetes_prevalence

  expander = HorizontalExpander(seed=11)
  cloned_tables = expander.expand_subgraph(seed_world.tables(), scale_factor=50)
  from medicare_synth.synthesis import ConditionalWorld

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
      n_beneficiaries=1000,
      seed=11,
      diabetes_prevalence=target,
      p_ip_given_diabetes=0.8,
      p_ip_given_no_diabetes=0.1,
    )
  )
  controlled_prev = estimate_world_relationships(controlled).diabetes_prevalence
  assert abs(controlled_prev - target) <= 0.03
  assert unique_support_ratio(controlled) == 1.0


def test_tabdat_adapter_is_not_conditional_on_diabetes():
  """Characterization: index/seed features ignore chronic flags."""
  from medicare_synth.expansion import TabDatSynthAdapter

  world = generate_diabetes_ip_world(_mvp_params(n_beneficiaries=40, seed=8))
  adapter = TabDatSynthAdapter()
  featured = adapter.synthesize_table(
    world.beneficiary_summary, target_columns=["SYN_RISK_SCORE"], seed=8
  )
  featured_again = adapter.synthesize_table(
    world.beneficiary_summary, target_columns=["SYN_RISK_SCORE"], seed=8
  )
  assert featured["SYN_RISK_SCORE"].to_list() == featured_again[
    "SYN_RISK_SCORE"
  ].to_list()
  assert "sp_diabetes" not in featured.columns
