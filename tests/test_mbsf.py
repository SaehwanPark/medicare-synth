"""Unit test suite for MBSF Chronic Conditions Segment domain extension.
"""

from pathlib import Path
import tempfile

import polars as pl

from medicare_synth.audit import AuditEngine
from medicare_synth.catalog import ScenarioCatalog
from medicare_synth.expansion import HorizontalExpander
from medicare_synth.models import MBSFChronicConditionsRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator


def test_mbsf_domain_model():
  record = MBSFChronicConditionsRecord(
    bene_id="BENE_TEST_01",
    rfrnc_yr=2021,
    sp_alzhmd="1",
    sp_chf="1",
    sp_chrnkidn="2",
    sp_cncr="2",
    sp_diabetes="1",
    sp_ischdmt="1",
    sp_strketia="2",
    val_mbsf_01=1.0,
  )
  assert record.bene_id == "BENE_TEST_01"
  assert record.sp_alzhmd == "1"
  assert record.sp_diabetes == "1"


def test_mbsf_normalizer():
  raw_records = [
    {
      "bene_id": "BENE_NORM_01",
      "rfrnc_yr": 2021,
      "sp_alzhmd": "1",
      "sp_chf": "2",
      "sp_chrnkidn": "1",
      "sp_cncr": "2",
      "sp_diabetes": "1",
      "sp_ischdmt": "2",
      "sp_strketia": "2",
      "val_mbsf_01": 1.0,
    }
  ]
  df = BaselineNormalizer.normalize_mbsf_chronic_conditions(raw_records)
  assert df.height == 1
  assert "sp_alzhmd" in df.columns
  assert df.schema["sp_alzhmd"] == pl.String


def test_mbsf_validation_clean():
  slice_data = ScenarioCompiler.valid_baseline_cohort()
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
  )
  assert report.is_valid
  assert len(report.findings) == 0


def test_mbsf_validation_invalid_indicator():
  slice_data = ScenarioCompiler.invalid_mbsf_chronic_condition_indicator()
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
  )
  assert not report.is_valid
  findings = [f for f in report.findings if f.rule_id == "FLD-006"]
  assert len(findings) == 1
  assert "invalid indicator value" in findings[0].message


def test_mbsf_release_exporter():
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  with tempfile.TemporaryDirectory() as tmp_dir:
    exporter = ReleaseExporter(output_dir=Path(tmp_dir), release_id="v1.0.0-test")
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
      hospice_df=slice_data.hospice_df,
      mbsf_cc_df=slice_data.mbsf_cc_df,
    )
    assert manifest.validation_passed
    assert "mbsf_cc_parquet" in manifest.files
    assert (Path(tmp_dir) / "mbsf_cc.parquet").exists()


def test_mbsf_expansion():
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  tables = {
    "beneficiary_summary": slice_data.bene_df,
    "mbsf_chronic_conditions": slice_data.mbsf_cc_df,
  }
  expander = HorizontalExpander()
  scaled = expander.expand_subgraph(tables, scale_factor=2)
  assert scaled["mbsf_chronic_conditions"].height == slice_data.mbsf_cc_df.height * 2


def test_mbsf_catalog_and_audit():
  info = ScenarioCatalog.get_scenario_info("invalid_mbsf_chronic_condition_indicator")
  assert info is not None
  assert not info.is_valid

  slice_data = ScenarioCompiler.valid_baseline_cohort()
  tables = {
    "beneficiary": slice_data.bene_df,
    "mbsf_cc": slice_data.mbsf_cc_df,
  }
  engine = AuditEngine(dataset=tables, scenario_name="test_mbsf")
  report = engine.run_audit()
  assert "beneficiary_mbsf_cc_coverage" in report.join_coverage
  assert report.join_coverage["beneficiary_mbsf_cc_coverage"] == 1.0
