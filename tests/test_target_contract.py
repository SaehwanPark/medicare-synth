"""Regressions for the shared 2021 evidence and calibration target contract."""

from datetime import date

import polars as pl
import pytest

from medicare_synth.calibration import (
  discrepancy_for_findings,
  moment_target_from_finding,
  reweight_beneficiaries,
)
from medicare_synth.evidence_corpus import PartitionName
from medicare_synth.evidence_ir import (
  compile_finding,
  execute_finding,
  load_finding,
  package_fixtures_dir,
)
from medicare_synth.synthesis import ConditionalWorldParams, generate_diabetes_ip_world


@pytest.fixture
def tables() -> dict[str, pl.DataFrame]:
  return generate_diabetes_ip_world(
    ConditionalWorldParams(
      n_beneficiaries=500,
      seed=42,
      diabetes_prevalence=0.4,
      p_ip_given_diabetes=0.5,
      p_ip_given_no_diabetes=0.1,
    )
  ).tables()


def test_unsupported_estimator_never_dispatches_as_crude() -> None:
  finding = load_finding(package_fixtures_dir() / "lit03_mmwr_diabetes_prevalence_2015.json")
  modified = finding.model_copy(update={"analysis": finding.analysis.model_copy(
    update={"estimator": "logistic_regression"}
  )})
  compiled = compile_finding(modified)
  assert not compiled.compatibility.executable
  assert any(issue.code == "ESTIMATOR" for issue in compiled.compatibility.errors)


def test_out_of_year_admissions_do_not_count(tables: dict[str, pl.DataFrame]) -> None:
  finding = load_finding(package_fixtures_dir() / "lit07_avalere_ffs_diabetes_ip_risk.json")
  tables["inpatient_claims"] = tables["inpatient_claims"].with_columns(
    pl.lit(date(2022, 1, 1)).alias("clm_admsn_dt")
  )
  report = execute_finding(finding, tables)
  disc = discrepancy_for_findings(tables, [finding], partition=PartitionName.CALIBRATION)
  assert report.synthetic_estimate == 0.0
  assert disc.rows[0].synthetic_estimate == 0.0


def test_reweight_does_not_use_ineligible_support(tables: dict[str, pl.DataFrame]) -> None:
  finding = load_finding(package_fixtures_dir() / "lit03_mmwr_diabetes_prevalence_2015.json")
  age_flags = tables["beneficiary_summary"].select(
    "bene_id", pl.when(pl.col("bene_birth_dt").dt.year() <= 1953)
    .then(pl.lit("1")).otherwise(pl.lit("0")).alias("new_diabetes")
  )
  tables["mbsf_chronic_conditions"] = (
    tables["mbsf_chronic_conditions"].join(age_flags, on="bene_id")
    .drop("sp_diabetes").rename({"new_diabetes": "sp_diabetes"})
  )
  result = reweight_beneficiaries(tables, [moment_target_from_finding(finding)])
  assert result.diagnostics.infeasible
  assert not result.diagnostics.converged
