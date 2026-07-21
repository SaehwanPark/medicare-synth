"""Unit test suite for MBSF Cost & Use Segment domain extension.
"""

from pathlib import Path
import tempfile

import polars as pl

from medicare_synth.audit import AuditEngine
from medicare_synth.catalog import ScenarioCatalog
from medicare_synth.expansion import HorizontalExpander
from medicare_synth.models import MBSFCostAndUseRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator


def test_mbsf_cu_domain_model():
  record = MBSFCostAndUseRecord(
    bene_id="BENE_TEST_CU_01",
    rfrnc_yr=2021,
    bene_mdcr_pay_amt=12500.0,
    bene_tot_pay_amt=14000.0,
    bene_ip_ddctbl_amt=1484.0,
    bene_cvrd_dys_cnt=12,
  )
  assert record.bene_id == "BENE_TEST_CU_01"
  assert record.bene_mdcr_pay_amt == 12500.0
  assert record.bene_cvrd_dys_cnt == 12


def test_mbsf_cu_normalizer():
  raw_records = [
    {
      "bene_id": "BENE_NORM_CU_01",
      "rfrnc_yr": 2021,
      "bene_mdcr_pay_amt": 8200.0,
      "bene_tot_pay_amt": 9500.0,
      "bene_ip_ddctbl_amt": 0.0,
      "bene_cvrd_dys_cnt": 5,
    }
  ]
  df = BaselineNormalizer.normalize_mbsf_cost_and_use(raw_records)
  assert df.height == 1
  assert "bene_mdcr_pay_amt" in df.columns
  assert df.schema["bene_mdcr_pay_amt"] == pl.Float64


def test_mbsf_cu_validation_clean():
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
    mbsf_cu_df=slice_data.mbsf_cu_df,
  )
  assert report.is_valid
  assert len(report.findings) == 0


def test_mbsf_cu_validation_invalid_payment():
  slice_data = ScenarioCompiler.invalid_mbsf_cost_use_payment()
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
  )
  assert not report.is_valid
  findings = [f for f in report.findings if f.rule_id == "FLD-007"]
  assert len(findings) == 1
  assert "violating non-negative payment" in findings[0].message


def test_mbsf_cu_release_exporter():
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
      mbsf_cu_df=slice_data.mbsf_cu_df,
    )
    assert manifest.validation_passed
    assert "mbsf_cu_parquet" in manifest.files
    assert (Path(tmp_dir) / "mbsf_cu.parquet").exists()


def test_mbsf_cu_expansion():
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  tables = {
    "beneficiary_summary": slice_data.bene_df,
    "mbsf_cost_and_use": slice_data.mbsf_cu_df,
  }
  expander = HorizontalExpander()
  scaled = expander.expand_subgraph(tables, scale_factor=2)
  assert scaled["mbsf_cost_and_use"].height == slice_data.mbsf_cu_df.height * 2


def test_mbsf_cu_catalog_and_audit():
  info = ScenarioCatalog.get_scenario_info("invalid_mbsf_cost_use_payment")
  assert info is not None
  assert not info.is_valid

  slice_data = ScenarioCompiler.valid_baseline_cohort()
  tables = {
    "beneficiary": slice_data.bene_df,
    "mbsf_cu": slice_data.mbsf_cu_df,
  }
  engine = AuditEngine(dataset=tables, scenario_name="test_mbsf_cu")
  report = engine.run_audit()
  assert "beneficiary_mbsf_cu_coverage" in report.join_coverage
  assert report.join_coverage["beneficiary_mbsf_cu_coverage"] == 1.0
