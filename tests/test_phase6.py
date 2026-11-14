"""Tests for the preregistered Phase 6 analyst workflow."""

from datetime import date

import polars as pl
import pytest

from medicare_synth.phase6 import analyze_workflow
from medicare_synth.synthesis import ConditionalWorldParams, generate_diabetes_ip_world


def _tables() -> dict[str, pl.DataFrame]:
  return generate_diabetes_ip_world(ConditionalWorldParams(
    n_beneficiaries=400, seed=11, diabetes_prevalence=0.3, hf_prevalence=0.2,
    p_ip_given_diabetes=0.2, p_ip_given_no_diabetes=0.04,
  )).tables()


def test_claim_duplication_does_not_duplicate_people() -> None:
  tables = _tables()
  result = analyze_workflow(tables)
  duplicated = dict(tables)
  duplicated["inpatient_claims"] = pl.concat([tables["inpatient_claims"]] * 2)
  assert analyze_workflow(duplicated) == result
  assert result["n_eligible"] == 400


def test_reference_year_and_weights() -> None:
  tables = _tables()
  later = dict(tables)
  later["inpatient_claims"] = later["inpatient_claims"].with_columns(
    pl.lit(date(2022, 1, 1)).alias("clm_admsn_dt")
  )
  assert analyze_workflow(later)["ip_risk"] == 0.0
  cc = tables["mbsf_chronic_conditions"]
  weights = cc.select("bene_id", pl.when(pl.col("sp_diabetes") == "1")
                      .then(2.0).otherwise(1.0).alias("weight"))
  raw = analyze_workflow(tables)
  weighted = analyze_workflow(tables, weights=weights)
  assert weighted["diabetes_prevalence"] > raw["diabetes_prevalence"]
  with pytest.raises(ValueError, match="weight"):
    analyze_workflow(tables, weights=weights.slice(1))
