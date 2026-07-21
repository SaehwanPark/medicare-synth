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

    return ScenarioSlice(
      bene_df=bene_df,
      carrier_df=carrier_df,
      outpatient_df=outpatient_df,
      inpatient_df=inpatient_df,
      pde_df=pde_df,
      snf_df=snf_df,
      hha_df=hha_df,
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
    return ScenarioSlice(
      bene_df=bene_sub,
      carrier_df=carrier_sub,
      outpatient_df=outpatient_sub,
      inpatient_df=inpatient_sub,
      pde_df=pde_sub,
      snf_df=snf_sub,
      hha_df=hha_sub,
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
    }
    if name not in scenarios:
      raise ValueError(f"Unknown scenario name: '{name}'. Available: {list(scenarios.keys())}")
    return scenarios[name]()
