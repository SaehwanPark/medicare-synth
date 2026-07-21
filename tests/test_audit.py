"""Unit tests for AuditEngine, AuditReport, and CLI audit subcommand."""

import json
from pathlib import Path
from medicare_synth.audit import AuditEngine, AuditReport
from medicare_synth.cli import main
from medicare_synth.scenarios import ScenarioCompiler


def test_audit_engine_basic() -> None:
  scenario_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
  dataset = {
    "beneficiary": scenario_slice.bene_df,
    "carrier": scenario_slice.carrier_df,
    "outpatient": scenario_slice.outpatient_df,
  }

  engine = AuditEngine(dataset=dataset, scenario_name="valid_baseline_cohort")
  report = engine.run_audit()

  assert isinstance(report, AuditReport)
  assert report.scenario_name == "valid_baseline_cohort"
  assert report.join_coverage.get("beneficiary_carrier_coverage") == 1.0
  assert report.join_coverage.get("beneficiary_outpatient_coverage") == 1.0


def test_k_anonymity_calculation() -> None:
  scenario_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
  dataset = {
    "beneficiary": scenario_slice.bene_df,
    "carrier": scenario_slice.carrier_df,
  }

  engine = AuditEngine(dataset=dataset, scenario_name="valid_baseline_cohort")
  res = engine.compute_k_anonymity("beneficiary", ["BENE_BIRTH_DT"])

  assert res is not None
  assert [c.upper() for c in res.qi_columns] == ["BENE_BIRTH_DT"]
  assert res.min_k >= 1
  assert res.class_count >= 1
  assert res.at_risk_record_count >= 0


def test_column_metrics_calculation() -> None:
  scenario_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
  dataset = {"carrier": scenario_slice.carrier_df}

  engine = AuditEngine(dataset=dataset, scenario_name="valid_baseline_cohort")
  metrics = engine.compute_column_metrics("carrier")

  assert len(metrics) > 0
  col_names = [m.column_name.upper() for m in metrics]
  assert "CLM_ID" in col_names
  assert "BENE_ID" in col_names


def test_cli_audit_subcommand(tmp_path: Path) -> None:
  out_dir = tmp_path / "audit_out"
  exit_code = main(["audit", "--scenario", "valid_baseline_cohort", "--output-dir", str(out_dir)])
  assert exit_code == 0

  report_file = out_dir / "audit_report.json"
  assert report_file.exists()

  data = json.loads(report_file.read_text(encoding="utf-8"))
  assert data["scenario_name"] == "valid_baseline_cohort"
  assert "join_coverage" in data
  assert "k_anonymity" in data
  assert "column_metrics" in data


def test_extended_k_anonymity_calculation() -> None:
  scenario_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
  dataset = {
    "beneficiary": scenario_slice.bene_df,
    "carrier": scenario_slice.carrier_df,
    "outpatient": scenario_slice.outpatient_df,
    "snf": scenario_slice.snf_df,
    "hha": scenario_slice.hha_df,
    "dme": scenario_slice.dme_df,
    "hospice": scenario_slice.hospice_df,
    "pde": scenario_slice.pde_df,
    "mbsf_cc": scenario_slice.mbsf_cc_df,
    "mbsf_oc": scenario_slice.mbsf_oc_df,
    "mbsf_cu": scenario_slice.mbsf_cu_df,
    "mbsf_d": scenario_slice.mbsf_d_df,
    "mbsf_base": scenario_slice.mbsf_base_df,
    "mbsf_ndi": scenario_slice.mbsf_ndi_df,
    "mbsf_ra": scenario_slice.mbsf_ra_df,
    "mbsf_c": scenario_slice.mbsf_c_df,
    "mbsf_ffs": scenario_slice.mbsf_ffs_df,
    "mbsf_pde_util": scenario_slice.mbsf_pde_util_df,
  }

  engine = AuditEngine(dataset=dataset, scenario_name="valid_baseline_cohort")
  report = engine.run_audit()

  assert isinstance(report, AuditReport)
  assert "beneficiary" in report.k_anonymity
  assert "carrier" in report.k_anonymity
  assert "outpatient" in report.k_anonymity
  assert "snf" in report.k_anonymity
  assert "hha" in report.k_anonymity
  assert "dme" in report.k_anonymity
  assert "hospice" in report.k_anonymity
  assert "pde" in report.k_anonymity
  assert "mbsf_cc" in report.k_anonymity
  assert "mbsf_oc" in report.k_anonymity
  assert "mbsf_cu" in report.k_anonymity
  assert "mbsf_d" in report.k_anonymity
  assert "mbsf_base" in report.k_anonymity
  assert "mbsf_ndi" in report.k_anonymity
  assert "mbsf_ra" in report.k_anonymity
  assert "mbsf_c" in report.k_anonymity
  assert "mbsf_ffs" in report.k_anonymity
  assert "mbsf_pde_util" in report.k_anonymity

  # Verify quasi-identifiers
  assert "bene_birth_dt" in report.k_anonymity["beneficiary"].qi_columns
  assert "icd_dgns_cd1" in report.k_anonymity["carrier"].qi_columns
  assert "icd_dgns_cd1" in report.k_anonymity["outpatient"].qi_columns
  assert "clm_utlztn_day_cnt" in report.k_anonymity["snf"].qi_columns
  assert "clm_utlztn_day_cnt" in report.k_anonymity["hha"].qi_columns
  assert "line_cms_type_srvc_cd" in report.k_anonymity["dme"].qi_columns
  assert "hospice_terminal_diag_cd" in report.k_anonymity["hospice"].qi_columns
  assert "prod_srvc_id" in report.k_anonymity["pde"].qi_columns
  assert "sp_diabetes" in report.k_anonymity["mbsf_cc"].qi_columns
  assert "sp_hypert" in report.k_anonymity["mbsf_oc"].qi_columns
  assert "bene_mdcr_pay_amt" in report.k_anonymity["mbsf_cu"].qi_columns
  assert "ptd_cntrct_id_01" in report.k_anonymity["mbsf_d"].qi_columns
  assert "mdcr_entlmt_buyin_ind_01" in report.k_anonymity["mbsf_base"].qi_columns
  assert "ndi_match_ind" in report.k_anonymity["mbsf_ndi"].qi_columns
  assert "cms_hcc_risk_score" in report.k_anonymity["mbsf_ra"].qi_columns
  assert "ptc_cntrct_id_01" in report.k_anonymity["mbsf_c"].qi_columns
  assert "ip_adm_cnt" in report.k_anonymity["mbsf_ffs"].qi_columns
  assert "pde_tot_fill_cnt" in report.k_anonymity["mbsf_pde_util"].qi_columns

