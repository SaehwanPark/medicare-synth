"""Behavioral tests for Medicare-Synth CLI."""

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
