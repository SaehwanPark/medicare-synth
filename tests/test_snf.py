"""Unit test suite for Skilled Nursing Facility (SNF) Claims domain model, validation, scenarios, normalizer, and release pipeline.
"""

from datetime import date
from pathlib import Path

import polars as pl
import pytest
from medicare_synth.models import SkilledNursingFacilityClaimRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import FindingCategory, RelationalValidator, Severity


def test_snf_record_validation():
  """Tests valid SkilledNursingFacilityClaimRecord creation and field bounds."""
  rec = SkilledNursingFacilityClaimRecord(
    clm_id="CLM_S001",
    bene_id="BENE_001",
    clm_admsn_dt=date(2021, 6, 1),
    nch_bene_dschrg_dt=date(2021, 6, 15),
    clm_pmt_amt=8500.0,
    clm_utlztn_day_cnt=14,
    ncvd_days_cnt=0,
  )
  assert rec.clm_id == "CLM_S001"
  assert rec.clm_utlztn_day_cnt == 14

  with pytest.raises(ValueError):
    # Invalid negative utilization days count
    SkilledNursingFacilityClaimRecord(
      clm_id="CLM_ERR",
      bene_id="BENE_001",
      clm_admsn_dt=date(2021, 6, 1),
      nch_bene_dschrg_dt=date(2021, 6, 15),
      clm_utlztn_day_cnt=-1,
    )


def test_relational_validator_snf_field_constraints():
  """Tests RelationalValidator detection of SNF field constraint violations."""
  validator = RelationalValidator()
  bene_df = pl.DataFrame(
    [{"bene_id": "BENE_001", "bene_birth_dt": date(1950, 1, 1), "bene_sex_ident_cd": "1", "bene_race_cd": "1"}]
  )
  snf_df = pl.DataFrame(
    [
      {
        "clm_id": "CLM_ERR",
        "bene_id": "BENE_001",
        "clm_admsn_dt": date(2021, 6, 1),
        "nch_bene_dschrg_dt": date(2021, 6, 15),
        "clm_pmt_amt": 8500.0,
        "clm_utlztn_day_cnt": -5,
        "ncvd_days_cnt": 0,
      }
    ]
  )

  report = validator.validate_slice(bene_df=bene_df, snf_df=snf_df)
  assert not report.is_valid
  assert len(report.findings) == 1
  finding = report.findings[0]
  assert finding.rule_id == "FLD-002"
  assert finding.category == FindingCategory.FIELD
  assert finding.severity == Severity.HIGH


def test_scenario_compiler_invalid_snf_utilization_days():
  """Tests ScenarioCompiler compilation of invalid_snf_utilization_days scenario."""
  slice_data = ScenarioCompiler.get_scenario("invalid_snf_utilization_days")
  validator = RelationalValidator()
  report = validator.validate_slice(
    bene_df=slice_data.bene_df,
    carrier_df=slice_data.carrier_df,
    outpatient_df=slice_data.outpatient_df,
    inpatient_df=slice_data.inpatient_df,
    pde_df=slice_data.pde_df,
    snf_df=slice_data.snf_df,
  )

  assert not report.is_valid
  rule_ids = [f.rule_id for f in report.findings]
  assert "FLD-002" in rule_ids


def test_baseline_normalizer_snf():
  """Tests BaselineNormalizer normalization of raw SNF claim dictionaries."""
  records = [
    {
      "clm_id": "CLM_S100",
      "bene_id": "BENE_100",
      "clm_admsn_dt": date(2021, 6, 1),
      "nch_bene_dschrg_dt": date(2021, 6, 10),
      "clm_pmt_amt": 5000.0,
      "clm_utlztn_day_cnt": 9,
      "ncvd_days_cnt": 0,
    }
  ]
  df = BaselineNormalizer.normalize_snf_claims(records)
  assert df.height == 1
  assert "clm_admsn_dt" in df.columns
  assert df.schema["clm_pmt_amt"] == pl.Float64


def test_release_exporter_snf(tmp_path: Path):
  """Tests ReleaseExporter export including SNF claims table."""
  slice_data = ScenarioCompiler.get_scenario("valid_baseline_cohort")
  exporter = ReleaseExporter(output_dir=tmp_path, release_id="test_snf_release")
  manifest = exporter.export_slice(
    bene_df=slice_data.bene_df,
    carrier_df=slice_data.carrier_df,
    outpatient_df=slice_data.outpatient_df,
    fmt="csv",
    inpatient_df=slice_data.inpatient_df,
    pde_df=slice_data.pde_df,
    snf_df=slice_data.snf_df,
  )

  assert manifest.validation_passed
  assert "snf_csv" in manifest.files
  assert (tmp_path / "snf.csv").exists()
