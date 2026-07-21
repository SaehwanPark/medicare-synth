"""Unit tests for MBSF Part D PDE Cost & Utilization Segment domain extension, validation, and release pipelines."""

import tempfile
from pathlib import Path
import pytest
from medicare_synth.cli import main
from medicare_synth.evidence import RKBEvidenceSnapshot
from medicare_synth.manifest import SourceManifest
from medicare_synth.models import MBSFPartDPDEUtilizationRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator, Severity


def test_mbsf_pde_util_model_validation():
  """Tests valid and invalid field assignments on MBSFPartDPDEUtilizationRecord."""
  rec = MBSFPartDPDEUtilizationRecord(
    bene_id="BENE_PDE_001",
    rfrnc_yr=2021,
    pde_tot_fill_cnt=10,
    pde_brand_fill_cnt=3,
    pde_generic_fill_cnt=7,
    pde_tot_cst_amt=1200.0,
    pde_ptnt_pay_amt=100.0,
    pde_lis_pay_amt=0.0,
    val_mbsf_pde_util_01=1.0,
  )
  assert rec.bene_id == "BENE_PDE_001"
  assert rec.pde_tot_fill_cnt == 10
  assert rec.pde_tot_cst_amt == 1200.0

  with pytest.raises(Exception):
    MBSFPartDPDEUtilizationRecord(bene_id="BENE_PDE_002", pde_tot_fill_cnt=-1)


def test_mbsf_pde_util_manifest_and_evidence():
  """Verifies manifest entry and RKB snapshot variables/constraints for MBSF Part D PDE Utilization Segment."""
  manifest = SourceManifest.load_default_manifest()
  pde_util_file = next((f for f in manifest.files if f.file_domain == "mbsf_pde_util"), None)
  assert pde_util_file is not None
  assert pde_util_file.file_id == "DE1_0_2021_MBSF_PDE_Utilization_Sample_1"
  assert pde_util_file.primary_key == ["BENE_ID"]

  snapshot = RKBEvidenceSnapshot.load_default_snapshot()
  assert "PDE_TOT_FILL_CNT" in snapshot.variables
  assert "PDE_BRAND_FILL_CNT" in snapshot.variables
  assert "PDE_GENERIC_FILL_CNT" in snapshot.variables
  assert "PDE_TOT_CST_AMT" in snapshot.variables

  pde_util_constraint = next((c for c in snapshot.constraints if c.constraint_id == "VAL_MBSF_PDE_UTIL_01"), None)
  assert pde_util_constraint is not None
  assert pde_util_constraint.category == "field"


def test_mbsf_pde_util_relational_validation():
  """Tests relational validator on valid cohort and PDE utilization anomaly scenario."""
  validator = RelationalValidator()

  valid_slice = ScenarioCompiler.valid_baseline_cohort()
  valid_report = validator.validate_slice(
    bene_df=valid_slice.bene_df,
    carrier_df=valid_slice.carrier_df,
    outpatient_df=valid_slice.outpatient_df,
    mbsf_pde_util_df=valid_slice.mbsf_pde_util_df,
  )
  assert valid_report.is_valid

  invalid_slice = ScenarioCompiler.invalid_mbsf_pde_utilization_count()
  invalid_report = validator.validate_slice(
    bene_df=invalid_slice.bene_df,
    carrier_df=invalid_slice.carrier_df,
    outpatient_df=invalid_slice.outpatient_df,
    mbsf_pde_util_df=invalid_slice.mbsf_pde_util_df,
  )
  assert not invalid_report.is_valid
  fld_findings = [f for f in invalid_report.findings if f.rule_id == "FLD-015"]
  assert len(fld_findings) == 1
  assert fld_findings[0].severity == Severity.HIGH


def test_mbsf_pde_util_normalizer():
  """Tests BaselineNormalizer.normalize_mbsf_pde_utilization with raw record dictionaries."""
  records = [
    {
      "bene_id": "BENE_PDE_101",
      "rfrnc_yr": 2021,
      "pde_tot_fill_cnt": 8,
      "pde_brand_fill_cnt": 2,
      "pde_generic_fill_cnt": 6,
      "pde_tot_cst_amt": 850.0,
      "pde_ptnt_pay_amt": 60.0,
      "pde_lis_pay_amt": 0.0,
      "val_mbsf_pde_util_01": 1.0,
    }
  ]
  df = BaselineNormalizer.normalize_mbsf_pde_utilization(records)
  assert df.height == 1
  assert "pde_tot_fill_cnt" in df.columns
  assert df["pde_tot_fill_cnt"][0] == 8


def test_mbsf_pde_util_exporter_and_cli():
  """Tests release exporter writing mbsf_pde_util artifacts and CLI subcommand integration."""
  valid_slice = ScenarioCompiler.valid_baseline_cohort()
  with tempfile.TemporaryDirectory() as tmpdir:
    output_dir = Path(tmpdir) / "release"
    exporter = ReleaseExporter(output_dir=output_dir, release_id="test_release_pde_util")
    manifest = exporter.export_slice(
      bene_df=valid_slice.bene_df,
      carrier_df=valid_slice.carrier_df,
      outpatient_df=valid_slice.outpatient_df,
      mbsf_pde_util_df=valid_slice.mbsf_pde_util_df,
    )
    assert manifest.validation_passed
    assert (output_dir / "mbsf_pde_util.parquet").exists()
    assert (output_dir / "mbsf_pde_util.csv").exists()

  with tempfile.TemporaryDirectory() as tmpdir:
    ret = main(["export", "--scenario", "valid_baseline_cohort", "--output-dir", tmpdir, "--format", "parquet"])
    assert ret == 0
    assert (Path(tmpdir) / "mbsf_pde_util.parquet").exists()
