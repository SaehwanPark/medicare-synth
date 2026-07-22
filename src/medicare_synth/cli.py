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
        "--html-report",
        type=str,
        default=None,
        help="Optional path to write an HTML summary execution report",
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
    auto_wf_parser.add_argument(
        "--audit-check",
        action="store_true",
        help="Verify dataset privacy and relational join audit before commit/push",
    )
    auto_wf_parser.add_argument(
        "--validation-check",
        action="store_true",
        help="Verify dataset relational validation integrity before commit/push",
    )
    auto_wf_parser.add_argument(
        "--export-check",
        action="store_true",
        help="Verify scenario release package export before commit/push",
    )
    auto_wf_parser.add_argument(
        "--diff-check",
        action="store_true",
        help="Verify schema diff for evidence snapshot before commit/push",
    )
    auto_wf_parser.add_argument(
        "--profile-check",
        action="store_true",
        help="Verify limitations profile disclosures before commit/push",
    )
    auto_wf_parser.add_argument(
        "--catalog-check",
        action="store_true",
        help="Verify scenario catalog indexing and CI fixture export before commit/push",
    )
    auto_wf_parser.add_argument(
        "--expansion-check",
        action="store_true",
        help="Verify vertical and horizontal dataset expansion logic before commit/push",
    )
    auto_wf_parser.add_argument(
        "--provenance-check",
        action="store_true",
        help="Verify field-level dataset provenance status taxonomy before commit/push",
    )
    auto_wf_parser.add_argument(
        "--benchmark-check",
        action="store_true",
        help="Verify synthetic dataset generation benchmark throughput before commit/push",
    )
    auto_wf_parser.add_argument(
        "--summary-check",
        action="store_true",
        help="Verify aggregated dataset summary matrix before commit/push",
    )
    auto_wf_parser.add_argument(
        "--manifest-check",
        action="store_true",
        help="Verify CMS baseline source manifest entries and relationships before commit/push",
    )
    auto_wf_parser.add_argument(
        "--dag-check",
        action="store_true",
        help="Verify relation-level and column-level DAG topology contracts before commit/push",
    )
    auto_wf_parser.add_argument(
        "--temporal-check",
        action="store_true",
        help="Verify temporal start/end date consistency across claim tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--evidence-check",
        action="store_true",
        help="Verify ResDAC Knowledge Base evidence snapshot contracts before commit/push",
    )
    auto_wf_parser.add_argument(
        "--accounting-check",
        action="store_true",
        help="Verify claim payment accounting non-negativity across claim tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--uniqueness-check",
        action="store_true",
        help="Verify primary key uniqueness across all baseline tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--orphan-check",
        action="store_true",
        help="Verify zero orphan beneficiary keys across all 18 child tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--privacy-check",
        action="store_true",
        help="Verify k-anonymity privacy score evaluation across all 19 synthetic tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--mortality-check",
        action="store_true",
        help="Verify beneficiary mortality temporal consistency across all claim tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--enrollment-check",
        action="store_true",
        help="Verify beneficiary enrollment consistency across MBSF Base enrollment records before commit/push",
    )
    auto_wf_parser.add_argument(
        "--dob-check",
        action="store_true",
        help="Verify beneficiary birth date temporal consistency across all claim tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--provider-check",
        action="store_true",
        help="Verify provider NPI 10-digit numeric format consistency across all claim tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--icd-check",
        action="store_true",
        help="Verify ICD diagnosis code 3-7 alphanumeric format consistency across all claim tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--hcpcs-check",
        action="store_true",
        help="Verify HCPCS procedure code 5-character alphanumeric format consistency across all claim tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--ndc-check",
        action="store_true",
        help="Verify NDC 11-character alphanumeric format consistency for Part D PDE records before commit/push",
    )
    auto_wf_parser.add_argument(
        "--drg-check",
        action="store_true",
        help="Verify DRG 3-character alphanumeric format consistency for inpatient claim records before commit/push",
    )
    auto_wf_parser.add_argument(
        "--taxonomy-check",
        action="store_true",
        help="Verify Healthcare Provider Taxonomy Code 10-character alphanumeric format consistency across claim records before commit/push",
    )
    auto_wf_parser.add_argument(
        "--pos-check",
        action="store_true",
        help="Verify Place of Service (POS) 2-digit numeric format consistency across claim records before commit/push",
    )
    auto_wf_parser.add_argument(
        "--claim-type-check",
        action="store_true",
        help="Verify Claim Type Code 2-digit numeric format consistency across claim records before commit/push",
    )
    auto_wf_parser.add_argument(
        "--disposition-check",
        action="store_true",
        help="Verify Claim Processing Disposition Code 2-digit numeric format consistency across claim records before commit/push",
    )
    auto_wf_parser.add_argument(
        "--rev-center-check",
        action="store_true",
        help="Verify Revenue Center Code 4-digit numeric format consistency across claim records before commit/push",
    )
    auto_wf_parser.add_argument(
        "--demographic-check",
        action="store_true",
        help="Verify beneficiary demographic sex and race code format consistency before commit/push",
    )
    auto_wf_parser.add_argument(
        "--mbsf-check",
        action="store_true",
        help="Verify Master Beneficiary Summary File (MBSF) domain field constraints across all 10 MBSF tables before commit/push",
    )
    auto_wf_parser.add_argument(
        "--inpatient-check",
        action="store_true",
        help="Verify Inpatient claim domain field constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--snf-check",
        action="store_true",
        help="Verify Skilled Nursing Facility (SNF) claim domain field constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--hha-check",
        action="store_true",
        help="Verify Home Health Agency (HHA) claim domain field constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--dme-check",
        action="store_true",
        help="Verify Durable Medical Equipment (DME) claim domain field constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--hospice-check",
        action="store_true",
        help="Verify Hospice claim domain field constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--pde-util-check",
        action="store_true",
        help="Verify Part D PDE Utilization domain field constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--carrier-check",
        action="store_true",
        help="Verify Carrier claim domain field constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--outpatient-check",
        action="store_true",
        help="Verify Outpatient claim domain field constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--zip-check",
        action="store_true",
        help="Verify Zip Code domain format constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--line-item-check",
        action="store_true",
        help="Verify claim line item count/number domain format constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--charge-check",
        action="store_true",
        help="Verify claim charge total and deductible/coinsurance non-negativity constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--age-check",
        action="store_true",
        help="Verify beneficiary age temporal constraints (0 <= age <= 120) before commit/push",
    )
    auto_wf_parser.add_argument(
        "--utilization-check",
        action="store_true",
        help="Verify claim utilization and non-covered day count constraints before commit/push",
    )
    auto_wf_parser.add_argument(
        "--checkout-main",
        action="store_true",
        help="Checkout main branch and pull latest changes after autonomous PR merge",
    )
    auto_wf_parser.add_argument(
        "--all-checks",
        action="store_true",
        help="Enable all available workflow verification checks before commit/push",
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
            html_report_path=args.html_report,
            changelog_check=args.changelog_check,
            git_clean_check=args.git_clean_check,
            audit_check=args.audit_check,
            validation_check=args.validation_check,
            export_check=args.export_check,
            diff_check=args.diff_check,
            profile_check=args.profile_check,
            catalog_check=args.catalog_check,
            expansion_check=args.expansion_check,
            provenance_check=args.provenance_check,
            benchmark_check=args.benchmark_check,
            summary_check=args.summary_check,
            manifest_check=args.manifest_check,
            dag_check=args.dag_check,
            temporal_check=args.temporal_check,
            evidence_check=args.evidence_check,
            accounting_check=args.accounting_check,
            uniqueness_check=args.uniqueness_check,
            orphan_check=args.orphan_check,
            privacy_check=args.privacy_check,
            mortality_check=args.mortality_check,
            enrollment_check=args.enrollment_check,
            dob_check=args.dob_check,
            provider_check=args.provider_check,
            icd_check=args.icd_check,
            hcpcs_check=args.hcpcs_check,
            ndc_check=args.ndc_check,
            drg_check=args.drg_check,
            taxonomy_check=args.taxonomy_check,
            pos_check=args.pos_check,
            claim_type_check=args.claim_type_check,
            disposition_check=args.disposition_check,
            rev_center_check=args.rev_center_check,
            demographic_check=args.demographic_check,
            mbsf_check=args.mbsf_check,
            inpatient_check=args.inpatient_check,
            snf_check=args.snf_check,
            hha_check=args.hha_check,
            dme_check=args.dme_check,
            hospice_check=args.hospice_check,
            pde_util_check=args.pde_util_check,
            carrier_check=args.carrier_check,
            outpatient_check=args.outpatient_check,
            zip_check=args.zip_check,
            line_item_check=args.line_item_check,
            charge_check=args.charge_check,
            age_check=args.age_check,
            utilization_check=args.utilization_check,
            checkout_main=args.checkout_main,
            all_checks=args.all_checks,
        )

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
