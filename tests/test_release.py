"""Unit tests for ReleaseExporter, FidelityProfile, and release CLI subcommand.
"""

import json
from pathlib import Path

from medicare_synth import FidelityProfile, ReleaseExporter, ScenarioCompiler
from medicare_synth.cli import main as cli_main


def test_release_exporter_export_all(tmp_path: Path):
  """Test exporting a scenario slice to CSV, Parquet, and metadata files."""
  slice_data = ScenarioCompiler.get_scenario("valid_baseline_cohort")
  exporter = ReleaseExporter(output_dir=tmp_path, release_id="v1.0.0-test")

  manifest = exporter.export_slice(
    bene_df=slice_data.bene_df,
    carrier_df=slice_data.carrier_df,
    outpatient_df=slice_data.outpatient_df,
    fmt="all",
  )

  assert manifest.release_id == "v1.0.0-test"
  assert manifest.validation_passed is True
  assert len(manifest.files) == 6  # 3 tables x 2 formats

  # Check generated metadata files
  assert (tmp_path / "release_manifest.json").exists()
  assert (tmp_path / "validation_report.json").exists()
  assert (tmp_path / "fidelity_profile.json").exists()
  assert (tmp_path / "sql_reference_schema.sql").exists()

  # Check tabular data files
  assert (tmp_path / "beneficiary.csv").exists()
  assert (tmp_path / "beneficiary.parquet").exists()
  assert (tmp_path / "carrier.csv").exists()
  assert (tmp_path / "carrier.parquet").exists()
  assert (tmp_path / "outpatient.csv").exists()
  assert (tmp_path / "outpatient.parquet").exists()


def test_fidelity_profile_computation(tmp_path: Path):
  """Test fidelity profile metric calculation on valid vs invalid scenarios."""
  valid_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
  exporter = ReleaseExporter(output_dir=tmp_path)

  manifest_valid = exporter.export_slice(
    bene_df=valid_slice.bene_df,
    carrier_df=valid_slice.carrier_df,
    outpatient_df=valid_slice.outpatient_df,
  )

  assert manifest_valid.validation_passed is True

  with open(tmp_path / "fidelity_profile.json") as f:
    fidelity_data = json.load(f)

  profile = FidelityProfile(**fidelity_data)
  assert profile.bene_count == 3
  assert profile.carrier_claim_count == 2
  assert profile.outpatient_claim_count == 2
  assert profile.foreign_key_validity_rate == 1.0
  assert profile.temporal_integrity_rate == 1.0


def test_cli_export(tmp_path: Path):
  """Test medicare-synth export CLI subcommand."""
  exit_code = cli_main([
    "export",
    "--scenario",
    "valid_baseline_cohort",
    "--output-dir",
    str(tmp_path),
    "--format",
    "parquet",
  ])

  assert exit_code == 0
  assert (tmp_path / "beneficiary.parquet").exists()
  assert (tmp_path / "carrier.parquet").exists()
  assert (tmp_path / "outpatient.parquet").exists()
  assert (tmp_path / "release_manifest.json").exists()
