"""Preregistered Phase 6 beneficiary-grain workflow; not Medicare inference."""

from __future__ import annotations

import math
from typing import Mapping, TypedDict

import polars as pl

from medicare_synth.calibration import validate_beneficiary_weights
from medicare_synth.evidence_ir import (
  EligibilityPlan,
  FfsRule,
  admissions_in_year,
  eligible_bene_ids,
  validate_analysis_tables,
)


class WorkflowResult(TypedDict):
  n_eligible: int
  n_diabetes: int
  n_no_diabetes: int
  n_ip_beneficiaries: int
  diabetes_prevalence: float
  hf_prevalence: float
  ip_risk: float
  ip_given_diabetes: float | None
  ip_given_no_diabetes: float | None
  weight_sum: float


def analyze_workflow(
  tables: Mapping[str, pl.DataFrame], *, weights: pl.DataFrame | None = None
) -> WorkflowResult:
  """Run one Option B, 2021 beneficiary-level analysis on raw or weighted rows."""
  validate_analysis_tables(tables, 2021, (
    "beneficiary_summary", "mbsf_base_enrollment", "mbsf_chronic_conditions", "inpatient_claims"
  ))
  plan = EligibilityPlan(
    age_minimum=65, reference_year=2021, require_full_year_ab=True,
    require_zero_hmo_months=True, ffs_rule=FfsRule.OPTION_B_FULL_YEAR,
  )
  eligible = eligible_bene_ids(tables, plan)
  if eligible.height == 0:
    raise ValueError("workflow eligible cohort is empty")
  beneficiaries = tables["beneficiary_summary"].select("bene_id")
  weights = weights if weights is not None else beneficiaries.with_columns(pl.lit(1.0).alias("weight"))
  validate_beneficiary_weights(beneficiaries, weights)
  cc = tables["mbsf_chronic_conditions"].select(
    "bene_id", pl.col("sp_diabetes").is_in(["1", "2"]).alias("diabetes"),
    pl.col("sp_chf").is_in(["1", "2"]).alias("hf"),
  )
  ip = admissions_in_year(tables["inpatient_claims"], 2021).select("bene_id").unique().with_columns(
    pl.lit(True).alias("ip")
  )
  frame = (eligible.join(cc, on="bene_id").join(ip, on="bene_id", how="left")
           .join(weights, on="bene_id").with_columns(pl.col("ip").fill_null(False))
           .sort("bene_id").rechunk())
  values = frame.select("diabetes", "hf", "ip", "weight").iter_rows()
  rows = [(bool(d), bool(h), bool(i), float(w)) for d, h, i, w in values]
  total = math.fsum(w for _, _, _, w in rows)
  if total <= 0:
    raise ValueError("eligible workflow weight is zero")
  diab = [(d, h, i, w) for d, h, i, w in rows if d]
  no_diab = [(d, h, i, w) for d, h, i, w in rows if not d]
  def risk(group: list[tuple[bool, bool, bool, float]]) -> float | None:
    mass = math.fsum(w for _, _, _, w in group)
    return math.fsum(w for _, _, i, w in group if i) / mass if mass > 0 else None
  return {
    "n_eligible": len(rows),
    "n_diabetes": len(diab),
    "n_no_diabetes": len(no_diab),
    "n_ip_beneficiaries": sum(1 for _, _, i, _ in rows if i),
    "diabetes_prevalence": math.fsum(w for d, _, _, w in rows if d) / total,
    "hf_prevalence": math.fsum(w for _, h, _, w in rows if h) / total,
    "ip_risk": math.fsum(w for _, _, i, w in rows if i) / total,
    "ip_given_diabetes": risk(diab),
    "ip_given_no_diabetes": risk(no_diab),
    "weight_sum": total,
  }
