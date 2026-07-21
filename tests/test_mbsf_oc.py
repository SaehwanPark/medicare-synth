"""Unit tests for Master Beneficiary Summary File (MBSF) Other Chronic Conditions Segment domain extension."""

from pathlib import Path
from tempfile import TemporaryDirectory

import polars as pl
import pytest
from pydantic import ValidationError

from medicare_synth.cli import main as cli_main
from medicare_synth.models import MBSFOtherChronicConditionsRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import FindingCategory, RelationalValidator, Severity


def test_mbsf_oc_model_validation():
  """Tests Pydantic validation for MBSFOtherChronicConditionsRecord."""
  rec = MBSFOtherChronicConditionsRecord(
    bene_id="BENE_OC_001",
    rfrnc_yr=2021,
    sp_arthglau="1",
    sp_asthma="2",
    sp_atrialf="1",
    sp_hyperl="1",
    sp_hypert="1",
    sp_hypot="2",
    sp_osteop="2",
    val_mbsf_oc_01=1.0,
  )
  assert rec.bene_id == "BENE_OC_001"
  assert rec.sp_arthglau == "1"
  assert rec.sp_asthma == "2"

  with pytest.raises(ValidationError):
    MBSFOtherChronicConditionsRecord(bene_id="BENE_EXCEED_LIMIT_99999999")


def test_mbsf_oc_normalizer():
  """Tests BaselineNormalizer.normalize_mbsf_oc."""
  raw_records = [
    {
      "bene_id": "BENE_001",
      "rfrnc_yr": 2021,
      "sp_arthglau": "1",
      "sp_asthma": "1",
      "sp_atrialf": "2",
      "sp_hyperl": "1",
      "sp_hypert": "1",
      "sp_hypot": "2",
      "sp_osteop": "2",
      "val_mbsf_oc_01": 1.0,
    }
  ]
  df = BaselineNormalizer.normalize_mbsf_oc(raw_records)
  assert isinstance(df, pl.DataFrame)
  assert df.height == 1
  assert "sp_arthglau" in df.columns
  assert df.schema["sp_arthglau"] == pl.String
  assert df.schema["val_mbsf_oc_01"] == pl.Float64


def test_mbsf_oc_field_constraints_validation():
  """Tests RelationalValidator.check_mbsf_oc_field_constraints for valid and invalid records."""
  valid_df = pl.DataFrame(
    [
      {
        "bene_id": "BENE_001",
        "rfrnc_yr": 2021,
        "sp_arthglau": "1",
        "sp_asthma": "2",
        "sp_atrialf": "1",
        "sp_hyperl": "1",
        "sp_hypert": "1",
        "sp_hypot": "2",
        "sp_osteop": "2",
        "val_mbsf_oc_01": 1.0,
      }
    ]
  )
  findings = RelationalValidator.check_mbsf_oc_field_constraints(valid_df)
  assert len(findings) == 0

  invalid_df = pl.DataFrame(
    [
      {
        "bene_id": "BENE_001",
        "rfrnc_yr": 2021,
        "sp_arthglau": "9",  # Invalid indicator
        "sp_asthma": "1",
        "sp_atrialf": "2",
        "sp_hyperl": "1",
        "sp_hypert": "1",
        "sp_hypot": "2",
        "sp_osteop": "2",
        "val_mbsf_oc_01": 1.0,
      }
    ]
  )
  findings = RelationalValidator.check_mbsf_oc_field_constraints(invalid_df)
  assert len(findings) == 1
  assert findings[0].rule_id == "FLD-010"
  assert findings[0].severity == Severity.HIGH
  assert findings[0].category == FindingCategory.FIELD


def test_invalid_mbsf_other_chronic_condition_indicator_scenario():
  """Tests anomaly scenario compilation and validation for invalid indicator value."""
  slice_data = ScenarioCompiler.get_scenario("invalid_mbsf_other_chronic_condition_indicator")
  assert slice_data.mbsf_oc_df.height == 1

  validator = RelationalValidator()
  report = validator.validate_slice(
    bene_df=slice_data.bene_df,
    carrier_df=slice_data.carrier_df,
    outpatient_df=slice_data.outpatient_df,
    inpatient_df=slice_data.inpatient_df,
    pde_df=slice_data.pde_df,
    snf_df=slice_data.snf_df,
    hha_df=slice_data.hha_df,
    dme_df=slice_data.dme_df,
    hospice_df=slice_data.hospice_df,
    mbsf_cc_df=slice_data.mbsf_cc_df,
    mbsf_cu_df=slice_data.mbsf_cu_df,
    mbsf_d_df=slice_data.mbsf_d_df,
    mbsf_base_df=slice_data.mbsf_base_df,
    mbsf_oc_df=slice_data.mbsf_oc_df,
  )
  assert not report.is_valid
  assert any(f.rule_id == "FLD-010" for f in report.findings)


def test_mbsf_oc_release_export():
  """Tests ReleaseExporter inclusion of mbsf_oc table."""
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  with TemporaryDirectory() as tmpdir:
    exporter = ReleaseExporter(output_dir=Path(tmpdir))
    manifest = exporter.export_slice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=slice_data.outpatient_df,
      inpatient_df=slice_data.inpatient_df,
      pde_df=slice_data.pde_df,
      snf_df=slice_data.snf_df,
      hha_df=slice_data.hha_df,
      dme_df=slice_data.dme_df,
      hospice_df=slice_data.hospice_df,
      mbsf_cc_df=slice_data.mbsf_cc_df,
      mbsf_cu_df=slice_data.mbsf_cu_df,
      mbsf_d_df=slice_data.mbsf_d_df,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
    )
    assert manifest.validation_passed
    assert "mbsf_oc_csv" in manifest.files
    assert "mbsf_oc_parquet" in manifest.files
    assert (Path(tmpdir) / "mbsf_oc.csv").exists()
    assert (Path(tmpdir) / "mbsf_oc.parquet").exists()


def test_mbsf_oc_cli_subcommands(capsys):
  """Tests CLI subcommands with mbsf_oc data."""
  code = cli_main(["validate", "--scenario", "invalid_mbsf_other_chronic_condition_indicator"])
  assert code == 1
  captured = capsys.readouterr()
  assert "FLD-010" in captured.out

  code = cli_main(["scenario", "--name", "valid_baseline_cohort"])
  assert code == 0
  captured = capsys.readouterr()
  assert "MBSF Other Chronic Conditions" in captured.out

  with TemporaryDirectory() as tmpdir:
    code = cli_main(["export", "--scenario", "valid_baseline_cohort", "--output-dir", tmpdir])
    assert code == 0
    assert (Path(tmpdir) / "mbsf_oc.parquet").exists()

    code = cli_main(["audit", "--scenario", "valid_baseline_cohort", "--output-dir", tmpdir])
    assert code == 0
    assert (Path(tmpdir) / "audit_report.json").exists()
