"""Unit tests for Master Beneficiary Summary File (MBSF) National Death Index (NDI) Segment domain extension."""

from pathlib import Path
from tempfile import TemporaryDirectory

import polars as pl
import pytest
from pydantic import ValidationError

from medicare_synth.cli import main as cli_main
from medicare_synth.models import MBSFNDIRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import FindingCategory, RelationalValidator, Severity


def test_mbsf_ndi_model_validation():
  """Tests Pydantic validation for MBSFNDIRecord."""
  rec = MBSFNDIRecord(
    bene_id="BENE_NDI_001",
    rfrnc_yr=2021,
    ndi_match_ind="1",
    ndi_diuse_cd="I2510",
    val_mbsf_ndi_01=1.0,
  )
  assert rec.bene_id == "BENE_NDI_001"
  assert rec.ndi_match_ind == "1"
  assert rec.ndi_diuse_cd == "I2510"

  with pytest.raises(ValidationError):
    MBSFNDIRecord(bene_id="BENE_EXCEED_LIMIT_99999999")


def test_mbsf_ndi_normalizer():
  """Tests BaselineNormalizer.normalize_mbsf_ndi."""
  raw_records = [
    {
      "bene_id": "BENE_001",
      "rfrnc_yr": 2021,
      "ndi_match_ind": "1",
      "ndi_diuse_cd": "I2510",
      "val_mbsf_ndi_01": 1.0,
    }
  ]
  df = BaselineNormalizer.normalize_mbsf_ndi(raw_records)
  assert isinstance(df, pl.DataFrame)
  assert df.height == 1
  assert "ndi_match_ind" in df.columns
  assert df.schema["ndi_match_ind"] == pl.String
  assert df.schema["val_mbsf_ndi_01"] == pl.Float64


def test_mbsf_ndi_field_constraints_validation():
  """Tests RelationalValidator.check_mbsf_ndi_field_constraints for valid and invalid records."""
  valid_df = pl.DataFrame(
    [
      {
        "bene_id": "BENE_001",
        "rfrnc_yr": 2021,
        "ndi_match_ind": "1",
        "ndi_diuse_cd": "I2510",
        "val_mbsf_ndi_01": 1.0,
      }
    ]
  )
  findings = RelationalValidator.check_mbsf_ndi_field_constraints(valid_df)
  assert len(findings) == 0

  invalid_df = pl.DataFrame(
    [
      {
        "bene_id": "BENE_001",
        "rfrnc_yr": 2021,
        "ndi_match_ind": "X",  # Invalid indicator
        "ndi_diuse_cd": None,
        "val_mbsf_ndi_01": 1.0,
      }
    ]
  )
  findings = RelationalValidator.check_mbsf_ndi_field_constraints(invalid_df)
  assert len(findings) == 1
  assert findings[0].rule_id == "FLD-011"
  assert findings[0].severity == Severity.HIGH
  assert findings[0].category == FindingCategory.FIELD


def test_invalid_mbsf_ndi_match_indicator_scenario():
  """Tests anomaly scenario compilation and validation for invalid NDI match indicator."""
  slice_data = ScenarioCompiler.get_scenario("invalid_mbsf_ndi_match_indicator")
  assert slice_data.mbsf_ndi_df.height == 1

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
    mbsf_ndi_df=slice_data.mbsf_ndi_df,
  )
  assert not report.is_valid
  assert any(f.rule_id == "FLD-011" for f in report.findings)


def test_mbsf_ndi_release_export():
  """Tests ReleaseExporter inclusion of mbsf_ndi table."""
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
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )
    assert manifest.validation_passed
    assert "mbsf_ndi_csv" in manifest.files
    assert "mbsf_ndi_parquet" in manifest.files
    assert (Path(tmpdir) / "mbsf_ndi.csv").exists()
    assert (Path(tmpdir) / "mbsf_ndi.parquet").exists()


def test_mbsf_ndi_cli_subcommands(capsys):
  """Tests CLI subcommands with mbsf_ndi data."""
  code = cli_main(["validate", "--scenario", "invalid_mbsf_ndi_match_indicator"])
  assert code == 1
  captured = capsys.readouterr()
  assert "FLD-011" in captured.out

  code = cli_main(["scenario", "--name", "valid_baseline_cohort"])
  assert code == 0
  captured = capsys.readouterr()
  assert "MBSF NDI" in captured.out

  with TemporaryDirectory() as tmpdir:
    code = cli_main(["export", "--scenario", "valid_baseline_cohort", "--output-dir", tmpdir])
    assert code == 0
    assert (Path(tmpdir) / "mbsf_ndi.parquet").exists()

    code = cli_main(["audit", "--scenario", "valid_baseline_cohort", "--output-dir", tmpdir])
    assert code == 0
    assert (Path(tmpdir) / "audit_report.json").exists()
