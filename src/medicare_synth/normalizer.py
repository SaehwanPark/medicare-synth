"""Baseline normalizer for converting raw CMS records into canonical typed Polars DataFrames.

Parses date fields, standardizes column names, applies type conversions, and tags field lineage.
"""

from typing import Any, Sequence

import polars as pl
from medicare_synth.models import (
  BeneficiaryRecord,
  CarrierClaimLineRecord,
  DurableMedicalEquipmentClaimRecord,
  HomeHealthAgencyClaimRecord,
  HospiceClaimHeaderRecord,
  InpatientClaimHeaderRecord,
  MBSFChronicConditionsRecord,
  MBSFCostAndUseRecord,
  MBSFPartDRecord,
  OutpatientClaimHeaderRecord,
  PrescriptionDrugEventRecord,
  ProvenanceStatus,
  SkilledNursingFacilityClaimRecord,
)


class BaselineNormalizer:

  """Normalizes raw input records into canonical Polars DataFrames."""

  @staticmethod
  def normalize_hospice_claims(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw Hospice claim header dictionary records into a canonical Polars DataFrame."""
    validated = [HospiceClaimHeaderRecord(**r) for r in records]
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
          "hospice_terminal_diag_cd": pl.String,
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
        pl.col("hospice_terminal_diag_cd").cast(pl.String),
      ]
    )

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
  def normalize_pde_events(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw Part D Prescription Drug Event dictionary records into a canonical Polars DataFrame."""
    validated = [PrescriptionDrugEventRecord(**r) for r in records]
    df = pl.DataFrame([v.model_dump() for v in validated])
    if df.is_empty():
      return pl.DataFrame(
        schema={
          "pde_id": pl.String,
          "bene_id": pl.String,
          "srvc_dt": pl.Date,
          "prod_srvc_id": pl.String,
          "qty_dspnsd_num": pl.Float64,
          "days_suply_num": pl.Int64,
          "ptnt_pay_amt": pl.Float64,
          "tot_rx_cst_amt": pl.Float64,
        }
      )
    return df.with_columns(
      [
        pl.col("pde_id").cast(pl.String),
        pl.col("bene_id").cast(pl.String),
        pl.col("srvc_dt").cast(pl.Date),
        pl.col("prod_srvc_id").cast(pl.String),
        pl.col("qty_dspnsd_num").cast(pl.Float64),
        pl.col("days_suply_num").cast(pl.Int64),
        pl.col("ptnt_pay_amt").cast(pl.Float64),
        pl.col("tot_rx_cst_amt").cast(pl.Float64),
      ]
    )

  @staticmethod
  def normalize_snf_claims(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw SNF claim header dictionary records into a canonical Polars DataFrame."""
    validated = [SkilledNursingFacilityClaimRecord(**r) for r in records]
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
          "ncvd_days_cnt": pl.Int64,
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
        pl.col("ncvd_days_cnt").cast(pl.Int64),
      ]
    )

  @staticmethod
  def normalize_hha_claims(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw HHA claim header dictionary records into a canonical Polars DataFrame."""
    validated = [HomeHealthAgencyClaimRecord(**r) for r in records]
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
          "clm_hha_lupa_ind": pl.String,
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
        pl.col("clm_hha_lupa_ind").cast(pl.String),
      ]
    )

  @staticmethod
  def normalize_dme_claims(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw DME claim line dictionary records into a canonical Polars DataFrame."""
    validated = [DurableMedicalEquipmentClaimRecord(**r) for r in records]
    df = pl.DataFrame([v.model_dump() for v in validated])
    if df.is_empty():
      return pl.DataFrame(
        schema={
          "clm_id": pl.String,
          "line_num": pl.Int64,
          "bene_id": pl.String,
          "clm_from_dt": pl.Date,
          "clm_thru_dt": pl.Date,
          "clm_pmt_amt": pl.Float64,
          "dme_line_item_count": pl.Int64,
          "line_cms_type_srvc_cd": pl.String,
        }
      )
    return df.with_columns(
      [
        pl.col("clm_id").cast(pl.String),
        pl.col("line_num").cast(pl.Int64),
        pl.col("bene_id").cast(pl.String),
        pl.col("clm_from_dt").cast(pl.Date),
        pl.col("clm_thru_dt").cast(pl.Date),
        pl.col("clm_pmt_amt").cast(pl.Float64),
        pl.col("dme_line_item_count").cast(pl.Int64),
        pl.col("line_cms_type_srvc_cd").cast(pl.String),
      ]
    )



  @staticmethod
  def normalize_mbsf_chronic_conditions(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw MBSF Chronic Condition dictionary records into a canonical Polars DataFrame."""
    validated = [MBSFChronicConditionsRecord(**r) for r in records]
    df = pl.DataFrame([v.model_dump() for v in validated])
    if df.is_empty():
      return pl.DataFrame(
        schema={
          "bene_id": pl.String,
          "rfrnc_yr": pl.Int64,
          "sp_alzhmd": pl.String,
          "sp_chf": pl.String,
          "sp_chrnkidn": pl.String,
          "sp_cncr": pl.String,
          "sp_diabetes": pl.String,
          "sp_ischdmt": pl.String,
          "sp_strketia": pl.String,
          "val_mbsf_01": pl.Float64,
        }
      )
    return df.with_columns(
      [
        pl.col("bene_id").cast(pl.String),
        pl.col("rfrnc_yr").cast(pl.Int64),
        pl.col("sp_alzhmd").cast(pl.String),
        pl.col("sp_chf").cast(pl.String),
        pl.col("sp_chrnkidn").cast(pl.String),
        pl.col("sp_cncr").cast(pl.String),
        pl.col("sp_diabetes").cast(pl.String),
        pl.col("sp_ischdmt").cast(pl.String),
        pl.col("sp_strketia").cast(pl.String),
        pl.col("val_mbsf_01").cast(pl.Float64),
      ]
    )

  @staticmethod
  def normalize_mbsf_cost_and_use(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw MBSF Cost & Use dictionary records into a canonical Polars DataFrame."""
    validated = [MBSFCostAndUseRecord(**r) for r in records]
    df = pl.DataFrame([v.model_dump() for v in validated])
    if df.is_empty():
      return pl.DataFrame(
        schema={
          "bene_id": pl.String,
          "rfrnc_yr": pl.Int64,
          "bene_mdcr_pay_amt": pl.Float64,
          "bene_tot_pay_amt": pl.Float64,
          "bene_ip_ddctbl_amt": pl.Float64,
          "bene_cvrd_dys_cnt": pl.Int64,
        }
      )
    return df.with_columns(
      [
        pl.col("bene_id").cast(pl.String),
        pl.col("rfrnc_yr").cast(pl.Int64),
        pl.col("bene_mdcr_pay_amt").cast(pl.Float64),
        pl.col("bene_tot_pay_amt").cast(pl.Float64),
        pl.col("bene_ip_ddctbl_amt").cast(pl.Float64),
        pl.col("bene_cvrd_dys_cnt").cast(pl.Int64),
      ]
    )

  @staticmethod
  def normalize_mbsf_part_d(records: Sequence[dict[str, Any]]) -> pl.DataFrame:
    """Normalizes raw MBSF Part D dictionary records into a canonical Polars DataFrame."""
    validated = [MBSFPartDRecord(**r) for r in records]
    df = pl.DataFrame([v.model_dump() for v in validated])
    if df.is_empty():
      return pl.DataFrame(
        schema={
          "bene_id": pl.String,
          "rfrnc_yr": pl.Int64,
          "ptd_cntrct_id_01": pl.String,
          "ptd_pbp_id_01": pl.String,
          "ptd_sgnt_cd_01": pl.String,
          "rds_ind_01": pl.String,
          "li_cost_shrh_grp_cd_01": pl.String,
          "bene_ptd_trcc_amt": pl.Float64,
          "bene_ptd_moop_amt": pl.Float64,
        }
      )
    return df.with_columns(
      [
        pl.col("bene_id").cast(pl.String),
        pl.col("rfrnc_yr").cast(pl.Int64),
        pl.col("ptd_cntrct_id_01").cast(pl.String),
        pl.col("ptd_pbp_id_01").cast(pl.String),
        pl.col("ptd_sgnt_cd_01").cast(pl.String),
        pl.col("rds_ind_01").cast(pl.String),
        pl.col("li_cost_shrh_grp_cd_01").cast(pl.String),
        pl.col("bene_ptd_trcc_amt").cast(pl.Float64),
        pl.col("bene_ptd_moop_amt").cast(pl.Float64),
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
