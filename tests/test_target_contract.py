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
  EvidenceIRError,
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


@pytest.mark.parametrize("defect", ["duplicate", "wrong_year", "missing_year", "missing_date"])
def test_ambiguous_analysis_inputs_are_refused(
  tables: dict[str, pl.DataFrame], defect: str
) -> None:
  finding = load_finding(package_fixtures_dir() / "lit07_avalere_ffs_diabetes_ip_risk.json")
  if defect == "duplicate":
    cc = tables["mbsf_chronic_conditions"]
    tables["mbsf_chronic_conditions"] = pl.concat([cc, cc.head(1)])
  elif defect == "wrong_year":
    tables["mbsf_chronic_conditions"] = tables["mbsf_chronic_conditions"].with_columns(
      pl.lit(2022).alias("rfrnc_yr")
    )
  elif defect == "missing_year":
    tables["mbsf_base_enrollment"] = tables["mbsf_base_enrollment"].drop("rfrnc_yr")
  else:
    tables["inpatient_claims"] = tables["inpatient_claims"].drop("clm_admsn_dt")
  report = execute_finding(finding, tables)
  assert not report.executable
  assert report.synthetic_estimate is None
  assert report.errors
  with pytest.raises(EvidenceIRError):
    discrepancy_for_findings(tables, [finding], partition=PartitionName.CALIBRATION)


def test_weighted_stratified_prevalence_and_ineligible_weights(
  tables: dict[str, pl.DataFrame],
) -> None:
  finding = load_finding(package_fixtures_dir() / "lit03_mmwr_diabetes_prevalence_2015.json")
  finding = finding.model_copy(update={
    "population": finding.population.model_copy(update={"sex_codes": ("2",)}),
    "result": finding.result.model_copy(update={"estimate": 0.25}),
  })
  bene = tables["beneficiary_summary"].head(5).with_columns(
    pl.Series("bene_birth_dt", [date(1951, 1, 1)] * 4 + [date(1958, 1, 1)]),
    pl.Series("bene_sex_ident_cd", ["2", "2", "2", "1", "2"]),
  )
  ids = bene["bene_id"].to_list()
  tables["beneficiary_summary"] = bene
  tables["mbsf_base_enrollment"] = tables["mbsf_base_enrollment"].head(5).with_columns(
    pl.Series("bene_hi_cvrage_tot_mons", [12, 12, 11, 12, 12])
  )
  tables["mbsf_chronic_conditions"] = tables["mbsf_chronic_conditions"].head(5).with_columns(
    pl.Series("sp_diabetes", ["1", "0", "1", "1", "1"])
  )
  tables["inpatient_claims"] = tables["inpatient_claims"].head(0)
  weights = pl.DataFrame({"bene_id": ids, "weight": [3.0, 1.0, 9.0, 9.0, 9.0]})
  unweighted = execute_finding(finding, tables)
  weighted = discrepancy_for_findings(
    tables, [finding], partition=PartitionName.CALIBRATION, weights=weights
  )
  assert unweighted.n_eligible == 2
  assert unweighted.synthetic_estimate == 0.5
  assert weighted.rows[0].synthetic_estimate == 0.75
  fitted = reweight_beneficiaries(tables, [moment_target_from_finding(finding)])
  assert fitted.after.rows[0].synthetic_estimate == 0.25
  assert fitted.weights.filter(pl.col("bene_id").is_in(ids[2:]))["weight"].to_list() == [1.0] * 3


def test_optional_part_c_ma_months_exclude_beneficiaries(
  tables: dict[str, pl.DataFrame],
) -> None:
  finding = load_finding(package_fixtures_dir() / "lit03_mmwr_diabetes_prevalence_2015.json")
  before = execute_finding(finding, tables)
  ids = tables["beneficiary_summary"]["bene_id"].to_list()
  tables["mbsf_part_c"] = pl.DataFrame({
    "bene_id": ids,
    "rfrnc_yr": [2021] * len(ids),
    "bene_ma_cvrage_tot_mons": [12] * len(ids),
  })
  assert before.n_eligible > 0
  after = execute_finding(finding, tables)
  assert not after.executable
  assert after.n_eligible == 0
  fitted = reweight_beneficiaries(tables, [moment_target_from_finding(finding)])
  assert fitted.diagnostics.infeasible
  assert fitted.after.rows[0].synthetic_estimate is None


def test_conditional_risk_weighting_uses_eligible_diabetes_denominator(
  tables: dict[str, pl.DataFrame],
) -> None:
  finding = load_finding(package_fixtures_dir() / "lit07_avalere_ffs_diabetes_ip_risk.json")
  bene = tables["beneficiary_summary"].head(4).with_columns(
    pl.Series("bene_birth_dt", [date(1951, 1, 1)] * 3 + [date(1960, 1, 1)])
  )
  ids = bene["bene_id"].to_list()
  tables["beneficiary_summary"] = bene
  tables["mbsf_base_enrollment"] = tables["mbsf_base_enrollment"].head(4)
  tables["mbsf_chronic_conditions"] = tables["mbsf_chronic_conditions"].head(4).with_columns(
    pl.Series("sp_diabetes", ["1", "1", "0", "1"])
  )
  tables["inpatient_claims"] = pl.DataFrame({
    "bene_id": [ids[0], ids[0], ids[2], ids[3]],
    "clm_admsn_dt": [date(2021, 1, 1)] * 4,
  })
  weights = pl.DataFrame({"bene_id": ids, "weight": [3.0, 1.0, 20.0, 30.0]})
  report = execute_finding(finding, tables)
  disc = discrepancy_for_findings(
    tables, [finding], partition=PartitionName.CALIBRATION, weights=weights
  )
  assert report.n_eligible == 2
  assert report.synthetic_estimate == 0.5
  assert disc.rows[0].synthetic_estimate == 0.75
  fitted = reweight_beneficiaries(tables, [moment_target_from_finding(finding)])
  assert fitted.after.rows[0].synthetic_estimate == pytest.approx(0.13)
  assert fitted.weights.filter(pl.col("bene_id").is_in(ids[2:]))["weight"].to_list() == [1.0, 1.0]


@pytest.mark.parametrize("overlap", [True, False])
def test_multi_target_fit_and_report_share_each_cohort(
  tables: dict[str, pl.DataFrame], overlap: bool
) -> None:
  finding = load_finding(package_fixtures_dir() / "lit03_mmwr_diabetes_prevalence_2015.json")
  women = finding.model_copy(update={
    "finding_id": "women",
    "population": finding.population.model_copy(update={"sex_codes": ("2",)}),
    "result": finding.result.model_copy(update={"estimate": 0.4}),
  })
  second = finding.model_copy(update={
    "finding_id": "overlap" if overlap else "men",
    "population": finding.population.model_copy(
      update={"sex_codes": None if overlap else ("1",)}
    ),
    "result": finding.result.model_copy(update={"estimate": 0.5}),
  })
  findings = [women, second]
  fit = reweight_beneficiaries(
    tables, [moment_target_from_finding(item) for item in findings], max_iterations=3
  )
  reported = discrepancy_for_findings(
    tables, findings, partition=PartitionName.CALIBRATION, weights=fit.weights
  )
  assert [row.synthetic_estimate for row in fit.after.rows] == [
    row.synthetic_estimate for row in reported.rows
  ]
