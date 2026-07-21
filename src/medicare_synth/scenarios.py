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

    return ScenarioSlice(bene_df=bene_df, carrier_df=carrier_df, outpatient_df=outpatient_df)

  @staticmethod
  def valid_chronic_subgroup() -> ScenarioSlice:
    """Creates a valid chronic condition subgroup slice."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    # Filter to BENE_001 and BENE_002
    bene_sub = slice_data.bene_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    carrier_sub = slice_data.carrier_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    outpatient_sub = slice_data.outpatient_df.filter(pl.col("bene_id").is_in(["BENE_001", "BENE_002"]))
    return ScenarioSlice(bene_df=bene_sub, carrier_df=carrier_sub, outpatient_df=outpatient_sub)

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
    return ScenarioSlice(bene_df=slice_data.bene_df, carrier_df=carrier_df, outpatient_df=slice_data.outpatient_df)

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
    }
    if name not in scenarios:
      raise ValueError(f"Unknown scenario name: '{name}'. Available: {list(scenarios.keys())}")
    return scenarios[name]()
