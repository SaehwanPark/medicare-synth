"""Tests for the autonomous workflow runner script."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from scripts.autonomous_workflow import main


@patch("subprocess.run")
@patch("sys.argv", ["scripts/autonomous_workflow.py", "--dry-run"])
def test_autonomous_workflow_dry_run(mock_run):
    """Test that dry-run mode completes successfully with mock subprocess calls."""
    # Mocking successful command execution for check steps
    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/autonomous-workflow-integration"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    # Should exit with code 0
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0

    # Verify that it ran the validation commands first
    assert mock_run.call_count >= 4
    called_cmds = [call_args[0][0] for call_args in mock_run.call_args_list]

    # Assert check commands are in the call list
    assert ["uv", "run", "ruff", "check", "."] in called_cmds
    assert ["uv", "run", "basedpyright"] in called_cmds
    assert ["uv", "run", "pytest"] in called_cmds
    assert ["git", "branch", "--show-current"] in called_cmds


@patch("subprocess.run")
@patch("sys.argv", ["scripts/autonomous_workflow.py"])
def test_autonomous_workflow_checks_failed(mock_run):
    """Test that if a verification check fails, the workflow exits early with non-zero."""
    # Mock a failing command (e.g., ruff check fails)
    mock_res = MagicMock()
    mock_res.returncode = 1
    mock_res.stdout = ""
    mock_res.stderr = "Linter failed"
    mock_run.return_value = mock_res

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code != 0
    # verify that execution stopped at the first step
    mock_run.assert_called_once_with(
        ["uv", "run", "ruff", "check", "."], capture_output=True, text=True
    )


@patch("subprocess.run")
def test_run_autonomous_workflow_json_report(mock_run, tmp_path):
    """Test that run_autonomous_workflow produces a valid JSON report file."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report.json"
    res_code = run_autonomous_workflow(dry_run=True, json_report_path=str(report_file))
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["status"] == "success"
    assert data["dry_run"] is True
    assert data["branch"] == "feat/test-branch"


@patch("subprocess.run")
def test_run_autonomous_workflow_changelog_check(mock_run, tmp_path):
    """Test that changelog_check option runs git status check on CHANGELOG.md and logs status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = " M CHANGELOG.md\n"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_cl.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        changelog_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["changelog_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_md_report(mock_run, tmp_path):
    """Test that run_autonomous_workflow produces a valid Markdown report file."""
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report.md"
    res_code = run_autonomous_workflow(dry_run=True, md_report_path=str(report_file))
    assert res_code == 0
    assert report_file.exists()

    content = report_file.read_text(encoding="utf-8")
    assert "# Autonomous Workflow Execution Report" in content
    assert "| **Status** | success |" in content
    assert "| **Branch** | feat/test-branch |" in content


@patch("subprocess.run")
def test_run_autonomous_workflow_git_clean_check(mock_run, tmp_path):
    """Test that git_clean_check option runs git status check step and records status in report."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_gcc.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        git_clean_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["git_clean_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_html_report(mock_run, tmp_path):
    """Test that run_autonomous_workflow produces a valid HTML report file."""
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report.html"
    res_code = run_autonomous_workflow(dry_run=True, html_report_path=str(report_file))
    assert res_code == 0
    assert report_file.exists()

    content = report_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "<title>Autonomous Workflow Execution Report</title>" in content
    assert "<td>feat/test-branch</td>" in content


@patch("subprocess.run")
def test_run_autonomous_workflow_audit_check(mock_run, tmp_path):
    """Test that audit_check option executes dataset audit step and records status in report."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_audit.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        audit_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["audit_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_validation_check(mock_run, tmp_path):
    """Test that validation_check option executes relational validation step and records status in report."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_val.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        validation_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["validation_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_export_check(mock_run, tmp_path):
    """Test that export_check option executes release export step and records status in report."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_export.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        export_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["export_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_catalog_check(mock_run, tmp_path):
    """Test that catalog_check option executes scenario catalog step and records status in report."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_cat.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        catalog_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["catalog_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_all_checks(mock_run, tmp_path):
    """Test that all_checks option enables all verification steps and records status in report."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_all.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        all_checks=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["all_checks"] is True
    assert data["changelog_check"] is True
    assert data["git_clean_check"] is True
    assert data["audit_check"] is True
    assert data["validation_check"] is True
    assert data["export_check"] is True
    assert data["diff_check"] is True
    assert data["profile_check"] is True
    assert data["catalog_check"] is True
    assert data["expansion_check"] is True
    assert data["provenance_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_expansion_check(mock_run, tmp_path):
    """Test that expansion_check option executes vertical & horizontal expansion step and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_exp.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        expansion_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["expansion_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_provenance_check(mock_run, tmp_path):
    """Test that provenance_check option executes dataset provenance step and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_prov.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        provenance_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["provenance_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_checkout_main(mock_run, tmp_path):
    """Test that checkout_main option records status and executes git checkout main."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_co.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        checkout_main=True,
    )
    assert res_code == 0
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["checkout_main"] is True
