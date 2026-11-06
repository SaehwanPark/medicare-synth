"""Conditional synthesizer for MVP known-truth research worlds.

Phase 1 contract: generate coherent beneficiary subgraphs with controllable
diabetes prevalence and inpatient hospitalization probabilities. Deterministic
under pinned seeds. Not a Medicare fidelity claim.
"""

from __future__ import annotations

from datetime import date, timedelta
from hashlib import sha256
from typing import Mapping

import polars as pl
from pydantic import BaseModel, ConfigDict, Field

from medicare_synth.models import ProvenanceStatus


class ConditionalWorldParams(BaseModel):
  """Pinned parameters for a diabetes → IP known-truth world."""

  model_config = ConfigDict(frozen=True)

  n_beneficiaries: int = Field(..., ge=1, le=500_000)
  seed: int = Field(..., ge=0)
  diabetes_prevalence: float = Field(..., ge=0.0, le=1.0)
  p_ip_given_diabetes: float = Field(..., ge=0.0, le=1.0)
  p_ip_given_no_diabetes: float = Field(..., ge=0.0, le=1.0)
  reference_year: int = Field(default=2021, ge=2000, le=2099)
  recovery_tolerance: float = Field(
    default=0.03,
    ge=0.0,
    le=1.0,
    description="Absolute tolerance for recovering declared probabilities.",
  )


class ConditionalWorldEstimates(BaseModel):
  """Empirical estimates recovered from a generated world."""

  model_config = ConfigDict(frozen=True)

  diabetes_prevalence: float
  p_ip_given_diabetes: float
  p_ip_given_no_diabetes: float
  risk_difference: float
  n_beneficiaries: int
  n_with_diabetes: int
  n_inpatient_claims: int


class ConditionalWorld(BaseModel):
  """Generated known-truth world plus declared parameters."""

  model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

  params: ConditionalWorldParams
  provenance_status: ProvenanceStatus = ProvenanceStatus.SYNTHESIZED
  context_id: str = "mvp-2021-om-ffs-diabetes-ip"
  beneficiary_summary: pl.DataFrame
  mbsf_base_enrollment: pl.DataFrame
  mbsf_chronic_conditions: pl.DataFrame
  inpatient_claims: pl.DataFrame

  def tables(self) -> dict[str, pl.DataFrame]:
    """Return MVP tables keyed by canonical names."""
    return {
      "beneficiary_summary": self.beneficiary_summary,
      "mbsf_base_enrollment": self.mbsf_base_enrollment,
      "mbsf_chronic_conditions": self.mbsf_chronic_conditions,
      "inpatient_claims": self.inpatient_claims,
    }


def _unit_uniform(seed: int, stream: str, index: int) -> float:
  """Deterministic Uniform(0,1) draw from seed/stream/index."""
  digest = sha256(f"{seed}:{stream}:{index}".encode()).digest()
  # 53-bit float in [0, 1)
  n = int.from_bytes(digest[:8], "big") >> 11
  return n / float(1 << 53)


def _bernoulli(seed: int, stream: str, index: int, p: float) -> bool:
  if p <= 0.0:
    return False
  if p >= 1.0:
    return True
  return _unit_uniform(seed, stream, index) < p


def _bene_id(index: int) -> str:
  # Keep within Encrypted CCW ID max_length=15.
  return f"S{index:014d}"


def _clm_id(index: int) -> str:
  return f"I{index:014d}"


def generate_diabetes_ip_world(params: ConditionalWorldParams) -> ConditionalWorld:
  """Generate a coherent MVP subgraph with controllable diabetes→IP conditionals.

  Beneficiaries are age 65+ FFS Option-B-like (full-year A/B, HMO months 0).
  Diabetes uses collapsed present code ``1``. O1 is ≥1 inpatient claim in the
  reference year.
  """
  bene_rows: list[dict[str, object]] = []
  base_rows: list[dict[str, object]] = []
  cc_rows: list[dict[str, object]] = []
  ip_rows: list[dict[str, object]] = []
  ip_seq = 0

  ref_year = params.reference_year
  year_start = date(ref_year, 1, 1)

  for i in range(params.n_beneficiaries):
    bene_id = _bene_id(i)
    has_diabetes = _bernoulli(
      params.seed, "diabetes", i, params.diabetes_prevalence
    )
    p_ip = (
      params.p_ip_given_diabetes
      if has_diabetes
      else params.p_ip_given_no_diabetes
    )
    has_ip = _bernoulli(params.seed, "ip", i, p_ip)

    # Ages 65–89 at year-end; sex/race cycle for non-degenerate demographics.
    age = 65 + int(_unit_uniform(params.seed, "age", i) * 25)
    birth = date(ref_year - age, 1 + (i % 12), 1 + (i % 28))
    sex = "1" if _unit_uniform(params.seed, "sex", i) < 0.48 else "2"
    race = str(1 + int(_unit_uniform(params.seed, "race", i) * 6) % 6)

    bene_rows.append(
      {
        "bene_id": bene_id,
        "bene_birth_dt": birth,
        "bene_death_dt": None,
        "bene_sex_ident_cd": sex,
        "bene_race_cd": race,
      }
    )
    base_rows.append(
      {
        "bene_id": bene_id,
        "rfrnc_yr": ref_year,
        "bene_hi_cvrage_tot_mons": 12,
        "bene_smi_cvrage_tot_mons": 12,
        "bene_hmo_cvrage_tot_mons": 0,
        "bene_ptd_cvrage_tot_mons": 12,
        "mdcr_entlmt_buyin_ind_01": "3",
        "dual_stus_cd_01": "00",
        "val_mbsf_base_01": 0.0,
      }
    )
    cc_rows.append(
      {
        "bene_id": bene_id,
        "rfrnc_yr": ref_year,
        "sp_alzhmd": "0",
        "sp_chf": "0",
        "sp_chrnkidn": "0",
        "sp_cncr": "0",
        "sp_diabetes": "1" if has_diabetes else "0",
        "sp_ischdmt": "0",
        "sp_strketia": "0",
        "val_mbsf_01": 0.0,
      }
    )

    if has_ip:
      los = 1 + int(_unit_uniform(params.seed, "los", i) * 7)
      day_offset = int(_unit_uniform(params.seed, "adm_day", i) * 300)
      admit = year_start + timedelta(days=day_offset)
      discharge = admit + timedelta(days=los)
      ip_rows.append(
        {
          "clm_id": _clm_id(ip_seq),
          "bene_id": bene_id,
          "clm_admsn_dt": admit,
          "nch_bene_dschrg_dt": discharge,
          "clm_pmt_amt": 1000.0 + 100.0 * los,
          "clm_utlztn_day_cnt": los,
          "clm_drg_cd": "194" if has_diabetes else "291",
        }
      )
      ip_seq += 1

  inpatient = (
    pl.DataFrame(ip_rows)
    if ip_rows
    else pl.DataFrame(
      schema={
        "clm_id": pl.Utf8,
        "bene_id": pl.Utf8,
        "clm_admsn_dt": pl.Date,
        "nch_bene_dschrg_dt": pl.Date,
        "clm_pmt_amt": pl.Float64,
        "clm_utlztn_day_cnt": pl.Int64,
        "clm_drg_cd": pl.Utf8,
      }
    )
  )

  return ConditionalWorld(
    params=params,
    beneficiary_summary=pl.DataFrame(bene_rows),
    mbsf_base_enrollment=pl.DataFrame(base_rows),
    mbsf_chronic_conditions=pl.DataFrame(cc_rows),
    inpatient_claims=inpatient,
  )


def estimate_world_relationships(
  world: ConditionalWorld,
  bene_ids: list[str] | None = None,
) -> ConditionalWorldEstimates:
  """Estimate prevalence and O1 conditionals, optionally on a beneficiary subset."""
  cc = world.mbsf_chronic_conditions
  ip = world.inpatient_claims
  if bene_ids is not None:
    id_frame = pl.DataFrame({"bene_id": bene_ids})
    cc = cc.join(id_frame, on="bene_id", how="inner")
    ip = ip.join(id_frame, on="bene_id", how="inner")

  n = cc.height
  if n == 0:
    return ConditionalWorldEstimates(
      diabetes_prevalence=0.0,
      p_ip_given_diabetes=0.0,
      p_ip_given_no_diabetes=0.0,
      risk_difference=0.0,
      n_beneficiaries=0,
      n_with_diabetes=0,
      n_inpatient_claims=ip.height,
    )

  diabetes = cc.with_columns(
    (pl.col("sp_diabetes").is_in(["1", "2"])).alias("has_diabetes")
  )
  ip_flag = (
    ip.select("bene_id")
    .unique()
    .with_columns(pl.lit(True).alias("has_ip"))
  )
  joined = diabetes.join(ip_flag, on="bene_id", how="left").with_columns(
    pl.col("has_ip").fill_null(False)
  )

  n_diab = joined.filter(pl.col("has_diabetes")).height
  n_no = n - n_diab
  ip_diab = joined.filter(pl.col("has_diabetes") & pl.col("has_ip")).height
  ip_no = joined.filter((~pl.col("has_diabetes")) & pl.col("has_ip")).height

  p_diab = n_diab / n
  p_ip_diab = (ip_diab / n_diab) if n_diab else 0.0
  p_ip_no = (ip_no / n_no) if n_no else 0.0

  return ConditionalWorldEstimates(
    diabetes_prevalence=p_diab,
    p_ip_given_diabetes=p_ip_diab,
    p_ip_given_no_diabetes=p_ip_no,
    risk_difference=p_ip_diab - p_ip_no,
    n_beneficiaries=n,
    n_with_diabetes=n_diab,
    n_inpatient_claims=ip.height,
  )


def split_bene_ids(
  world: ConditionalWorld,
  *,
  holdout_fraction: float = 0.4,
  stream: str = "split",
) -> tuple[list[str], list[str]]:
  """Deterministically partition beneficiaries into estimation vs holdout sets."""
  if not 0.0 < holdout_fraction < 1.0:
    raise ValueError("holdout_fraction must be in (0, 1)")
  estimation: list[str] = []
  holdout: list[str] = []
  for i, bene_id in enumerate(world.beneficiary_summary["bene_id"].to_list()):
    if _unit_uniform(world.params.seed, stream, i) < holdout_fraction:
      holdout.append(bene_id)
    else:
      estimation.append(bene_id)
  return estimation, holdout


def relationships_within_tolerance(
  estimates: ConditionalWorldEstimates,
  params: ConditionalWorldParams,
  *,
  check_held_out_no_diabetes: bool = True,
) -> Mapping[str, bool]:
  """Compare estimates to known-truth params using the contract tolerance."""
  tol = params.recovery_tolerance
  result = {
    "diabetes_prevalence": abs(
      estimates.diabetes_prevalence - params.diabetes_prevalence
    )
    <= tol,
    "p_ip_given_diabetes": abs(
      estimates.p_ip_given_diabetes - params.p_ip_given_diabetes
    )
    <= tol,
  }
  if check_held_out_no_diabetes:
    result["p_ip_given_no_diabetes"] = (
      abs(estimates.p_ip_given_no_diabetes - params.p_ip_given_no_diabetes)
      <= tol
    )
  return result


def unique_support_ratio(world: ConditionalWorld) -> float:
  """Fraction of beneficiaries that are unique IDs (1.0 for genuine draws)."""
  n = world.beneficiary_summary.height
  if n == 0:
    return 0.0
  return world.beneficiary_summary["bene_id"].n_unique() / float(n)
