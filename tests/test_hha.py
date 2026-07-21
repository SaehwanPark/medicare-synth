"""Unit tests for Home Health Agency (HHA) Claims domain extension."""

from datetime import date
from pathlib import Path
import tempfile

import polars as pl
import pytest
from medicare_synth.audit import AuditEngine
from medicare_synth.catalog import ScenarioCatalog
from medicare_synth.cli import main as cli_main
from medicare_synth.expansion import HorizontalExpander
from medicare_synth.manifest import SourceManifest
from medicare_synth.models import HomeHealthAgencyClaimRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import FindingCategory, RelationalValidator, Severity


def test_hha_claim_record_validation():
  """Tests HomeHealthAgencyClaimRecord Pydantic model validation."""
  record = HomeHealthAgencyClaimRecord(
    clm_id="CLM_H001",
    bene_id="BENE_001",
    clm_admsn_dt=date(2021, 4, 1),
    nch_bene_dschrg_dt=date(2021, 4, 20),
    clm_pmt_amt=2500.00,
    clm_utlztn_day_cnt=19,
    clm_hha_lupa_ind="0",
  )
  assert record.clm_id == "CLM_H001"
  assert record.bene_id == "BENE_001"
  assert record.clm_utlztn_day_cnt == 19
  assert record.clm_hha_lupa_ind == "0"


def test_source_manifest_hha_file_entry():
  """Tests that source manifest contains HHA claims file entry."""
  manifest = SourceManifest.load_default_manifest()
  hha_files = [f for f in manifest.files if f.file_domain == "hha"]
  assert len(hha_files) == 1
  assert hha_files[0].file_id == "DE1_0_2021_HHA_Claims_Sample_1"
  assert hha_files[0].primary_key == ["CLM_ID"]


def test_hha_baseline_normalizer():
  """Tests BaselineNormalizer.normalize_hha_claims method."""
  raw_records = [
    {
      "clm_id": "CLM_H001",
      "bene_id": "BENE_001",
      "clm_admsn_dt": date(2021, 4, 1),
      "nch_bene_dschrg_dt": date(2021, 4, 20),
      "clm_pmt_amt": 2500.00,
      "clm_utlztn_day_cnt": 19,
      "clm_hha_lupa_ind": "0",
    }
  ]
  df = BaselineNormalizer.normalize_hha_claims(raw_records)
  assert df.height == 1
  assert "clm_hha_lupa_ind" in df.columns
  assert df.schema["clm_admsn_dt"] == pl.Date


def test_hha_validator_checks():
  """Tests RelationalValidator checks on HHA claims."""
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
  )
  assert report_valid.is_valid

  # Invalid scenario: negative utilization days
  slice_invalid = ScenarioCompiler.invalid_hha_utilization_days()
  report_invalid = validator.validate_slice(
    bene_df=slice_invalid.bene_df,
    carrier_df=slice_invalid.carrier_df,
    outpatient_df=slice_invalid.outpatient_df,
    inpatient_df=slice_invalid.inpatient_df,
    pde_df=slice_invalid.pde_df,
    snf_df=slice_invalid.snf_df,
    hha_df=slice_invalid.hha_df,
  )
  assert not report_invalid.is_valid
  field_findings = [f for f in report_invalid.findings if f.category == FindingCategory.FIELD and f.rule_id == "FLD-003"]
  assert len(field_findings) == 1


def test_hha_release_export():
  """Tests exporting HHA claims to release bundles."""
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  with tempfile.TemporaryDirectory() as tmp_dir:
    exporter = ReleaseExporter(output_dir=tmp_dir, release_id="v1.0.0-hha-test")
    manifest = exporter.export_slice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=slice_data.outpatient_df,
      fmt="parquet",
      inpatient_df=slice_data.inpatient_df,
      pde_df=slice_data.pde_df,
      snf_df=slice_data.snf_df,
      hha_df=slice_data.hha_df,
    )
    assert manifest.validation_passed
    assert "hha_parquet" in manifest.files
    hha_file = Path(tmp_dir) / "hha.parquet"
    assert hha_file.exists()


def test_hha_horizontal_expansion():
  """Tests connected-subgraph horizontal expansion on HHA claims."""
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  tables = {
    "beneficiary_summary": slice_data.bene_df,
    "carrier_claims": slice_data.carrier_df,
    "outpatient_claims": slice_data.outpatient_df,
    "inpatient_claims": slice_data.inpatient_df,
    "pde_events": slice_data.pde_df,
    "snf_claims": slice_data.snf_df,
    "hha_claims": slice_data.hha_df,
  }
  expander = HorizontalExpander(seed=42)
  expanded = expander.expand_subgraph(tables, scale_factor=2)
  assert expanded["hha_claims"].height == slice_data.hha_df.height * 2


def test_hha_audit_engine():
  """Tests AuditEngine metrics including HHA claims."""
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  tables = {
    "beneficiary": slice_data.bene_df,
    "carrier": slice_data.carrier_df,
    "outpatient": slice_data.outpatient_df,
    "inpatient": slice_data.inpatient_df,
    "pde": slice_data.pde_df,
    "snf": slice_data.snf_df,
    "hha": slice_data.hha_df,
  }
  engine = AuditEngine(dataset=tables, scenario_name="test_hha")
  report = engine.run_audit()
  assert "beneficiary_hha_coverage" in report.join_coverage
  assert report.join_coverage["beneficiary_hha_coverage"] == 1.0
  assert "hha" in report.column_metrics


def test_hha_cli_commands():
  """Tests CLI execution for validate, scenario, export, and audit with HHA claims."""
  with tempfile.TemporaryDirectory() as tmp_dir:
    assert cli_main(["validate", "--scenario", "valid_baseline_cohort"]) == 0
    assert cli_main(["scenario", "--name", "valid_baseline_cohort"]) == 0
    assert cli_main(["export", "--scenario", "valid_baseline_cohort", "--output-dir", tmp_dir, "--format", "parquet"]) == 0
    assert cli_main(["audit", "--scenario", "valid_baseline_cohort", "--output-dir", tmp_dir]) == 0
