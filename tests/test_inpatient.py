"""Unit test suite for Inpatient Claims domain model, validation, scenarios, normalizer, and release pipeline.
"""

from datetime import date
from pathlib import Path

import polars as pl
import pytest
from medicare_synth.models import InpatientClaimHeaderRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import FindingCategory, RelationalValidator, Severity


def test_inpatient_record_validation():
  """Tests valid InpatientClaimHeaderRecord creation and field bounds."""
  rec = InpatientClaimHeaderRecord(
    clm_id="CLM_I001",
    bene_id="BENE_001",
    clm_admsn_dt=date(2021, 5, 10),
    nch_bene_dschrg_dt=date(2021, 5, 15),
    clm_pmt_amt=4500.0,
    clm_utlztn_day_cnt=5,
    clm_drg_cd="291",
  )
  assert rec.clm_id == "CLM_I001"
  assert rec.clm_utlztn_day_cnt == 5

  with pytest.raises(ValueError):
    # Invalid negative payment amount
    InpatientClaimHeaderRecord(
      clm_id="CLM_ERR",
      bene_id="BENE_001",
      clm_admsn_dt=date(2021, 5, 10),
      nch_bene_dschrg_dt=date(2021, 5, 15),
      clm_pmt_amt=-100.0,
    )


def test_relational_validator_inpatient_admission_inversion():
  """Tests RelationalValidator detection of inpatient admission temporal inversion."""
  validator = RelationalValidator()
  bene_df = pl.DataFrame(
    [{"bene_id": "BENE_001", "bene_birth_dt": date(1950, 1, 1), "bene_sex_ident_cd": "1", "bene_race_cd": "1"}]
  )
  inpatient_df = pl.DataFrame(
    [
      {
        "clm_id": "CLM_ERR",
        "bene_id": "BENE_001",
        "clm_admsn_dt": date(2021, 5, 20),
        "nch_bene_dschrg_dt": date(2021, 5, 10),
        "clm_pmt_amt": 1000.0,
        "clm_utlztn_day_cnt": 1,
      }
    ]
  )

  report = validator.validate_slice(bene_df=bene_df, inpatient_df=inpatient_df)
  assert not report.is_valid
  assert len(report.findings) == 1
  finding = report.findings[0]
  assert finding.rule_id == "TMP-002"
  assert finding.category == FindingCategory.TEMPORAL
  assert finding.severity == Severity.HIGH


def test_scenario_compiler_invalid_inpatient_admission():
  """Tests ScenarioCompiler compilation of invalid_inpatient_admission scenario."""
  slice_data = ScenarioCompiler.get_scenario("invalid_inpatient_admission")
  validator = RelationalValidator()
  report = validator.validate_slice(
    bene_df=slice_data.bene_df,
    carrier_df=slice_data.carrier_df,
    outpatient_df=slice_data.outpatient_df,
    inpatient_df=slice_data.inpatient_df,
  )

  assert not report.is_valid
  rule_ids = [f.rule_id for f in report.findings]
  assert "TMP-002" in rule_ids


def test_baseline_normalizer_inpatient():
  """Tests BaselineNormalizer normalization of raw inpatient claim dictionaries."""
  records = [
    {
      "clm_id": "CLM_I100",
      "bene_id": "BENE_100",
      "clm_admsn_dt": date(2021, 1, 1),
      "nch_bene_dschrg_dt": date(2021, 1, 3),
      "clm_pmt_amt": 2500.0,
      "clm_utlztn_day_cnt": 2,
      "clm_drg_cd": "100",
    }
  ]
  df = BaselineNormalizer.normalize_inpatient_claims(records)
  assert df.height == 1
  assert "clm_admsn_dt" in df.columns
  assert df.schema["clm_pmt_amt"] == pl.Float64


def test_release_exporter_inpatient(tmp_path: Path):
  """Tests ReleaseExporter export including inpatient claims table."""
  slice_data = ScenarioCompiler.get_scenario("valid_baseline_cohort")
  exporter = ReleaseExporter(output_dir=tmp_path, release_id="test_inpatient_release")
  manifest = exporter.export_slice(
    bene_df=slice_data.bene_df,
    carrier_df=slice_data.carrier_df,
    outpatient_df=slice_data.outpatient_df,
    fmt="csv",
    inpatient_df=slice_data.inpatient_df,
  )

  assert manifest.validation_passed
  assert "inpatient_csv" in manifest.files
  assert (tmp_path / "inpatient.csv").exists()
