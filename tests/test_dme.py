"""Unit tests for Durable Medical Equipment (DME) Claims domain extension."""

from datetime import date
from pathlib import Path
import tempfile

import polars as pl
from medicare_synth.audit import AuditEngine
from medicare_synth.cli import main as cli_main
from medicare_synth.expansion import HorizontalExpander
from medicare_synth.manifest import SourceManifest
from medicare_synth.models import DurableMedicalEquipmentClaimRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import FindingCategory, RelationalValidator


def test_dme_claim_record_validation():
  """Tests DurableMedicalEquipmentClaimRecord Pydantic model validation."""
  record = DurableMedicalEquipmentClaimRecord(
    clm_id="CLM_D001",
    line_num=1,
    bene_id="BENE_001",
    clm_from_dt=date(2021, 2, 10),
    clm_thru_dt=date(2021, 2, 15),
    clm_pmt_amt=350.00,
    dme_line_item_count=2,
    line_cms_type_srvc_cd="P",
  )
  assert record.clm_id == "CLM_D001"
  assert record.line_num == 1
  assert record.bene_id == "BENE_001"
  assert record.dme_line_item_count == 2
  assert record.line_cms_type_srvc_cd == "P"


def test_source_manifest_dme_file_entry():
  """Tests that source manifest contains DME claims file entry."""
  manifest = SourceManifest.load_default_manifest()
  dme_files = [f for f in manifest.files if f.file_domain == "dme"]
  assert len(dme_files) == 1
  assert dme_files[0].file_id == "DE1_0_2021_DME_Claims_Sample_1"
  assert dme_files[0].primary_key == ["CLM_ID", "LINE_NUM"]


def test_dme_baseline_normalizer():
  """Tests BaselineNormalizer.normalize_dme_claims method."""
  raw_records = [
    {
      "clm_id": "CLM_D001",
      "line_num": 1,
      "bene_id": "BENE_001",
      "clm_from_dt": date(2021, 2, 10),
      "clm_thru_dt": date(2021, 2, 15),
      "clm_pmt_amt": 350.00,
      "dme_line_item_count": 2,
      "line_cms_type_srvc_cd": "P",
    }
  ]
  df = BaselineNormalizer.normalize_dme_claims(raw_records)
  assert df.height == 1
  assert "dme_line_item_count" in df.columns
  assert df.schema["clm_from_dt"] == pl.Date


def test_dme_validator_checks():
  """Tests RelationalValidator checks on DME claims."""
  validator = RelationalValidator()

  # Valid scenario
  slice_valid = ScenarioCompiler.valid_baseline_cohort()
  report_valid = validator.validate_slice(
    bene_df=slice_valid.bene_df,
    carrier_df=slice_valid.carrier_df,
    outpatient_df=slice_valid.outpatient_df,
    inpatient_df=slice_valid.inpatient_df,
    pde_df=slice_valid.pde_df,
    snf_df=slice_valid.snf_df,
    hha_df=slice_valid.hha_df,
    dme_df=slice_valid.dme_df,
  )
  assert report_valid.is_valid

  # Invalid scenario: zero line item count
  slice_invalid = ScenarioCompiler.invalid_dme_line_item_count()
  report_invalid = validator.validate_slice(
    bene_df=slice_invalid.bene_df,
    carrier_df=slice_invalid.carrier_df,
    outpatient_df=slice_invalid.outpatient_df,
    inpatient_df=slice_invalid.inpatient_df,
    pde_df=slice_invalid.pde_df,
    snf_df=slice_invalid.snf_df,
    hha_df=slice_invalid.hha_df,
    dme_df=slice_invalid.dme_df,
  )
  assert not report_invalid.is_valid
  field_findings = [f for f in report_invalid.findings if f.category == FindingCategory.FIELD and f.rule_id == "FLD-004"]
  assert len(field_findings) == 1


def test_dme_release_export():
  """Tests exporting DME claims to release bundles."""
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  with tempfile.TemporaryDirectory() as tmp_dir:
    exporter = ReleaseExporter(output_dir=tmp_dir, release_id="v1.0.0-dme-test")
    manifest = exporter.export_slice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=slice_data.outpatient_df,
      fmt="parquet",
      inpatient_df=slice_data.inpatient_df,
      pde_df=slice_data.pde_df,
      snf_df=slice_data.snf_df,
      hha_df=slice_data.hha_df,
      dme_df=slice_data.dme_df,
    )
    assert manifest.validation_passed
    assert "dme_parquet" in manifest.files
    dme_file = Path(tmp_dir) / "dme.parquet"
    assert dme_file.exists()


def test_dme_horizontal_expansion():
  """Tests connected-subgraph horizontal expansion on DME claims."""
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  tables = {
    "beneficiary_summary": slice_data.bene_df,
    "carrier_claims": slice_data.carrier_df,
    "outpatient_claims": slice_data.outpatient_df,
    "inpatient_claims": slice_data.inpatient_df,
    "pde_events": slice_data.pde_df,
    "snf_claims": slice_data.snf_df,
    "hha_claims": slice_data.hha_df,
    "dme_claims": slice_data.dme_df,
  }
  expander = HorizontalExpander(seed=42)
  expanded = expander.expand_subgraph(tables, scale_factor=2)
  assert expanded["dme_claims"].height == slice_data.dme_df.height * 2


def test_dme_audit_engine():
  """Tests AuditEngine metrics including DME claims."""
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  tables = {
    "beneficiary": slice_data.bene_df,
    "carrier": slice_data.carrier_df,
    "outpatient": slice_data.outpatient_df,
    "inpatient": slice_data.inpatient_df,
    "pde": slice_data.pde_df,
    "snf": slice_data.snf_df,
    "hha": slice_data.hha_df,
    "dme": slice_data.dme_df,
  }
  engine = AuditEngine(dataset=tables, scenario_name="test_dme")
  report = engine.run_audit()
  assert "beneficiary_dme_coverage" in report.join_coverage
  assert report.join_coverage["beneficiary_dme_coverage"] == 1.0
  assert "dme" in report.column_metrics


def test_dme_cli_commands():
  """Tests CLI execution for validate, scenario, export, and audit with DME claims."""
  with tempfile.TemporaryDirectory() as tmp_dir:
    assert cli_main(["validate", "--scenario", "valid_baseline_cohort"]) == 0
    assert cli_main(["scenario", "--name", "valid_baseline_cohort"]) == 0
    assert cli_main(["export", "--scenario", "valid_baseline_cohort", "--output-dir", tmp_dir, "--format", "parquet"]) == 0
    assert cli_main(["audit", "--scenario", "valid_baseline_cohort", "--output-dir", tmp_dir]) == 0
