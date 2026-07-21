"""Behavioral tests for ScenarioCompiler."""

import pytest
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator, Severity


def test_valid_baseline_cohort_compilation():
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  assert slice_data.bene_df.height == 3
  assert slice_data.carrier_df.height == 2
  assert slice_data.outpatient_df.height == 2

  validator = RelationalValidator()
  report = validator.validate_slice(
    bene_df=slice_data.bene_df,
    carrier_df=slice_data.carrier_df,
    outpatient_df=slice_data.outpatient_df,
  )
  assert report.is_valid is True
  assert len(report.findings) == 0


def test_invalid_orphaned_claim_compilation():
  slice_data = ScenarioCompiler.invalid_orphaned_claim()
  validator = RelationalValidator()
  report = validator.validate_slice(
    bene_df=slice_data.bene_df,
    carrier_df=slice_data.carrier_df,
    outpatient_df=slice_data.outpatient_df,
  )
  assert report.is_valid is False
  assert any(f.rule_id == "REL-001" and f.severity == Severity.CRITICAL for f in report.findings)


def test_invalid_temporal_inversion_compilation():
  slice_data = ScenarioCompiler.invalid_temporal_inversion()
  validator = RelationalValidator()
  report = validator.validate_slice(
    bene_df=slice_data.bene_df,
    carrier_df=slice_data.carrier_df,
    outpatient_df=slice_data.outpatient_df,
  )
  assert report.is_valid is False
  assert any(f.rule_id == "TMP-001" and f.severity == Severity.HIGH for f in report.findings)


def test_get_scenario_invalid_name():
  with pytest.raises(ValueError, match="Unknown scenario name"):
    ScenarioCompiler.get_scenario("non_existent_scenario")
