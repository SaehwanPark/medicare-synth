"""Baseline normalizer for converting raw CMS records into canonical typed Polars DataFrames.

Parses date fields, standardizes column names, applies type conversions, and tags field lineage.
"""

from typing import Any, Sequence

import polars as pl
from medicare_synth.models import (
  BeneficiaryRecord,
  CarrierClaimLineRecord,
  InpatientClaimHeaderRecord,
  OutpatientClaimHeaderRecord,
  ProvenanceStatus,
)


class BaselineNormalizer:
  """Normalizes raw input records into canonical Polars DataFrames."""

  @staticmethod
  def normalize_beneficiaries(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw beneficiary dictionary records into a canonical Polars DataFrame."""
    validated = [BeneficiaryRecord(**r) for r in records]
    df = pl.DataFrame([v.model_dump() for v in validated])
    if df.is_empty():
      return pl.DataFrame(
        schema={
          "bene_id": pl.String,
          "bene_birth_dt": pl.Date,
          "bene_death_dt": pl.Date,
          "bene_sex_ident_cd": pl.String,
          "bene_race_cd": pl.String,
        }
      )
    return df.with_columns(
      [
        pl.col("bene_id").cast(pl.String),
        pl.col("bene_birth_dt").cast(pl.Date),
        pl.col("bene_death_dt").cast(pl.Date),
        pl.col("bene_sex_ident_cd").cast(pl.String),
        pl.col("bene_race_cd").cast(pl.String),
      ]
    )

  @staticmethod
  def normalize_carrier_claims(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw carrier claim line dictionary records into a canonical Polars DataFrame."""
    validated = [CarrierClaimLineRecord(**r) for r in records]
    df = pl.DataFrame([v.model_dump() for v in validated])
    if df.is_empty():
      return pl.DataFrame(
        schema={
          "clm_id": pl.String,
          "line_num": pl.Int64,
          "bene_id": pl.String,
          "clm_from_dt": pl.Date,
          "clm_thru_dt": pl.Date,
          "prvdr_npi": pl.String,
          "icd_dgns_cd1": pl.String,
        }
      )
    return df.with_columns(
      [
        pl.col("clm_id").cast(pl.String),
        pl.col("line_num").cast(pl.Int64),
        pl.col("bene_id").cast(pl.String),
        pl.col("clm_from_dt").cast(pl.Date),
        pl.col("clm_thru_dt").cast(pl.Date),
        pl.col("prvdr_npi").cast(pl.String),
        pl.col("icd_dgns_cd1").cast(pl.String),
      ]
    )

  @staticmethod
  def normalize_outpatient_claims(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw outpatient claim header dictionary records into a canonical Polars DataFrame."""
    validated = [OutpatientClaimHeaderRecord(**r) for r in records]
    df = pl.DataFrame([v.model_dump() for v in validated])
    if df.is_empty():
      return pl.DataFrame(
        schema={
          "clm_id": pl.String,
          "bene_id": pl.String,
          "clm_from_dt": pl.Date,
          "clm_thru_dt": pl.Date,
          "prvdr_npi": pl.String,
          "icd_dgns_cd1": pl.String,
        }
      )
    return df.with_columns(
      [
        pl.col("clm_id").cast(pl.String),
        pl.col("bene_id").cast(pl.String),
        pl.col("clm_from_dt").cast(pl.Date),
        pl.col("clm_thru_dt").cast(pl.Date),
        pl.col("prvdr_npi").cast(pl.String),
        pl.col("icd_dgns_cd1").cast(pl.String),
      ]
    )

  @staticmethod
  def normalize_inpatient_claims(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw inpatient claim header dictionary records into a canonical Polars DataFrame."""
    validated = [InpatientClaimHeaderRecord(**r) for r in records]
    df = pl.DataFrame([v.model_dump() for v in validated])
    if df.is_empty():
      return pl.DataFrame(
        schema={
          "clm_id": pl.String,
          "bene_id": pl.String,
          "clm_admsn_dt": pl.Date,
          "nch_bene_dschrg_dt": pl.Date,
          "clm_pmt_amt": pl.Float64,
          "clm_utlztn_day_cnt": pl.Int64,
          "clm_drg_cd": pl.String,
        }
      )
    return df.with_columns(
      [
        pl.col("clm_id").cast(pl.String),
        pl.col("bene_id").cast(pl.String),
        pl.col("clm_admsn_dt").cast(pl.Date),
        pl.col("nch_bene_dschrg_dt").cast(pl.Date),
        pl.col("clm_pmt_amt").cast(pl.Float64),
        pl.col("clm_utlztn_day_cnt").cast(pl.Int64),
        pl.col("clm_drg_cd").cast(pl.String),
      ]
    )

  @staticmethod
  def attach_provenance_metadata(df: pl.DataFrame, status: ProvenanceStatus) -> dict[str, Any]:
    """Generates a summary metadata object detailing table shape and provenance status."""
    return {
      "row_count": df.height,
      "columns": df.columns,
      "provenance_status": status.value,
    }
