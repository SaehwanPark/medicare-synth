"""Unit test suite for MBSF Part D Characteristics Segment domain extension.
"""

from pathlib import Path
import tempfile

import polars as pl
import pytest

from medicare_synth.audit import AuditEngine
from medicare_synth.catalog import ScenarioCatalog
from medicare_synth.expansion import HorizontalExpander
from medicare_synth.models import MBSFPartDRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator


def test_mbsf_d_domain_model():
  record = MBSFPartDRecord(
    bene_id="BENE_TEST_D_01",
    rfrnc_yr=2021,
    ptd_cntrct_id_01="S0001",
    ptd_pbp_id_01="001",
    ptd_sgnt_cd_01="000",
    rds_ind_01="N",
    li_cost_shrh_grp_cd_01="00",
    bene_ptd_trcc_amt=1850.0,
    bene_ptd_moop_amt=420.0,
  )
  assert record.bene_id == "BENE_TEST_D_01"
  assert record.bene_ptd_trcc_amt == 1850.0
  assert record.bene_ptd_moop_amt == 420.0


def test_mbsf_d_normalizer():
  raw_records = [
    {
      "bene_id": "BENE_NORM_D_01",
      "rfrnc_yr": 2021,
      "ptd_cntrct_id_01": "S0002",
      "ptd_pbp_id_01": "002",
      "ptd_sgnt_cd_01": "000",
      "rds_ind_01": "N",
      "li_cost_shrh_grp_cd_01": "01",
      "bene_ptd_trcc_amt": 650.0,
      "bene_ptd_moop_amt": 150.0,
    }
  ]
  df = BaselineNormalizer.normalize_mbsf_part_d(raw_records)
  assert df.height == 1
  assert "bene_ptd_trcc_amt" in df.columns
  assert df.schema["bene_ptd_trcc_amt"] == pl.Float64


def test_mbsf_d_validation_clean():
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
    mbsf_d_df=slice_data.mbsf_d_df,
  )
  assert report.is_valid
  assert len(report.findings) == 0


def test_mbsf_d_validation_invalid_contract():
  slice_data = ScenarioCompiler.invalid_mbsf_part_d_contract()
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
  )
  assert not report.is_valid
  findings = [f for f in report.findings if f.rule_id == "FLD-008"]
  assert len(findings) == 1
  assert "violating non-negative cost constraints" in findings[0].message


def test_mbsf_d_release_exporter():
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
      mbsf_d_df=slice_data.mbsf_d_df,
    )
    assert manifest.validation_passed
    assert "mbsf_d_parquet" in manifest.files
    assert (Path(tmp_dir) / "mbsf_d.parquet").exists()


def test_mbsf_d_expansion():
  slice_data = ScenarioCompiler.valid_baseline_cohort()
  tables = {
    "beneficiary_summary": slice_data.bene_df,
    "mbsf_part_d": slice_data.mbsf_d_df,
  }
  expander = HorizontalExpander()
  scaled = expander.expand_subgraph(tables, scale_factor=2)
  assert scaled["mbsf_part_d"].height == slice_data.mbsf_d_df.height * 2


def test_mbsf_d_catalog_and_audit():
  info = ScenarioCatalog.get_scenario_info("invalid_mbsf_part_d_contract")
  assert info is not None
  assert not info.is_valid

  slice_data = ScenarioCompiler.valid_baseline_cohort()
  tables = {
    "beneficiary": slice_data.bene_df,
    "mbsf_d": slice_data.mbsf_d_df,
  }
  engine = AuditEngine(dataset=tables, scenario_name="test_mbsf_d")
  report = engine.run_audit()
  assert "beneficiary_mbsf_d_coverage" in report.join_coverage
  assert report.join_coverage["beneficiary_mbsf_d_coverage"] == 1.0
