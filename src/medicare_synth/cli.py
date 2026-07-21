"""CLI interface for Medicare-Synth: validation, scenario compilation, evidence inspection, and release exports.
"""

import argparse
from pathlib import Path
import sys
from typing import Optional

from medicare_synth.evidence import RKBEvidenceSnapshot
from medicare_synth.manifest import SourceManifest
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator


def main(argv: Optional[list[str]] = None) -> int:
  """Main CLI entrypoint for medicare-synth."""
  parser = argparse.ArgumentParser(
    prog="medicare-synth",
    description="Medicare-Synth: Provenance-backed Medicare synthetic data and deterministic research fixtures.",
  )
  subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

  # Subcommand: validate
  val_parser = subparsers.add_parser("validate", help="Run relational and temporal validation on a scenario fixture")
  val_parser.add_argument(
    "--scenario",
    type=str,
    default="valid_baseline_cohort",
    help="Name of scenario fixture to validate (default: valid_baseline_cohort)",
  )

  # Subcommand: scenario
  scen_parser = subparsers.add_parser("scenario", help="Compile and display a deterministic scenario fixture")
  scen_parser.add_argument(
    "--name",
    type=str,
    default="valid_baseline_cohort",
    help="Name of scenario fixture to compile (default: valid_baseline_cohort)",
  )

  # Subcommand: manifest
  man_parser = subparsers.add_parser("manifest", help="Inspect source baseline manifest or evidence snapshot")
  man_parser.add_argument(
    "--type",
    choices=["baseline", "evidence"],
    default="baseline",
    help="Manifest type to display (baseline or evidence)",
  )

  # Subcommand: export
  exp_parser = subparsers.add_parser("export", help="Export scenario fixture or baseline slice to a release bundle")
  exp_parser.add_argument(
    "--scenario",
    type=str,
    default="valid_baseline_cohort",
    help="Name of scenario fixture to export (default: valid_baseline_cohort)",
  )
  exp_parser.add_argument(
    "--output-dir",
    type=str,
    required=True,
    help="Output directory path for release artifacts",
  )
  exp_parser.add_argument(
    "--format",
    choices=["csv", "parquet", "all"],
    default="all",
    help="Target export format (default: all)",
  )
  exp_parser.add_argument(
    "--release-id",
    type=str,
    default="v1.0.0-2021",
    help="Release version identifier (default: v1.0.0-2021)",
  )

  args = parser.parse_args(argv)

  if args.command == "validate":
    try:
      scenario_slice = ScenarioCompiler.get_scenario(args.scenario)
    except ValueError as e:
      print(f"Error: {e}", file=sys.stderr)
      return 1

    validator = RelationalValidator()
    report = validator.validate_slice(
      bene_df=scenario_slice.bene_df,
      carrier_df=scenario_slice.carrier_df,
      outpatient_df=scenario_slice.outpatient_df,
    )
    print(f"Scenario: {args.scenario}")
    print(f"Valid: {report.is_valid}")
    print(f"Findings Count: {len(report.findings)}")
    for f in report.findings:
      print(f"  [{f.severity.value}] {f.rule_id}: {f.message}")
    return 0 if report.is_valid else 1

  elif args.command == "scenario":
    try:
      scenario_slice = ScenarioCompiler.get_scenario(args.name)
    except ValueError as e:
      print(f"Error: {e}", file=sys.stderr)
      return 1

    print(f"Scenario Fixture: {args.name}")
    print(f"  Beneficiaries: {scenario_slice.bene_df.height} rows")
    print(f"  Carrier Claims: {scenario_slice.carrier_df.height} rows")
    print(f"  Outpatient Claims: {scenario_slice.outpatient_df.height} rows")
    return 0

  elif args.command == "manifest":
    if args.type == "baseline":
      manifest = SourceManifest.load_default_manifest()
      print(f"Baseline Collection: {manifest.collection_id}")
      print(f"Target Year: {manifest.schema_year}")
      print(f"Files: {len(manifest.files)}")
    else:
      snapshot = RKBEvidenceSnapshot.load_default_snapshot()
      print(f"Evidence Version: {snapshot.rkb_version}")
      print(f"Snapshot Date: {snapshot.snapshot_date}")
      print(f"Variables: {len(snapshot.variables)}")
    return 0

  elif args.command == "export":
    try:
      scenario_slice = ScenarioCompiler.get_scenario(args.scenario)
    except ValueError as e:
      print(f"Error: {e}", file=sys.stderr)
      return 1

    exporter = ReleaseExporter(output_dir=Path(args.output_dir), release_id=args.release_id)
    manifest = exporter.export_slice(
      bene_df=scenario_slice.bene_df,
      carrier_df=scenario_slice.carrier_df,
      outpatient_df=scenario_slice.outpatient_df,
      fmt=args.format,
    )

    print(f"Exported Release Bundle: {manifest.release_id}")
    print(f"Target Directory: {args.output_dir}")
    print(f"Validation Passed: {manifest.validation_passed}")
    print(f"Files Exported: {len(manifest.files)}")
    return 0

  else:
    parser.print_help()
    return 0


if __name__ == "__main__":
  sys.exit(main())
