"""Scenario catalog and teaching/CI fixture generator.

Provides a structured catalog of named scenario fixtures and automated export of
lightweight CI test fixtures.
"""

from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from medicare_synth.scenarios import ScenarioCompiler, ScenarioSlice


class ScenarioEntry(BaseModel):
  """Metadata entry describing a scenario fixture in the catalog."""

  name: str = Field(description="Unique scenario name identifier.")
  description: str = Field(description="Detailed explanation of the scenario purpose and invariants.")
  is_valid: bool = Field(description="True if scenario represents valid data; False if intentional anomaly.")
  expected_findings_count: int = Field(description="Number of validator findings expected when validating this scenario.")
  target_files: List[str] = Field(description="Medicare file grains represented in this scenario slice.")
  sample_bene_count: int = Field(description="Number of beneficiary records in the scenario slice.")
  sample_claim_count: int = Field(description="Total number of claim records (carrier + outpatient) in the slice.")


class ScenarioCatalog:
  """Catalog providing metadata inspection and CI fixture export capabilities."""

  _CATALOG: Dict[str, ScenarioEntry] = {
    "valid_baseline_cohort": ScenarioEntry(
      name="valid_baseline_cohort",
      description="Valid baseline cohort with matching beneficiary and claim records across carrier, outpatient, and inpatient files.",
      is_valid=True,
      expected_findings_count=0,
      target_files=["beneficiary_summary", "carrier_claims", "outpatient_claims", "inpatient_claims"],
      sample_bene_count=3,
      sample_claim_count=5,
    ),
    "valid_chronic_subgroup": ScenarioEntry(
      name="valid_chronic_subgroup",
      description="Valid subgroup focusing on chronic condition tracking and outpatient/inpatient encounters.",
      is_valid=True,
      expected_findings_count=0,
      target_files=["beneficiary_summary", "outpatient_claims", "inpatient_claims"],
      sample_bene_count=2,
      sample_claim_count=4,
    ),
    "valid_carrier_line_item": ScenarioEntry(
      name="valid_carrier_line_item",
      description="Valid detailed carrier line-item claim records with valid NPI providers.",
      is_valid=True,
      expected_findings_count=0,
      target_files=["beneficiary_summary", "carrier_claims", "inpatient_claims"],
      sample_bene_count=2,
      sample_claim_count=4,
    ),
    "invalid_orphaned_claim": ScenarioEntry(
      name="invalid_orphaned_claim",
      description="Intentional anomaly fixture containing a claim referencing a non-existent beneficiary ID.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "carrier_claims"],
      sample_bene_count=1,
      sample_claim_count=2,
    ),
    "invalid_temporal_inversion": ScenarioEntry(
      name="invalid_temporal_inversion",
      description="Intentional anomaly fixture with claim end date preceding claim start date.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "outpatient_claims"],
      sample_bene_count=1,
      sample_claim_count=1,
    ),
    "invalid_inpatient_admission": ScenarioEntry(
      name="invalid_inpatient_admission",
      description="Intentional anomaly fixture with inpatient admission date after discharge date.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "inpatient_claims"],
      sample_bene_count=1,
      sample_claim_count=1,
    ),
    "invalid_pde_days_supply": ScenarioEntry(
      name="invalid_pde_days_supply",
      description="Intentional anomaly fixture containing a PDE event with invalid negative days supply.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "pde_events"],
      sample_bene_count=1,
      sample_claim_count=1,
    ),
    "invalid_snf_utilization_days": ScenarioEntry(
      name="invalid_snf_utilization_days",
      description="Intentional anomaly fixture containing a SNF claim with invalid negative utilization days.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "snf_claims"],
      sample_bene_count=1,
      sample_claim_count=1,
    ),
    "invalid_hha_utilization_days": ScenarioEntry(
      name="invalid_hha_utilization_days",
      description="Intentional anomaly fixture containing an HHA claim with invalid negative utilization days.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "hha_claims"],
      sample_bene_count=1,
      sample_claim_count=1,
    ),
    "invalid_dme_line_item_count": ScenarioEntry(
      name="invalid_dme_line_item_count",
      description="Intentional anomaly fixture containing a DME claim with invalid zero line item count.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "dme_claims"],
      sample_bene_count=1,
      sample_claim_count=1,
    ),
    "invalid_hospice_utilization_days": ScenarioEntry(
      name="invalid_hospice_utilization_days",
      description="Intentional anomaly fixture containing a Hospice claim with invalid negative utilization days.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "hospice_claims"],
      sample_bene_count=1,
      sample_claim_count=1,
    ),
    "invalid_mbsf_chronic_condition_indicator": ScenarioEntry(
      name="invalid_mbsf_chronic_condition_indicator",
      description="Intentional anomaly fixture containing an MBSF record with invalid indicator value outside {'0', '1', '2'}.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "mbsf_chronic_conditions"],
      sample_bene_count=1,
      sample_claim_count=1,
    ),
    "invalid_mbsf_cost_use_payment": ScenarioEntry(
      name="invalid_mbsf_cost_use_payment",
      description="Intentional anomaly fixture containing an MBSF Cost & Use record with negative payment amount.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "mbsf_cost_and_use"],
      sample_bene_count=1,
      sample_claim_count=1,
    ),
    "invalid_mbsf_part_d_contract": ScenarioEntry(
      name="invalid_mbsf_part_d_contract",
      description="Intentional anomaly fixture containing an MBSF Part D record with negative drug cost amount.",
      is_valid=False,
      expected_findings_count=1,
      target_files=["beneficiary_summary", "mbsf_part_d"],
      sample_bene_count=1,
      sample_claim_count=1,
    ),
  }

  @classmethod
  def get_catalog(cls) -> List[ScenarioEntry]:
    """Returns all entries in the scenario catalog."""
    return list(cls._CATALOG.values())

  @classmethod
  def get_scenario_info(cls, name: str) -> Optional[ScenarioEntry]:
    """Retrieves metadata for a specific scenario by name."""
    return cls._CATALOG.get(name)

  @classmethod
  def export_ci_fixtures(cls, output_dir: str | Path, file_format: str = "parquet") -> List[Path]:
    """Exports all scenario slices to the specified output directory as CI fixtures.

    Args:
      output_dir: Directory path to save exported CI fixture files.
      file_format: Output file format ('parquet' or 'csv').

    Returns:
      List of created file paths.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    created_files: List[Path] = []

    compiler_methods = {
      "valid_baseline_cohort": ScenarioCompiler.valid_baseline_cohort,
      "valid_chronic_subgroup": ScenarioCompiler.valid_chronic_subgroup,
      "valid_carrier_line_item": ScenarioCompiler.valid_carrier_line_item,
      "invalid_orphaned_claim": ScenarioCompiler.invalid_orphaned_claim,
      "invalid_temporal_inversion": ScenarioCompiler.invalid_temporal_inversion,
      "invalid_inpatient_admission": ScenarioCompiler.invalid_inpatient_admission,
      "invalid_pde_days_supply": ScenarioCompiler.invalid_pde_days_supply,
      "invalid_snf_utilization_days": ScenarioCompiler.invalid_snf_utilization_days,
      "invalid_hha_utilization_days": ScenarioCompiler.invalid_hha_utilization_days,
      "invalid_dme_line_item_count": ScenarioCompiler.invalid_dme_line_item_count,
      "invalid_hospice_utilization_days": ScenarioCompiler.invalid_hospice_utilization_days,
      "invalid_mbsf_chronic_condition_indicator": ScenarioCompiler.invalid_mbsf_chronic_condition_indicator,
      "invalid_mbsf_cost_use_payment": ScenarioCompiler.invalid_mbsf_cost_use_payment,
      "invalid_mbsf_part_d_contract": ScenarioCompiler.invalid_mbsf_part_d_contract,
    }

    for name, method in compiler_methods.items():
      slice_data: ScenarioSlice = method()
      scenario_dir = out_path / name
      scenario_dir.mkdir(parents=True, exist_ok=True)

      tables = [
        ("beneficiary_summary", slice_data.bene_df),
        ("carrier_claims", slice_data.carrier_df),
        ("outpatient_claims", slice_data.outpatient_df),
        ("inpatient_claims", slice_data.inpatient_df),
        ("pde_events", slice_data.pde_df),
        ("snf_claims", slice_data.snf_df),
        ("hha_claims", slice_data.hha_df),
        ("dme_claims", slice_data.dme_df),
        ("hospice_claims", slice_data.hospice_df),
        ("mbsf_chronic_conditions", slice_data.mbsf_cc_df),
        ("mbsf_cost_and_use", slice_data.mbsf_cu_df),
        ("mbsf_part_d", slice_data.mbsf_d_df),
      ]

      for table_name, df in tables:
        if df.is_empty():
          continue
        if file_format.lower() == "csv":
          file_file = scenario_dir / f"{table_name}.csv"
          df.write_csv(file_file)
        else:
          file_file = scenario_dir / f"{table_name}.parquet"
          df.write_parquet(file_file)
        created_files.append(file_file)

    return created_files
