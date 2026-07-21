"""CLI interface for Medicare-Synth: validation, scenario compilation, evidence inspection, release exports, dataset expansion, and privacy auditing.

Executes subcommands for validating relational/temporal integrity, compiling deterministic
scenario slices, loading source/evidence manifests, exporting versioned release bundles,
scaling subgraphs vertically/horizontally, diffing schema snapshots, and auditing k-anonymity.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import Optional

from medicare_synth.audit import AuditEngine
from medicare_synth.catalog import ScenarioCatalog
from medicare_synth.diff import SchemaDiffer
from medicare_synth.evidence import RKBEvidenceSnapshot
from medicare_synth.expansion import HorizontalExpander, VerticalExpander
from medicare_synth.manifest import SourceManifest
from medicare_synth.profile import LimitationsProfiler
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator
from medicare_synth.workflow import run_autonomous_workflow


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entrypoint for medicare-synth."""
    parser = argparse.ArgumentParser(
        prog="medicare-synth",
        description="Medicare-Synth: Provenance-backed Medicare synthetic data and deterministic research fixtures.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: validate
    val_parser = subparsers.add_parser(
        "validate", help="Run relational and temporal validation on a scenario fixture"
    )
    val_parser.add_argument(
        "--scenario",
        type=str,
        default="valid_baseline_cohort",
        help="Name of scenario fixture to validate (default: valid_baseline_cohort)",
    )
    val_parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Optional output directory path to save validation_report.json",
    )

    # Subcommand: scenario
    scen_parser = subparsers.add_parser(
        "scenario", help="Compile and display a deterministic scenario fixture"
    )
    scen_parser.add_argument(
        "--name",
        type=str,
        default="valid_baseline_cohort",
        help="Name of scenario fixture to compile (default: valid_baseline_cohort)",
    )

    # Subcommand: manifest
    man_parser = subparsers.add_parser(
        "manifest", help="Inspect source baseline manifest or evidence snapshot"
    )
    man_parser.add_argument(
        "--type",
        choices=["baseline", "evidence"],
        default="baseline",
        help="Manifest type to display (baseline or evidence)",
    )

    # Subcommand: export
    exp_parser = subparsers.add_parser(
        "export", help="Export scenario fixture or baseline slice to a release bundle"
    )
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

    # Subcommand: expand
    expand_parser = subparsers.add_parser(
        "expand",
        help="Perform vertical feature expansion or horizontal subgraph scaling",
    )
    expand_parser.add_argument(
        "--mode",
        choices=["vertical", "horizontal"],
        default="horizontal",
        help="Expansion mode (vertical or horizontal)",
    )
    expand_parser.add_argument(
        "--scenario",
        type=str,
        default="valid_baseline_cohort",
        help="Scenario fixture to use as base cohort (default: valid_baseline_cohort)",
    )
    expand_parser.add_argument(
        "--scale",
        type=int,
        default=2,
        help="Scale factor for horizontal expansion (default: 2)",
    )

    # Subcommand: catalog
    cat_parser = subparsers.add_parser(
        "catalog", help="List named scenario fixtures and metadata"
    )
    cat_parser.add_argument(
        "--json", action="store_true", help="Output catalog in JSON format"
    )

    # Subcommand: diff
    diff_parser = subparsers.add_parser(
        "diff", help="Diff two RKB evidence snapshot contracts or schema files"
    )
    diff_parser.add_argument(
        "--source-a", type=str, required=True, help="Path to first snapshot JSON file"
    )
    diff_parser.add_argument(
        "--source-b", type=str, required=True, help="Path to second snapshot JSON file"
    )

    # Subcommand: profile
    prof_parser = subparsers.add_parser(
        "profile", help="Generate dataset limitations disclosure profile"
    )
    prof_parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Output directory for limitations profile",
    )

    # Subcommand: export-ci
    ci_parser = subparsers.add_parser(
        "export-ci", help="Export CI test fixtures for all catalog scenarios"
    )
    ci_parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Output directory path for CI fixtures",
    )
    ci_parser.add_argument(
        "--format",
        choices=["csv", "parquet"],
        default="parquet",
        help="CI fixture format (default: parquet)",
    )

    # Subcommand: audit
    audit_parser = subparsers.add_parser(
        "audit", help="Run data quality and privacy audit on a scenario fixture"
    )
    audit_parser.add_argument(
        "--scenario",
        type=str,
        default="valid_baseline_cohort",
        help="Name of scenario fixture to audit (default: valid_baseline_cohort)",
    )
    audit_parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Optional output directory path to save audit_report.json",
    )

    # Subcommand: auto-workflow
    auto_wf_parser = subparsers.add_parser(
        "auto-workflow",
        help="Run local verification and autonomously stage, commit, push, PR, and merge",
    )
    auto_wf_parser.add_argument(
        "--commit-msg",
        type=str,
        default="feat: implement autonomous workflow subcommand and reconcile docs",
        help="Commit message to use for git commit",
    )
    auto_wf_parser.add_argument(
        "--title",
        type=str,
        default="feat: implement autonomous workflow subcommand and reconcile docs",
        help="Pull request title",
    )
    auto_wf_parser.add_argument(
        "--body",
        type=str,
        default="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
        help="Pull request body",
    )
    auto_wf_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate code and show git commands but do not commit, push, or merge",
    )
    auto_wf_parser.add_argument(
        "--skip-merge",
        action="store_true",
        help="Create the PR but skip the autonomous merge step",
    )
    auto_wf_parser.add_argument(
        "--json-report",
        type=str,
        default=None,
        help="Optional path to write a JSON summary execution report",
    )
    auto_wf_parser.add_argument(
        "--md-report",
        type=str,
        default=None,
        help="Optional path to write a Markdown summary execution report",
    )
    auto_wf_parser.add_argument(
        "--changelog-check",
        action="store_true",
        help="Verify CHANGELOG.md contains uncommitted modifications before commit/push",
    )
    auto_wf_parser.add_argument(
        "--git-clean-check",
        action="store_true",
        help="Verify git working tree status check step before staging/committing",
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
            inpatient_df=scenario_slice.inpatient_df,
            pde_df=scenario_slice.pde_df,
            snf_df=scenario_slice.snf_df,
            hha_df=scenario_slice.hha_df,
            dme_df=scenario_slice.dme_df,
            hospice_df=scenario_slice.hospice_df,
            mbsf_cc_df=scenario_slice.mbsf_cc_df,
            mbsf_cu_df=scenario_slice.mbsf_cu_df,
            mbsf_d_df=scenario_slice.mbsf_d_df,
            mbsf_base_df=scenario_slice.mbsf_base_df,
            mbsf_oc_df=scenario_slice.mbsf_oc_df,
            mbsf_ndi_df=scenario_slice.mbsf_ndi_df,
            mbsf_ra_df=scenario_slice.mbsf_ra_df,
            mbsf_c_df=scenario_slice.mbsf_c_df,
            mbsf_ffs_df=scenario_slice.mbsf_ffs_df,
            mbsf_pde_util_df=scenario_slice.mbsf_pde_util_df,
        )
        if args.output_dir:
            out_dir = Path(args.output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / "validation_report.json"
            out_file.write_text(report.model_dump_json(indent=2), encoding="utf-8")
            print(f"Validation report saved to: {out_file}")

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
        print(f"  Inpatient Claims: {scenario_slice.inpatient_df.height} rows")
        print(f"  Prescription Drug Events: {scenario_slice.pde_df.height} rows")
        print(f"  SNF Claims: {scenario_slice.snf_df.height} rows")
        print(f"  HHA Claims: {scenario_slice.hha_df.height} rows")
        print(f"  DME Claims: {scenario_slice.dme_df.height} rows")
        print(f"  Hospice Claims: {scenario_slice.hospice_df.height} rows")
        print(f"  MBSF Chronic Conditions: {scenario_slice.mbsf_cc_df.height} rows")
        print(f"  MBSF Cost & Use: {scenario_slice.mbsf_cu_df.height} rows")
        print(f"  MBSF Part D: {scenario_slice.mbsf_d_df.height} rows")
        print(f"  MBSF Base Enrollment: {scenario_slice.mbsf_base_df.height} rows")
        print(
            f"  MBSF Other Chronic Conditions: {scenario_slice.mbsf_oc_df.height} rows"
        )
        print(f"  MBSF NDI: {scenario_slice.mbsf_ndi_df.height} rows")
        print(f"  MBSF Risk Adjustment: {scenario_slice.mbsf_ra_df.height} rows")
        print(f"  MBSF Part C: {scenario_slice.mbsf_c_df.height} rows")
        print(f"  MBSF FFS Utilization: {scenario_slice.mbsf_ffs_df.height} rows")
        print(
            f"  MBSF Part D PDE Utilization: {scenario_slice.mbsf_pde_util_df.height} rows"
        )
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

        exporter = ReleaseExporter(
            output_dir=Path(args.output_dir), release_id=args.release_id
        )
        manifest = exporter.export_slice(
            bene_df=scenario_slice.bene_df,
            carrier_df=scenario_slice.carrier_df,
            outpatient_df=scenario_slice.outpatient_df,
            fmt=args.format,
            inpatient_df=scenario_slice.inpatient_df,
            pde_df=scenario_slice.pde_df,
            snf_df=scenario_slice.snf_df,
            hha_df=scenario_slice.hha_df,
            dme_df=scenario_slice.dme_df,
            hospice_df=scenario_slice.hospice_df,
            mbsf_cc_df=scenario_slice.mbsf_cc_df,
            mbsf_cu_df=scenario_slice.mbsf_cu_df,
            mbsf_d_df=scenario_slice.mbsf_d_df,
            mbsf_base_df=scenario_slice.mbsf_base_df,
            mbsf_oc_df=scenario_slice.mbsf_oc_df,
            mbsf_ndi_df=scenario_slice.mbsf_ndi_df,
            mbsf_ra_df=scenario_slice.mbsf_ra_df,
            mbsf_c_df=scenario_slice.mbsf_c_df,
            mbsf_ffs_df=scenario_slice.mbsf_ffs_df,
            mbsf_pde_util_df=scenario_slice.mbsf_pde_util_df,
        )

        print(f"Exported Release Bundle: {manifest.release_id}")
        print(f"Target Directory: {args.output_dir}")
        print(f"Validation Passed: {manifest.validation_passed}")
        print(f"Files Exported: {len(manifest.files)}")
        return 0

    elif args.command == "expand":
        try:
            scenario_slice = ScenarioCompiler.get_scenario(args.scenario)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        tables = {
            "beneficiary_summary": scenario_slice.bene_df,
            "carrier_claims": scenario_slice.carrier_df,
            "outpatient_claims": scenario_slice.outpatient_df,
            "inpatient_claims": scenario_slice.inpatient_df,
            "pde_events": scenario_slice.pde_df,
            "snf_claims": scenario_slice.snf_df,
            "hha_claims": scenario_slice.hha_df,
            "dme_claims": scenario_slice.dme_df,
            "hospice_claims": scenario_slice.hospice_df,
            "mbsf_chronic_conditions": scenario_slice.mbsf_cc_df,
            "mbsf_cost_and_use": scenario_slice.mbsf_cu_df,
            "mbsf_part_d": scenario_slice.mbsf_d_df,
            "mbsf_base_enrollment": scenario_slice.mbsf_base_df,
            "mbsf_other_chronic_conditions": scenario_slice.mbsf_oc_df,
            "mbsf_ndi": scenario_slice.mbsf_ndi_df,
            "mbsf_risk_adjustment": scenario_slice.mbsf_ra_df,
            "mbsf_part_c": scenario_slice.mbsf_c_df,
            "mbsf_ffs_utilization": scenario_slice.mbsf_ffs_df,
            "mbsf_pde_utilization": scenario_slice.mbsf_pde_util_df,
        }

        if args.mode == "vertical":
            expander = VerticalExpander()
            expanded = expander.expand_slice(tables)
            print(f"Vertical Expansion ({args.scenario}):")
            print(
                f"  Beneficiary summary columns: {expanded['beneficiary_summary'].columns}"
            )
        else:
            expander = HorizontalExpander()
            expanded = expander.expand_subgraph(tables, scale_factor=args.scale)
            print(
                f"Horizontal Subgraph Expansion ({args.scenario}, scale={args.scale}):"
            )
            print(f"  Beneficiaries: {expanded['beneficiary_summary'].height} rows")
            print(f"  Carrier Claims: {expanded['carrier_claims'].height} rows")
            print(f"  Outpatient Claims: {expanded['outpatient_claims'].height} rows")
            print(f"  Inpatient Claims: {expanded['inpatient_claims'].height} rows")
            print(f"  Prescription Drug Events: {expanded['pde_events'].height} rows")
            print(f"  SNF Claims: {expanded['snf_claims'].height} rows")
            print(f"  HHA Claims: {expanded['hha_claims'].height} rows")
            print(f"  DME Claims: {expanded['dme_claims'].height} rows")
            print(f"  Hospice Claims: {expanded['hospice_claims'].height} rows")
            print(
                f"  MBSF Chronic Conditions: {expanded['mbsf_chronic_conditions'].height} rows"
            )
            print(f"  MBSF Cost & Use: {expanded['mbsf_cost_and_use'].height} rows")
            print(f"  MBSF Part D: {expanded['mbsf_part_d'].height} rows")
            print(
                f"  MBSF Base Enrollment: {expanded['mbsf_base_enrollment'].height} rows"
            )
            print(
                f"  MBSF Other Chronic Conditions: {expanded['mbsf_other_chronic_conditions'].height} rows"
            )
            print(f"  MBSF NDI: {expanded['mbsf_ndi'].height} rows")
            print(
                f"  MBSF Risk Adjustment: {expanded['mbsf_risk_adjustment'].height} rows"
            )
            print(f"  MBSF Part C: {expanded['mbsf_part_c'].height} rows")
            print(
                f"  MBSF FFS Utilization: {expanded['mbsf_ffs_utilization'].height} rows"
            )
            print(
                f"  MBSF Part D PDE Utilization: {expanded['mbsf_pde_utilization'].height} rows"
            )
        return 0

    elif args.command == "catalog":
        entries = ScenarioCatalog.get_catalog()
        if args.json:
            print(json.dumps([e.model_dump() for e in entries], indent=2))
        else:
            print(f"Medicare-Synth Scenario Catalog ({len(entries)} scenarios):")
            for e in entries:
                status = "VALID" if e.is_valid else "ANOMALY"
                print(f"  [{status}] {e.name}: {e.description}")
        return 0

    elif args.command == "diff":
        report = SchemaDiffer.compare_files(Path(args.source_a), Path(args.source_b))
        print(
            f"Schema Diff Report ({report.snapshot_a_version} -> {report.snapshot_b_version}):"
        )
        print(f"  Has Breaking Changes: {report.has_breaking_changes}")
        print(f"  Total Changes: {report.total_changes}")
        print(f"  Added Variables: {len(report.added_variables)}")
        print(f"  Removed Variables: {len(report.removed_variables)}")
        print(f"  Modified Variables: {len(report.modified_variables)}")
        return 0

    elif args.command == "profile":
        prof = LimitationsProfiler.default_profile()
        out_file = prof.save_file(Path(args.output_dir) / "limitations_profile.json")
        print(f"Exported Limitations Profile: {out_file}")
        return 0

    elif args.command == "export-ci":
        created = ScenarioCatalog.export_ci_fixtures(
            args.output_dir, file_format=args.format
        )
        print(
            f"Exported {len(created)} CI fixture files to '{args.output_dir}' ({args.format})."
        )
        return 0

    elif args.command == "audit":
        try:
            scenario_slice = ScenarioCompiler.get_scenario(args.scenario)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        tables = {
            "beneficiary": scenario_slice.bene_df,
            "carrier": scenario_slice.carrier_df,
            "outpatient": scenario_slice.outpatient_df,
            "inpatient": scenario_slice.inpatient_df,
            "pde": scenario_slice.pde_df,
            "snf": scenario_slice.snf_df,
            "hha": scenario_slice.hha_df,
            "dme": scenario_slice.dme_df,
            "hospice": scenario_slice.hospice_df,
            "mbsf_cc": scenario_slice.mbsf_cc_df,
            "mbsf_cu": scenario_slice.mbsf_cu_df,
            "mbsf_d": scenario_slice.mbsf_d_df,
            "mbsf_base": scenario_slice.mbsf_base_df,
            "mbsf_oc": scenario_slice.mbsf_oc_df,
            "mbsf_ndi": scenario_slice.mbsf_ndi_df,
            "mbsf_ra": scenario_slice.mbsf_ra_df,
            "mbsf_c": scenario_slice.mbsf_c_df,
            "mbsf_ffs": scenario_slice.mbsf_ffs_df,
            "mbsf_pde_util": scenario_slice.mbsf_pde_util_df,
        }

        engine = AuditEngine(dataset=tables, scenario_name=args.scenario)
        report = engine.run_audit()

        if args.output_dir:
            out_dir = Path(args.output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / "audit_report.json"
            out_file.write_text(report.model_dump_json(indent=2), encoding="utf-8")
            print(f"Audit report saved to: {out_file}")

        print(f"Audit Report for Scenario '{args.scenario}':")
        print(f"  Join Coverage: {report.join_coverage}")
        print(f"  K-Anonymity Metrics: {list(report.k_anonymity.keys())}")
        print(f"  Column Metrics Tables: {list(report.column_metrics.keys())}")
        return 0

    elif args.command == "auto-workflow":
        return run_autonomous_workflow(
            commit_msg=args.commit_msg,
            title=args.title,
            body=args.body,
            dry_run=args.dry_run,
            skip_merge=args.skip_merge,
            json_report_path=args.json_report,
            md_report_path=args.md_report,
            changelog_check=args.changelog_check,
            git_clean_check=args.git_clean_check,
        )

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
