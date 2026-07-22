from unittest.mock import patch

from medicare_synth.cli import main


def test_cli_scenario_subcommand():
    code = main(["scenario", "--name", "valid_baseline_cohort"])
    assert code == 0


def test_cli_validate_subcommand_success():
    code = main(["validate", "--scenario", "valid_baseline_cohort"])
    assert code == 0


def test_cli_validate_subcommand_failure():
    code = main(["validate", "--scenario", "invalid_orphaned_claim"])
    assert code == 1


def test_cli_manifest_subcommand_baseline():
    code = main(["manifest", "--type", "baseline"])
    assert code == 0


def test_cli_manifest_subcommand_evidence():
    code = main(["manifest", "--type", "evidence"])
    assert code == 0


def test_cli_validate_subcommand_output_dir(tmp_path):
    import json

    out_dir = tmp_path / "val_out"
    code = main(
        [
            "validate",
            "--scenario",
            "valid_baseline_cohort",
            "--output-dir",
            str(out_dir),
        ]
    )
    assert code == 0
    report_file = out_dir / "validation_report.json"
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "findings" in data
    assert isinstance(data["findings"], list)


def test_cli_auto_workflow_dry_run():
    with patch("medicare_synth.cli.run_autonomous_workflow", return_value=0) as mock_wf:
        code = main(["auto-workflow", "--dry-run"])
        assert code == 0
        mock_wf.assert_called_once_with(
            commit_msg="feat: implement autonomous workflow subcommand and reconcile docs",
            title="feat: implement autonomous workflow subcommand and reconcile docs",
            body="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
            dry_run=True,
            skip_merge=False,
            json_report_path=None,
            md_report_path=None,
            html_report_path=None,
            changelog_check=False,
            git_clean_check=False,
            audit_check=False,
            validation_check=False,
            export_check=False,
            all_checks=False,
        )


def test_cli_auto_workflow_json_report(tmp_path):
    report_path = str(tmp_path / "report.json")
    with patch("medicare_synth.cli.run_autonomous_workflow", return_value=0) as mock_wf:
        code = main(["auto-workflow", "--dry-run", "--json-report", report_path])
        assert code == 0
        mock_wf.assert_called_once_with(
            commit_msg="feat: implement autonomous workflow subcommand and reconcile docs",
            title="feat: implement autonomous workflow subcommand and reconcile docs",
            body="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
            dry_run=True,
            skip_merge=False,
            json_report_path=report_path,
            md_report_path=None,
            html_report_path=None,
            changelog_check=False,
            git_clean_check=False,
            audit_check=False,
            validation_check=False,
            export_check=False,
            all_checks=False,
        )


def test_cli_auto_workflow_md_report(tmp_path):
    report_path = str(tmp_path / "report.md")
    with patch("medicare_synth.cli.run_autonomous_workflow", return_value=0) as mock_wf:
        code = main(["auto-workflow", "--dry-run", "--md-report", report_path])
        assert code == 0
        mock_wf.assert_called_once_with(
            commit_msg="feat: implement autonomous workflow subcommand and reconcile docs",
            title="feat: implement autonomous workflow subcommand and reconcile docs",
            body="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
            dry_run=True,
            skip_merge=False,
            json_report_path=None,
            md_report_path=report_path,
            html_report_path=None,
            changelog_check=False,
            git_clean_check=False,
            audit_check=False,
            validation_check=False,
            export_check=False,
            all_checks=False,
        )


def test_cli_auto_workflow_changelog_check():
    with patch("medicare_synth.cli.run_autonomous_workflow", return_value=0) as mock_wf:
        code = main(["auto-workflow", "--dry-run", "--changelog-check"])
        assert code == 0
        mock_wf.assert_called_once_with(
            commit_msg="feat: implement autonomous workflow subcommand and reconcile docs",
            title="feat: implement autonomous workflow subcommand and reconcile docs",
            body="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
            dry_run=True,
            skip_merge=False,
            json_report_path=None,
            md_report_path=None,
            html_report_path=None,
            changelog_check=True,
            git_clean_check=False,
            audit_check=False,
            validation_check=False,
            export_check=False,
            all_checks=False,
        )


def test_cli_auto_workflow_git_clean_check():
    with patch("medicare_synth.cli.run_autonomous_workflow", return_value=0) as mock_wf:
        code = main(["auto-workflow", "--dry-run", "--git-clean-check"])
        assert code == 0
        mock_wf.assert_called_once_with(
            commit_msg="feat: implement autonomous workflow subcommand and reconcile docs",
            title="feat: implement autonomous workflow subcommand and reconcile docs",
            body="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
            dry_run=True,
            skip_merge=False,
            json_report_path=None,
            md_report_path=None,
            html_report_path=None,
            changelog_check=False,
            git_clean_check=True,
            audit_check=False,
            validation_check=False,
            export_check=False,
            all_checks=False,
        )


def test_cli_auto_workflow_html_report(tmp_path):
    report_path = str(tmp_path / "report.html")
    with patch("medicare_synth.cli.run_autonomous_workflow", return_value=0) as mock_wf:
        code = main(["auto-workflow", "--dry-run", "--html-report", report_path])
        assert code == 0
        mock_wf.assert_called_once_with(
            commit_msg="feat: implement autonomous workflow subcommand and reconcile docs",
            title="feat: implement autonomous workflow subcommand and reconcile docs",
            body="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
            dry_run=True,
            skip_merge=False,
            json_report_path=None,
            md_report_path=None,
            html_report_path=report_path,
            changelog_check=False,
            git_clean_check=False,
            audit_check=False,
            validation_check=False,
            export_check=False,
            all_checks=False,
        )


def test_cli_auto_workflow_audit_check():
    with patch("medicare_synth.cli.run_autonomous_workflow", return_value=0) as mock_wf:
        code = main(["auto-workflow", "--dry-run", "--audit-check"])
        assert code == 0
        mock_wf.assert_called_once_with(
            commit_msg="feat: implement autonomous workflow subcommand and reconcile docs",
            title="feat: implement autonomous workflow subcommand and reconcile docs",
            body="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
            dry_run=True,
            skip_merge=False,
            json_report_path=None,
            md_report_path=None,
            html_report_path=None,
            changelog_check=False,
            git_clean_check=False,
            audit_check=True,
            validation_check=False,
            export_check=False,
            all_checks=False,
        )


def test_cli_auto_workflow_validation_check():
    with patch("medicare_synth.cli.run_autonomous_workflow", return_value=0) as mock_wf:
        code = main(["auto-workflow", "--dry-run", "--validation-check"])
        assert code == 0
        mock_wf.assert_called_once_with(
            commit_msg="feat: implement autonomous workflow subcommand and reconcile docs",
            title="feat: implement autonomous workflow subcommand and reconcile docs",
            body="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
            dry_run=True,
            skip_merge=False,
            json_report_path=None,
            md_report_path=None,
            html_report_path=None,
            changelog_check=False,
            git_clean_check=False,
            audit_check=False,
            validation_check=True,
            export_check=False,
            all_checks=False,
        )


def test_cli_auto_workflow_export_check():
    with patch("medicare_synth.cli.run_autonomous_workflow", return_value=0) as mock_wf:
        code = main(["auto-workflow", "--dry-run", "--export-check"])
        assert code == 0
        mock_wf.assert_called_once_with(
            commit_msg="feat: implement autonomous workflow subcommand and reconcile docs",
            title="feat: implement autonomous workflow subcommand and reconcile docs",
            body="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
            dry_run=True,
            skip_merge=False,
            json_report_path=None,
            md_report_path=None,
            html_report_path=None,
            changelog_check=False,
            git_clean_check=False,
            audit_check=False,
            validation_check=False,
            export_check=True,
            all_checks=False,
        )


def test_cli_auto_workflow_all_checks():
    with patch("medicare_synth.cli.run_autonomous_workflow", return_value=0) as mock_wf:
        code = main(["auto-workflow", "--dry-run", "--all-checks"])
        assert code == 0
        mock_wf.assert_called_once_with(
            commit_msg="feat: implement autonomous workflow subcommand and reconcile docs",
            title="feat: implement autonomous workflow subcommand and reconcile docs",
            body="Automated PR created by the autonomous workflow engine. Reconciles docs and adds CLI auto-workflow subcommand.",
            dry_run=True,
            skip_merge=False,
            json_report_path=None,
            md_report_path=None,
            html_report_path=None,
            changelog_check=False,
            git_clean_check=False,
            audit_check=False,
            validation_check=False,
            export_check=False,
            all_checks=True,
        )
