"""Python Reference Analysis Workflow for Medicare-Synth Release Bundles.

Demonstrates loading provenance-backed synthetic Medicare Parquet/CSV release files,
running relational validation, and performing basic epidemiological aggregation using Polars.
"""

import sys
from pathlib import Path

# Ensure src/ is on Python module search path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import polars as pl
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator



def run_reference_analysis() -> None:
  """Executes reference Polars aggregation on compiled scenario fixtures."""
  # 1. Compile baseline scenario fixture
  slice_data = ScenarioCompiler.valid_baseline_cohort()

  bene_df = slice_data.bene_df
  carrier_df = slice_data.carrier_df
  outpatient_df = slice_data.outpatient_df

  # 2. Run Relational & Temporal Validation
  validator = RelationalValidator()
  report = validator.validate_slice(bene_df, carrier_df, outpatient_df)
  print(f"Validation Result: {'PASSED' if report.is_valid else 'FAILED'}")
  print(f"Findings Count: {len(report.findings)}")

  # 3. Perform Join & Aggregation (Carrier Claims per Beneficiary)
  carrier_agg = (
    carrier_df.group_by("bene_id")
    .agg(
      pl.len().alias("total_carrier_claims"),
      pl.col("prvdr_npi").n_unique().alias("unique_providers"),
    )
  )

  joined_df = bene_df.join(carrier_agg, on="bene_id", how="left")
  print("\nBeneficiary Carrier Summary:")
  print(joined_df.select(["bene_id", "bene_sex_ident_cd", "total_carrier_claims", "unique_providers"]))



if __name__ == "__main__":
  run_reference_analysis()
