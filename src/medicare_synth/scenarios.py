"""Scenario compiler for compiling deterministic Medicare synthetic dataset fixtures.

Supports valid baseline cohort fixtures and targeted anomaly fixtures for validator testing.
"""

from datetime import date
from typing import NamedTuple

import polars as pl


class ScenarioSlice(NamedTuple):
  """Container for a dataset slice produced by a scenario fixture."""

  bene_df: pl.DataFrame
  carrier_df: pl.DataFrame
  outpatient_df: pl.DataFrame
  inpatient_df: pl.DataFrame
  pde_df: pl.DataFrame
  snf_df: pl.DataFrame
  hha_df: pl.DataFrame
  dme_df: pl.DataFrame
  hospice_df: pl.DataFrame
  mbsf_cc_df: pl.DataFrame
  mbsf_cu_df: pl.DataFrame
  mbsf_d_df: pl.DataFrame
  mbsf_base_df: pl.DataFrame
  mbsf_oc_df: pl.DataFrame
  mbsf_ndi_df: pl.DataFrame




class ScenarioCompiler:
  """Compiles named deterministic scenarios into Polars dataset slices."""

  @staticmethod
  def valid_baseline_cohort() -> ScenarioSlice:
    """Creates a valid baseline cohort with matching beneficiary and claim records."""
    bene_df = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "bene_birth_dt": date(1950, 1, 15),
          "bene_death_dt": None,
          "bene_sex_ident_cd": "1",
          "bene_race_cd": "1",
        },
        {
          "bene_id": "BENE_002",
          "bene_birth_dt": date(1945, 6, 20),
          "bene_death_dt": None,
          "bene_sex_ident_cd": "2",
          "bene_race_cd": "2",
        },
        {
          "bene_id": "BENE_003",
          "bene_birth_dt": date(1960, 11, 5),
          "bene_death_dt": None,
          "bene_sex_ident_cd": "1",
          "bene_race_cd": "1",
        },
      ]
    )

    carrier_df = pl.DataFrame(
      [
        {
          "clm_id": "CLM_C001",
          "line_num": 1,
          "bene_id": "BENE_001",
          "clm_from_dt": date(2021, 3, 1),
          "clm_thru_dt": date(2021, 3, 5),
          "prvdr_npi": "1234567890",
          "icd_dgns_cd1": "I10",
        },
        {
          "clm_id": "CLM_C002",
          "line_num": 1,
          "bene_id": "BENE_002",
          "clm_from_dt": date(2021, 4, 10),
          "clm_thru_dt": date(2021, 4, 12),
          "prvdr_npi": "0987654321",
          "icd_dgns_cd1": "E119",
        },
      ]
    )

    outpatient_df = pl.DataFrame(
      [
        {
          "clm_id": "CLM_O001",
          "bene_id": "BENE_001",
          "clm_from_dt": date(2021, 1, 10),
          "clm_thru_dt": date(2021, 1, 10),
          "prvdr_npi": "1234567890",
          "icd_dgns_cd1": "Z0000",
        },
        {
          "clm_id": "CLM_O002",
          "bene_id": "BENE_003",
          "clm_from_dt": date(2021, 2, 1),
          "clm_thru_dt": date(2021, 2, 1),
          "prvdr_npi": "1122334455",
          "icd_dgns_cd1": "M545",
        },
      ]
    )

    inpatient_df = pl.DataFrame(
      [
        {
          "clm_id": "CLM_I001",
          "bene_id": "BENE_001",
          "clm_admsn_dt": date(2021, 5, 10),
          "nch_bene_dschrg_dt": date(2021, 5, 15),
          "clm_pmt_amt": 4500.00,
          "clm_utlztn_day_cnt": 5,
          "clm_drg_cd": "291",
        },
        {
          "clm_id": "CLM_I002",
          "bene_id": "BENE_002",
          "clm_admsn_dt": date(2021, 7, 1),
          "nch_bene_dschrg_dt": date(2021, 7, 4),
          "clm_pmt_amt": 3200.50,
          "clm_utlztn_day_cnt": 3,
          "clm_drg_cd": "194",
        },
      ]
    )

    pde_df = pl.DataFrame(
      [
        {
          "pde_id": "PDE_P001",
          "bene_id": "BENE_001",
          "srvc_dt": date(2021, 3, 10),
          "prod_srvc_id": "00093015001",
          "qty_dspnsd_num": 30.0,
          "days_suply_num": 30,
          "ptnt_pay_amt": 10.00,
          "tot_rx_cst_amt": 45.50,
        },
        {
          "pde_id": "PDE_P002",
          "bene_id": "BENE_002",
          "srvc_dt": date(2021, 4, 15),
          "prod_srvc_id": "60505132301",
          "qty_dspnsd_num": 60.0,
          "days_suply_num": 90,
          "ptnt_pay_amt": 15.00,
          "tot_rx_cst_amt": 120.00,
        },
      ]
    )

    snf_df = pl.DataFrame(
      [
        {
          "clm_id": "CLM_S001",
          "bene_id": "BENE_001",
          "clm_admsn_dt": date(2021, 6, 1),
          "nch_bene_dschrg_dt": date(2021, 6, 15),
          "clm_pmt_amt": 8500.00,
          "clm_utlztn_day_cnt": 14,
          "ncvd_days_cnt": 0,
        },
        {
          "clm_id": "CLM_S002",
          "bene_id": "BENE_002",
          "clm_admsn_dt": date(2021, 8, 5),
          "nch_bene_dschrg_dt": date(2021, 8, 12),
          "clm_pmt_amt": 4200.00,
          "clm_utlztn_day_cnt": 7,
          "ncvd_days_cnt": 0,
        },
      ]
    )

    hha_df = pl.DataFrame(
      [
        {
          "clm_id": "CLM_H001",
          "bene_id": "BENE_001",
          "clm_admsn_dt": date(2021, 4, 1),
          "nch_bene_dschrg_dt": date(2021, 4, 20),
          "clm_pmt_amt": 2500.00,
          "clm_utlztn_day_cnt": 19,
          "clm_hha_lupa_ind": "0",
        },
        {
          "clm_id": "CLM_H002",
          "bene_id": "BENE_002",
          "clm_admsn_dt": date(2021, 9, 10),
          "nch_bene_dschrg_dt": date(2021, 9, 25),
          "clm_pmt_amt": 1800.00,
          "clm_utlztn_day_cnt": 15,
          "clm_hha_lupa_ind": "0",
        },
      ]
    )

    dme_df = pl.DataFrame(
      [
        {
          "clm_id": "CLM_D001",
          "line_num": 1,
          "bene_id": "BENE_001",
          "clm_from_dt": date(2021, 2, 10),
          "clm_thru_dt": date(2021, 2, 15),
          "clm_pmt_amt": 350.00,
          "dme_line_item_count": 2,
          "line_cms_type_srvc_cd": "P",
        },
        {
          "clm_id": "CLM_D002",
          "line_num": 1,
          "bene_id": "BENE_002",
          "clm_from_dt": date(2021, 6, 1),
          "clm_thru_dt": date(2021, 6, 5),
          "clm_pmt_amt": 620.00,
          "dme_line_item_count": 1,
          "line_cms_type_srvc_cd": "P",
        },
      ]
    )

    hospice_df = pl.DataFrame(
      [
        {
          "clm_id": "CLM_HS001",
          "bene_id": "BENE_001",
          "clm_admsn_dt": date(2021, 10, 1),
          "nch_bene_dschrg_dt": date(2021, 10, 14),
          "clm_pmt_amt": 3100.00,
          "clm_utlztn_day_cnt": 13,
          "hospice_terminal_diag_cd": "C3490",
        },
        {
          "clm_id": "CLM_HS002",
          "bene_id": "BENE_002",
          "clm_admsn_dt": date(2021, 11, 5),
          "nch_bene_dschrg_dt": date(2021, 11, 25),
          "clm_pmt_amt": 4800.00,
          "clm_utlztn_day_cnt": 20,
          "hospice_terminal_diag_cd": "I509",
        },
      ]
    )

    mbsf_cc_df = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "sp_alzhmd": "1",
          "sp_chf": "1",
          "sp_chrnkidn": "2",
          "sp_cncr": "2",
          "sp_diabetes": "1",
          "sp_ischdmt": "1",
          "sp_strketia": "2",
          "val_mbsf_01": 1.0,
        },
        {
          "bene_id": "BENE_002",
          "rfrnc_yr": 2021,
          "sp_alzhmd": "2",
          "sp_chf": "2",
          "sp_chrnkidn": "1",
          "sp_cncr": "2",
          "sp_diabetes": "1",
          "sp_ischdmt": "2",
          "sp_strketia": "2",
          "val_mbsf_01": 1.0,
        },
        {
          "bene_id": "BENE_003",
          "rfrnc_yr": 2021,
          "sp_alzhmd": "2",
          "sp_chf": "2",
          "sp_chrnkidn": "2",
          "sp_cncr": "2",
          "sp_diabetes": "2",
          "sp_ischdmt": "2",
          "sp_strketia": "2",
          "val_mbsf_01": 1.0,
        },
      ]
    )

    mbsf_cu_df = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "bene_mdcr_pay_amt": 12500.0,
          "bene_tot_pay_amt": 14000.0,
          "bene_ip_ddctbl_amt": 1484.0,
          "bene_cvrd_dys_cnt": 12,
        },
        {
          "bene_id": "BENE_002",
          "rfrnc_yr": 2021,
          "bene_mdcr_pay_amt": 8200.0,
          "bene_tot_pay_amt": 9500.0,
          "bene_ip_ddctbl_amt": 0.0,
          "bene_cvrd_dys_cnt": 5,
        },
        {
          "bene_id": "BENE_003",
          "rfrnc_yr": 2021,
          "bene_mdcr_pay_amt": 450.0,
          "bene_tot_pay_amt": 500.0,
          "bene_ip_ddctbl_amt": 0.0,
          "bene_cvrd_dys_cnt": 0,
        },
      ]
    )

    mbsf_d_df = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "ptd_cntrct_id_01": "S0001",
          "ptd_pbp_id_01": "001",
          "ptd_sgnt_cd_01": "000",
          "rds_ind_01": "N",
          "li_cost_shrh_grp_cd_01": "00",
          "bene_ptd_trcc_amt": 1850.0,
          "bene_ptd_moop_amt": 420.0,
        },
        {
          "bene_id": "BENE_002",
          "rfrnc_yr": 2021,
          "ptd_cntrct_id_01": "S0002",
          "ptd_pbp_id_01": "002",
          "ptd_sgnt_cd_01": "000",
          "rds_ind_01": "N",
          "li_cost_shrh_grp_cd_01": "01",
          "bene_ptd_trcc_amt": 650.0,
          "bene_ptd_moop_amt": 150.0,
        },
        {
          "bene_id": "BENE_003",
          "rfrnc_yr": 2021,
          "ptd_cntrct_id_01": "S0001",
          "ptd_pbp_id_01": "001",
          "ptd_sgnt_cd_01": "000",
          "rds_ind_01": "Y",
          "li_cost_shrh_grp_cd_01": "00",
          "bene_ptd_trcc_amt": 0.0,
          "bene_ptd_moop_amt": 0.0,
        },
      ]
    )

    mbsf_base_df = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "bene_hi_cvrage_tot_mons": 12,
          "bene_smi_cvrage_tot_mons": 12,
          "bene_hmo_cvrage_tot_mons": 0,
          "bene_ptd_cvrage_tot_mons": 12,
          "mdcr_entlmt_buyin_ind_01": "C",
          "dual_stus_cd_01": "00",
          "val_mbsf_base_01": 1.0,
        },
        {
          "bene_id": "BENE_002",
          "rfrnc_yr": 2021,
          "bene_hi_cvrage_tot_mons": 12,
          "bene_smi_cvrage_tot_mons": 12,
          "bene_hmo_cvrage_tot_mons": 6,
          "bene_ptd_cvrage_tot_mons": 12,
          "mdcr_entlmt_buyin_ind_01": "3",
          "dual_stus_cd_01": "02",
          "val_mbsf_base_01": 1.0,
        },
        {
          "bene_id": "BENE_003",
          "rfrnc_yr": 2021,
          "bene_hi_cvrage_tot_mons": 12,
          "bene_smi_cvrage_tot_mons": 12,
          "bene_hmo_cvrage_tot_mons": 0,
          "bene_ptd_cvrage_tot_mons": 0,
          "mdcr_entlmt_buyin_ind_01": "1",
          "dual_stus_cd_01": "00",
          "val_mbsf_base_01": 1.0,
        },
      ]
    )

    mbsf_oc_df = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "sp_arthglau": "1",
          "sp_asthma": "1",
          "sp_atrialf": "2",
          "sp_hyperl": "1",
          "sp_hypert": "1",
          "sp_hypot": "2",
          "sp_osteop": "2",
          "val_mbsf_oc_01": 1.0,
        },
        {
          "bene_id": "BENE_002",
          "rfrnc_yr": 2021,
          "sp_arthglau": "2",
          "sp_asthma": "2",
          "sp_atrialf": "1",
          "sp_hyperl": "1",
          "sp_hypert": "1",
          "sp_hypot": "1",
          "sp_osteop": "2",
          "val_mbsf_oc_01": 1.0,
        },
        {
          "bene_id": "BENE_003",
          "rfrnc_yr": 2021,
          "sp_arthglau": "2",
          "sp_asthma": "2",
          "sp_atrialf": "2",
          "sp_hyperl": "2",
          "sp_hypert": "2",
          "sp_hypot": "2",
          "sp_osteop": "2",
          "val_mbsf_oc_01": 1.0,
        },
      ]
    )

    mbsf_ndi_df = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "ndi_match_ind": "0",
          "ndi_diuse_cd": None,
          "val_mbsf_ndi_01": 1.0,
        },
        {
          "bene_id": "BENE_002",
          "rfrnc_yr": 2021,
          "ndi_match_ind": "1",
          "ndi_diuse_cd": "I2510",
          "val_mbsf_ndi_01": 1.0,
        },
        {
          "bene_id": "BENE_003",
          "rfrnc_yr": 2021,
          "ndi_match_ind": "0",
          "ndi_diuse_cd": None,
          "val_mbsf_ndi_01": 1.0,
        },
      ]
    )

    return ScenarioSlice(
      bene_df=bene_df,
      carrier_df=carrier_df,
      outpatient_df=outpatient_df,
      inpatient_df=inpatient_df,
      pde_df=pde_df,
      snf_df=snf_df,
      hha_df=hha_df,
      dme_df=dme_df,
      hospice_df=hospice_df,
      mbsf_cc_df=mbsf_cc_df,
      mbsf_cu_df=mbsf_cu_df,
      mbsf_d_df=mbsf_d_df,
      mbsf_base_df=mbsf_base_df,
      mbsf_oc_df=mbsf_oc_df,
      mbsf_ndi_df=mbsf_ndi_df,
    )



  @staticmethod
  def valid_chronic_subgroup() -> ScenarioSlice:
    """Creates a valid chronic condition subgroup slice."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    bene_sub = slice_data.bene_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    carrier_sub = slice_data.carrier_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    outpatient_sub = slice_data.outpatient_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    inpatient_sub = slice_data.inpatient_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    pde_sub = slice_data.pde_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    snf_sub = slice_data.snf_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    hha_sub = slice_data.hha_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    dme_sub = slice_data.dme_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    hospice_sub = slice_data.hospice_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    mbsf_cc_sub = slice_data.mbsf_cc_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    mbsf_cu_sub = slice_data.mbsf_cu_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    mbsf_d_sub = slice_data.mbsf_d_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    mbsf_base_sub = slice_data.mbsf_base_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    mbsf_oc_sub = slice_data.mbsf_oc_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    mbsf_ndi_sub = slice_data.mbsf_ndi_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    return ScenarioSlice(
      bene_df=bene_sub,
      carrier_df=carrier_sub,
      outpatient_df=outpatient_sub,
      inpatient_df=inpatient_sub,
      pde_df=pde_sub,
      snf_df=snf_sub,
      hha_df=hha_sub,
      dme_df=dme_sub,
      hospice_df=hospice_sub,
      mbsf_cc_df=mbsf_cc_sub,
      mbsf_cu_df=mbsf_cu_sub,
      mbsf_d_df=mbsf_d_sub,
      mbsf_base_df=mbsf_base_sub,
      mbsf_oc_df=mbsf_oc_sub,
      mbsf_ndi_df=mbsf_ndi_sub,
    )


  @staticmethod
  def valid_carrier_line_item() -> ScenarioSlice:
    """Creates a valid carrier line item slice with multiple lines per claim."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    carrier_df = pl.DataFrame(
      [
        {
          "clm_id": "CLM_C001",
          "line_num": 1,
          "bene_id": "BENE_001",
          "clm_from_dt": date(2021, 3, 1),
          "clm_thru_dt": date(2021, 3, 5),
          "prvdr_npi": "1234567890",
          "icd_dgns_cd1": "I10",
        },
        {
          "clm_id": "CLM_C001",
          "line_num": 2,
          "bene_id": "BENE_001",
          "clm_from_dt": date(2021, 3, 1),
          "clm_thru_dt": date(2021, 3, 5),
          "prvdr_npi": "1234567890",
          "icd_dgns_cd1": "E119",
        },
      ]
    )
    return ScenarioSlice(
      bene_df=slice_data.bene_df,
      carrier_df=carrier_df,
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
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_orphaned_claim() -> ScenarioSlice:
    """Creates an anomaly scenario containing an orphaned claim with missing beneficiary key."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    orphaned_carrier = pl.DataFrame(
      [
        {
          "clm_id": "CLM_ORPHAN",
          "line_num": 1,
          "bene_id": "BENE_MISSING_999",
          "clm_from_dt": date(2021, 5, 1),
          "clm_thru_dt": date(2021, 5, 2),
          "prvdr_npi": "9999999999",
          "icd_dgns_cd1": "R69",
        }
      ]
    )
    return ScenarioSlice(
      bene_df=slice_data.bene_df,
      carrier_df=orphaned_carrier,
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
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_temporal_inversion() -> ScenarioSlice:
    """Creates an anomaly scenario containing a claim with temporal date inversion."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    inverted_outpatient = pl.DataFrame(
      [
        {
          "clm_id": "CLM_TEMPORAL_ERR",
          "bene_id": "BENE_001",
          "clm_from_dt": date(2021, 6, 15),
          "clm_thru_dt": date(2021, 6, 1),  # clm_from_dt > clm_thru_dt
          "prvdr_npi": "1234567890",
          "icd_dgns_cd1": "Z0000",
        }
      ]
    )
    return ScenarioSlice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=inverted_outpatient,
      inpatient_df=slice_data.inpatient_df,
      pde_df=slice_data.pde_df,
      snf_df=slice_data.snf_df,
      hha_df=slice_data.hha_df,
      dme_df=slice_data.dme_df,
      hospice_df=slice_data.hospice_df,
      mbsf_cc_df=slice_data.mbsf_cc_df,
      mbsf_cu_df=slice_data.mbsf_cu_df,
      mbsf_d_df=slice_data.mbsf_d_df,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_inpatient_admission() -> ScenarioSlice:
    """Creates an anomaly scenario containing an inpatient claim with admission date after discharge date."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    inverted_inpatient = pl.DataFrame(
      [
        {
          "clm_id": "CLM_INPATIENT_ERR",
          "bene_id": "BENE_001",
          "clm_admsn_dt": date(2021, 8, 20),
          "nch_bene_dschrg_dt": date(2021, 8, 10),  # admission > discharge
          "clm_pmt_amt": 5000.00,
          "clm_utlztn_day_cnt": 1,
          "clm_drg_cd": "291",
        }
      ]
    )
    return ScenarioSlice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=slice_data.outpatient_df,
      inpatient_df=inverted_inpatient,
      pde_df=slice_data.pde_df,
      snf_df=slice_data.snf_df,
      hha_df=slice_data.hha_df,
      dme_df=slice_data.dme_df,
      hospice_df=slice_data.hospice_df,
      mbsf_cc_df=slice_data.mbsf_cc_df,
      mbsf_cu_df=slice_data.mbsf_cu_df,
      mbsf_d_df=slice_data.mbsf_d_df,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_pde_days_supply() -> ScenarioSlice:
    """Creates an anomaly scenario containing a PDE event with invalid negative days supply."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_pde = pl.DataFrame(
      [
        {
          "pde_id": "PDE_ERR_001",
          "bene_id": "BENE_001",
          "srvc_dt": date(2021, 9, 1),
          "prod_srvc_id": "00093015001",
          "qty_dspnsd_num": 30.0,
          "days_suply_num": -10,  # Negative days supply
          "ptnt_pay_amt": 5.00,
          "tot_rx_cst_amt": 25.00,
        }
      ]
    )
    return ScenarioSlice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=slice_data.outpatient_df,
      inpatient_df=slice_data.inpatient_df,
      pde_df=invalid_pde,
      snf_df=slice_data.snf_df,
      hha_df=slice_data.hha_df,
      dme_df=slice_data.dme_df,
      hospice_df=slice_data.hospice_df,
      mbsf_cc_df=slice_data.mbsf_cc_df,
      mbsf_cu_df=slice_data.mbsf_cu_df,
      mbsf_d_df=slice_data.mbsf_d_df,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_snf_utilization_days() -> ScenarioSlice:
    """Creates an anomaly scenario containing a SNF claim with invalid negative utilization days."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_snf = pl.DataFrame(
      [
        {
          "clm_id": "CLM_SNF_ERR_001",
          "bene_id": "BENE_001",
          "clm_admsn_dt": date(2021, 6, 1),
          "nch_bene_dschrg_dt": date(2021, 6, 15),
          "clm_pmt_amt": 8500.00,
          "clm_utlztn_day_cnt": -5,  # Negative utilization days
          "ncvd_days_cnt": 0,
        }
      ]
    )
    return ScenarioSlice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=slice_data.outpatient_df,
      inpatient_df=slice_data.inpatient_df,
      pde_df=slice_data.pde_df,
      snf_df=invalid_snf,
      hha_df=slice_data.hha_df,
      dme_df=slice_data.dme_df,
      hospice_df=slice_data.hospice_df,
      mbsf_cc_df=slice_data.mbsf_cc_df,
      mbsf_cu_df=slice_data.mbsf_cu_df,
      mbsf_d_df=slice_data.mbsf_d_df,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_hha_utilization_days() -> ScenarioSlice:
    """Creates an anomaly scenario containing an HHA claim with invalid negative utilization days."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_hha = pl.DataFrame(
      [
        {
          "clm_id": "CLM_HHA_ERR_001",
          "bene_id": "BENE_001",
          "clm_admsn_dt": date(2021, 4, 1),
          "nch_bene_dschrg_dt": date(2021, 4, 20),
          "clm_pmt_amt": 2500.00,
          "clm_utlztn_day_cnt": -3,  # Negative utilization days
          "clm_hha_lupa_ind": "0",
        }
      ]
    )
    return ScenarioSlice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=slice_data.outpatient_df,
      inpatient_df=slice_data.inpatient_df,
      pde_df=slice_data.pde_df,
      snf_df=slice_data.snf_df,
      hha_df=invalid_hha,
      dme_df=slice_data.dme_df,
      hospice_df=slice_data.hospice_df,
      mbsf_cc_df=slice_data.mbsf_cc_df,
      mbsf_cu_df=slice_data.mbsf_cu_df,
      mbsf_d_df=slice_data.mbsf_d_df,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_dme_line_item_count() -> ScenarioSlice:
    """Creates an anomaly scenario containing a DME claim with invalid zero line item count."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_dme = pl.DataFrame(
      [
        {
          "clm_id": "CLM_DME_ERR_001",
          "line_num": 1,
          "bene_id": "BENE_001",
          "clm_from_dt": date(2021, 2, 10),
          "clm_thru_dt": date(2021, 2, 15),
          "clm_pmt_amt": 350.00,
          "dme_line_item_count": 0,  # Invalid zero line item count
          "line_cms_type_srvc_cd": "P",
        }
      ]
    )
    return ScenarioSlice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=slice_data.outpatient_df,
      inpatient_df=slice_data.inpatient_df,
      pde_df=slice_data.pde_df,
      snf_df=slice_data.snf_df,
      hha_df=slice_data.hha_df,
      dme_df=invalid_dme,
      hospice_df=slice_data.hospice_df,
      mbsf_cc_df=slice_data.mbsf_cc_df,
      mbsf_cu_df=slice_data.mbsf_cu_df,
      mbsf_d_df=slice_data.mbsf_d_df,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_hospice_utilization_days() -> ScenarioSlice:
    """Creates an anomaly scenario containing a Hospice claim with invalid negative utilization days."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_hospice = pl.DataFrame(
      [
        {
          "clm_id": "CLM_HOSPICE_ERR_001",
          "bene_id": "BENE_001",
          "clm_admsn_dt": date(2021, 10, 1),
          "nch_bene_dschrg_dt": date(2021, 10, 14),
          "clm_pmt_amt": 3100.00,
          "clm_utlztn_day_cnt": -4,  # Negative utilization days
          "hospice_terminal_diag_cd": "C3490",
        }
      ]
    )
    return ScenarioSlice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=slice_data.outpatient_df,
      inpatient_df=slice_data.inpatient_df,
      pde_df=slice_data.pde_df,
      snf_df=slice_data.snf_df,
      hha_df=slice_data.hha_df,
      dme_df=slice_data.dme_df,
      hospice_df=invalid_hospice,
      mbsf_cc_df=slice_data.mbsf_cc_df,
      mbsf_cu_df=slice_data.mbsf_cu_df,
      mbsf_d_df=slice_data.mbsf_d_df,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_mbsf_chronic_condition_indicator() -> ScenarioSlice:
    """Creates an anomaly scenario containing an MBSF record with invalid indicator value outside {'0', '1', '2'}."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_mbsf = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "sp_alzhmd": "9",  # Invalid value "9" outside {'0', '1', '2'}
          "sp_chf": "1",
          "sp_chrnkidn": "2",
          "sp_cncr": "2",
          "sp_diabetes": "1",
          "sp_ischdmt": "1",
          "sp_strketia": "2",
          "val_mbsf_01": 1.0,
        }
      ]
    )
    return ScenarioSlice(
      bene_df=slice_data.bene_df,
      carrier_df=slice_data.carrier_df,
      outpatient_df=slice_data.outpatient_df,
      inpatient_df=slice_data.inpatient_df,
      pde_df=slice_data.pde_df,
      snf_df=slice_data.snf_df,
      hha_df=slice_data.hha_df,
      dme_df=slice_data.dme_df,
      hospice_df=slice_data.hospice_df,
      mbsf_cc_df=invalid_mbsf,
      mbsf_cu_df=slice_data.mbsf_cu_df,
      mbsf_d_df=slice_data.mbsf_d_df,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_mbsf_cost_use_payment() -> ScenarioSlice:
    """Creates an anomaly scenario containing an MBSF Cost & Use record with negative Medicare payment amount."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_cu = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "bene_mdcr_pay_amt": -500.0,  # Invalid negative payment amount
          "bene_tot_pay_amt": 1000.0,
          "bene_ip_ddctbl_amt": 0.0,
          "bene_cvrd_dys_cnt": 0,
        }
      ]
    )
    return ScenarioSlice(
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
      mbsf_cu_df=invalid_cu,
      mbsf_d_df=slice_data.mbsf_d_df,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_mbsf_part_d_contract() -> ScenarioSlice:
    """Creates an anomaly scenario containing an MBSF Part D record with negative drug cost."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_d = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "ptd_cntrct_id_01": "S0001",
          "ptd_pbp_id_01": "001",
          "ptd_sgnt_cd_01": "000",
          "rds_ind_01": "N",
          "li_cost_shrh_grp_cd_01": "00",
          "bene_ptd_trcc_amt": -250.0,  # Invalid negative drug cost
          "bene_ptd_moop_amt": 50.0,
        }
      ]
    )
    return ScenarioSlice(
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
      mbsf_d_df=invalid_d,
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_mbsf_base_coverage_months() -> ScenarioSlice:
    """Creates an anomaly scenario containing an MBSF Base record with invalid coverage months (>12)."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_base = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "bene_hi_cvrage_tot_mons": 15,  # Invalid coverage months (>12)
          "bene_smi_cvrage_tot_mons": 12,
          "bene_hmo_cvrage_tot_mons": 0,
          "bene_ptd_cvrage_tot_mons": 12,
          "mdcr_entlmt_buyin_ind_01": "C",
          "dual_stus_cd_01": "00",
          "val_mbsf_base_01": 1.0,
        }
      ]
    )
    return ScenarioSlice(
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
      mbsf_base_df=invalid_base,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_mbsf_other_chronic_condition_indicator() -> ScenarioSlice:
    """Creates an anomaly scenario containing an MBSF Other Chronic record with invalid indicator value ('9')."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_oc = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "sp_arthglau": "9",  # Invalid indicator value (not in 0, 1, 2)
          "sp_asthma": "1",
          "sp_atrialf": "2",
          "sp_hyperl": "1",
          "sp_hypert": "1",
          "sp_hypot": "2",
          "sp_osteop": "2",
          "val_mbsf_oc_01": 1.0,
        }
      ]
    )
    return ScenarioSlice(
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
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=invalid_oc,
      mbsf_ndi_df=slice_data.mbsf_ndi_df,
    )

  @staticmethod
  def invalid_mbsf_ndi_match_indicator() -> ScenarioSlice:
    """Creates an anomaly scenario containing an MBSF NDI record with invalid match indicator ('X')."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    invalid_ndi = pl.DataFrame(
      [
        {
          "bene_id": "BENE_001",
          "rfrnc_yr": 2021,
          "ndi_match_ind": "X",  # Invalid indicator (not in '0', '1', 'Y', 'N')
          "ndi_diuse_cd": None,
          "val_mbsf_ndi_01": 1.0,
        }
      ]
    )
    return ScenarioSlice(
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
      mbsf_base_df=slice_data.mbsf_base_df,
      mbsf_oc_df=slice_data.mbsf_oc_df,
      mbsf_ndi_df=invalid_ndi,
    )

  @classmethod
  def get_scenario(cls, name: str) -> ScenarioSlice:
    """Retrieves a scenario slice by its canonical name."""
    scenarios = {
      "valid_baseline_cohort": cls.valid_baseline_cohort,
      "valid_chronic_subgroup": cls.valid_chronic_subgroup,
      "valid_carrier_line_item": cls.valid_carrier_line_item,
      "invalid_orphaned_claim": cls.invalid_orphaned_claim,
      "invalid_temporal_inversion": cls.invalid_temporal_inversion,
      "invalid_inpatient_admission": cls.invalid_inpatient_admission,
      "invalid_pde_days_supply": cls.invalid_pde_days_supply,
      "invalid_snf_utilization_days": cls.invalid_snf_utilization_days,
      "invalid_hha_utilization_days": cls.invalid_hha_utilization_days,
      "invalid_dme_line_item_count": cls.invalid_dme_line_item_count,
      "invalid_hospice_utilization_days": cls.invalid_hospice_utilization_days,
      "invalid_mbsf_chronic_condition_indicator": cls.invalid_mbsf_chronic_condition_indicator,
      "invalid_mbsf_cost_use_payment": cls.invalid_mbsf_cost_use_payment,
      "invalid_mbsf_part_d_contract": cls.invalid_mbsf_part_d_contract,
      "invalid_mbsf_base_coverage_months": cls.invalid_mbsf_base_coverage_months,
      "invalid_mbsf_other_chronic_condition_indicator": cls.invalid_mbsf_other_chronic_condition_indicator,
      "invalid_mbsf_ndi_match_indicator": cls.invalid_mbsf_ndi_match_indicator,
    }
    if name not in scenarios:
      raise ValueError(f"Unknown scenario name: '{name}'. Available: {list(scenarios.keys())}")
    return scenarios[name]()
