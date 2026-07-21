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
  code = main(["validate", "--scenario", "valid_baseline_cohort", "--output-dir", str(out_dir)])
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
    )

