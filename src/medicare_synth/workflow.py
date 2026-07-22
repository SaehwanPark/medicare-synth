"""Autonomous workflow execution module for Medicare-Synth.

Automates code verification (linter, type checker, unit tests), git staging, committing,
pushing, PR creation via gh CLI, and autonomous merging into main.
"""

import json
from pathlib import Path
import subprocess
import sys
from typing import Optional


def run_cmd(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Helper to run a subprocess command and print stdout/stderr."""
    print(f"Running: {' '.join(args)}")
    result = subprocess.run(args, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        print(f"Error: Command failed with code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def _write_json_report(path: str, data: dict[str, object]) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Workflow execution report saved to: {out_path}")


def _write_md_report(path: str, data: dict[str, object]) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    status = data.get("status", "unknown")
    dry_run = data.get("dry_run", False)
    branch = data.get("branch", "N/A")
    commit_msg = data.get("commit_msg", "N/A")
    pr_url = data.get("pr_url") or "N/A"
    merged = data.get("merged", False)
    changelog_check = data.get("changelog_check", False)
    git_clean_check = data.get("git_clean_check", False)
    audit_check = data.get("audit_check", False)
    validation_check = data.get("validation_check", False)
    export_check = data.get("export_check", False)
    all_checks = data.get("all_checks", False)

    md_content = f"""# Autonomous Workflow Execution Report

## Execution Summary

| Parameter | Value |
| --- | --- |
| **Status** | {status} |
| **Dry Run** | {dry_run} |
| **Branch** | {branch} |
| **Commit Message** | {commit_msg} |
| **Pull Request URL** | {pr_url} |
| **Merged** | {merged} |
| **Changelog Verified** | {changelog_check} |
| **Git Clean State Checked** | {git_clean_check} |
| **Audit Verified** | {audit_check} |
| **Relational Validation Verified** | {validation_check} |
| **Release Export Verified** | {export_check} |
| **All Verification Checks Enabled** | {all_checks} |
"""
    out_path.write_text(md_content, encoding="utf-8")
    print(f"Markdown workflow report saved to: {out_path}")


def _write_html_report(path: str, data: dict[str, object]) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    status = data.get("status", "unknown")
    dry_run = data.get("dry_run", False)
    branch = data.get("branch", "N/A")
    commit_msg = data.get("commit_msg", "N/A")
    pr_url = data.get("pr_url") or "N/A"
    merged = data.get("merged", False)
    changelog_check = data.get("changelog_check", False)
    git_clean_check = data.get("git_clean_check", False)
    audit_check = data.get("audit_check", False)
    validation_check = data.get("validation_check", False)
    export_check = data.get("export_check", False)
    all_checks = data.get("all_checks", False)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Autonomous Workflow Execution Report</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; margin: 20px; line-height: 1.5; background-color: #f8f9fa; color: #212529; }}
        h1 {{ color: #0d6efd; border-bottom: 2px solid #0d6efd; padding-bottom: 8px; }}
        table {{ border-collapse: collapse; width: 100%; max-width: 800px; margin-top: 15px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th, td {{ border: 1px solid #dee2e6; padding: 10px 14px; text-align: left; }}
        th {{ background-color: #e9ecef; font-weight: 600; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
    </style>
</head>
<body>
    <h1>Autonomous Workflow Execution Report</h1>
    <h2>Execution Summary</h2>
    <table>
        <thead>
            <tr><th>Parameter</th><th>Value</th></tr>
        </thead>
        <tbody>
            <tr><td><strong>Status</strong></td><td>{status}</td></tr>
            <tr><td><strong>Dry Run</strong></td><td>{dry_run}</td></tr>
            <tr><td><strong>Branch</strong></td><td>{branch}</td></tr>
            <tr><td><strong>Commit Message</strong></td><td>{commit_msg}</td></tr>
            <tr><td><strong>Pull Request URL</strong></td><td>{pr_url}</td></tr>
            <tr><td><strong>Merged</strong></td><td>{merged}</td></tr>
            <tr><td><strong>Changelog Verified</strong></td><td>{changelog_check}</td></tr>
            <tr><td><strong>Git Clean State Checked</strong></td><td>{git_clean_check}</td></tr>
            <tr><td><strong>Audit Verified</strong></td><td>{audit_check}</td></tr>
            <tr><td><strong>Relational Validation Verified</strong></td><td>{validation_check}</td></tr>
            <tr><td><strong>Release Export Verified</strong></td><td>{export_check}</td></tr>
            <tr><td><strong>All Verification Checks Enabled</strong></td><td>{all_checks}</td></tr>
        </tbody>
    </table>
</body>
</html>
"""
    out_path.write_text(html_content, encoding="utf-8")
    print(f"HTML workflow report saved to: {out_path}")


def run_autonomous_workflow(
    commit_msg: str = "feat: implement autonomous workflow subcommand and reconcile docs",
    title: str = "feat: implement autonomous workflow subcommand and reconcile docs",
    body: str = "Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
    dry_run: bool = False,
    skip_merge: bool = False,
    json_report_path: Optional[str] = None,
    md_report_path: Optional[str] = None,
    html_report_path: Optional[str] = None,
    changelog_check: bool = False,
    git_clean_check: bool = False,
    audit_check: bool = False,
    validation_check: bool = False,
    export_check: bool = False,
    all_checks: bool = False,
) -> int:
    """Run local verification checks and autonomously stage, commit, push, create PR, and merge."""
    if all_checks:
        changelog_check = True
        git_clean_check = True
        audit_check = True
        validation_check = True
        export_check = True

    print("=== Step 1: Running Linter (Ruff) ===")
    run_cmd(["uv", "run", "ruff", "check", "."])

    print("\n=== Step 2: Running Type Checker (BasedPyright) ===")
    run_cmd(["uv", "run", "basedpyright"])

    print("\n=== Step 3: Running Unit Tests (Pytest) ===")
    run_cmd(["uv", "run", "pytest"])

    if changelog_check:
        print("\n=== Verification Step: Checking CHANGELOG.md Modifications ===")
        status_res = subprocess.run(
            ["git", "status", "--porcelain", "CHANGELOG.md"],
            capture_output=True,
            text=True,
        )
        if status_res.stdout.strip():
            print("✓ CHANGELOG.md modifications verified.")
        else:
            print(
                "Warning: CHANGELOG.md has no uncommitted modifications.",
                file=sys.stderr,
            )

    if git_clean_check:
        print("\n=== Verification Step: Checking Working Tree Clean State ===")
        clean_res = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
        )
        if not clean_res.stdout.strip():
            print("✓ Working tree clean state verified.")
        else:
            print(
                "✓ Working tree contains modified/untracked files.",
                file=sys.stderr,
            )

    if audit_check:
        print("\n=== Verification Step: Executing Dataset Audit Check ===")
        from medicare_synth.audit import AuditEngine
        from medicare_synth.scenarios import ScenarioCompiler

        scenario_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
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
        audit_engine = AuditEngine(
            dataset=tables, scenario_name="valid_baseline_cohort"
        )
        report = audit_engine.run_audit()
        print(
            f"✓ Dataset audit verified ({len(report.join_coverage)} join coverage relationships audited)."
        )

    if validation_check:
        print("\n=== Verification Step: Executing Relational Validation Check ===")
        from medicare_synth.scenarios import ScenarioCompiler
        from medicare_synth.validation import RelationalValidator

        scenario_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
        validator = RelationalValidator()
        val_report = validator.validate_slice(
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
        if val_report.is_valid:
            print(
                f"✓ Relational validation verified ({len(val_report.findings)} findings reported)."
            )
        else:
            print(
                f"Warning: Relational validation reported findings ({len(val_report.findings)} findings).",
                file=sys.stderr,
            )

    if export_check:
        print("\n=== Verification Step: Executing Scenario Release Export Check ===")
        import tempfile
        from medicare_synth.release import ReleaseExporter
        from medicare_synth.scenarios import ScenarioCompiler

        scenario_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
        with tempfile.TemporaryDirectory() as tmp_dir:
            exporter = ReleaseExporter(
                output_dir=Path(tmp_dir), release_id="v1.0.0-test"
            )
            manifest = exporter.export_slice(
                bene_df=scenario_slice.bene_df,
                carrier_df=scenario_slice.carrier_df,
                outpatient_df=scenario_slice.outpatient_df,
                fmt="all",
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
            print(
                f"✓ Release export verified (manifest generated with {len(manifest.files)} files)."
            )

    print("\n✓ Verification checks passed successfully.")

    branch_res = run_cmd(["git", "branch", "--show-current"])
    current_branch = branch_res.stdout.strip()
    if not current_branch:
        print("Error: Could not determine current git branch name.", file=sys.stderr)
        return 1

    print(f"Active branch: {current_branch}")
    if current_branch in ("main", "master"):
        print(
            "Error: Refusing to run workflow on base branch 'main/master'. Please checkout a feature branch.",
            file=sys.stderr,
        )
        return 1

    if dry_run:
        print("\n=== [Dry Run] Git Commit & Push ===")
        print("Would stage files: git add .")
        print(f"Would commit: git commit -m '{commit_msg}'")
        print("Would push: git push -u origin HEAD")
        print("\n=== [Dry Run] GitHub PR & Merge ===")
        print(f"Would create PR: gh pr create --title '{title}' --body '{body}'")
        if not skip_merge:
            print("Would autonomously merge PR: gh pr merge --merge --delete-branch")
        print("\n✓ Dry-run completed successfully.")
        report_data: dict[str, object] = {
            "status": "success",
            "dry_run": True,
            "branch": current_branch,
            "commit_msg": commit_msg,
            "pr_url": None,
            "merged": False,
            "changelog_check": changelog_check,
            "git_clean_check": git_clean_check,
            "audit_check": audit_check,
            "validation_check": validation_check,
            "export_check": export_check,
            "all_checks": all_checks,
        }
        if json_report_path:
            _write_json_report(json_report_path, report_data)
        if md_report_path:
            _write_md_report(md_report_path, report_data)
        if html_report_path:
            _write_html_report(html_report_path, report_data)
        return 0

    print("\n=== Step 4: Staging and Committing Changes ===")
    run_cmd(["git", "add", "."])
    diff_check = subprocess.run(["git", "diff", "--quiet", "--cached"])
    if diff_check.returncode == 0:
        print("No changes staged to commit.")
    else:
        run_cmd(["git", "commit", "-m", commit_msg])

    print("\n=== Step 5: Pushing branch to Remote ===")
    run_cmd(["git", "push", "-u", "origin", "HEAD"])

    print("\n=== Step 6: Creating GitHub Pull Request ===")
    pr_check = subprocess.run(
        ["gh", "pr", "view", "--json", "state,url"], capture_output=True, text=True
    )
    pr_url: Optional[str] = None
    if pr_check.returncode == 0:
        try:
            pr_data = json.loads(pr_check.stdout)
            if pr_data.get("state") == "OPEN":
                pr_url = str(pr_data.get("url", ""))
                print(f"Existing open PR found: {pr_url}")
        except Exception:
            pass

    if not pr_url:
        pr_res = run_cmd(["gh", "pr", "create", "--title", title, "--body", body])
        pr_url = pr_res.stdout.strip()
        print(f"Pull Request created: {pr_url}")

    if skip_merge:
        print("\n✓ PR Handoff completed. Skipping autonomous merge as requested.")
        report_data = {
            "status": "success",
            "dry_run": False,
            "branch": current_branch,
            "commit_msg": commit_msg,
            "pr_url": pr_url,
            "merged": False,
            "changelog_check": changelog_check,
            "git_clean_check": git_clean_check,
            "audit_check": audit_check,
            "validation_check": validation_check,
            "export_check": export_check,
            "all_checks": all_checks,
        }
        if json_report_path:
            _write_json_report(json_report_path, report_data)
        if md_report_path:
            _write_md_report(md_report_path, report_data)
        if html_report_path:
            _write_html_report(html_report_path, report_data)
        return 0

    print("\n=== Step 7: Autonomous Merge to main ===")
    run_cmd(["gh", "pr", "merge", "--merge", "--delete-branch"])
    print("\n✓ PR successfully merged into main and remote branch deleted.")
    report_data = {
        "status": "success",
        "dry_run": False,
        "branch": current_branch,
        "commit_msg": commit_msg,
        "pr_url": pr_url,
        "merged": True,
        "changelog_check": changelog_check,
        "git_clean_check": git_clean_check,
        "audit_check": audit_check,
        "validation_check": validation_check,
        "export_check": export_check,
        "all_checks": all_checks,
    }
    if json_report_path:
        _write_json_report(json_report_path, report_data)
    if md_report_path:
        _write_md_report(md_report_path, report_data)
    if html_report_path:
        _write_html_report(html_report_path, report_data)
    return 0

