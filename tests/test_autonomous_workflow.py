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
    assert data["benchmark_check"] is True
    assert data["summary_check"] is True
    assert data["uniqueness_check"] is True
    assert data["orphan_check"] is True
    assert data["privacy_check"] is True
    assert data["mortality_check"] is True


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


@patch("subprocess.run")
def test_run_autonomous_workflow_benchmark_check(mock_run, tmp_path):
    """Test that benchmark_check option executes synthetic benchmark step and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_bm.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        benchmark_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["benchmark_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_summary_check(mock_run, tmp_path):
    """Test that summary_check option executes dataset summary matrix step and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_sm.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        summary_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["summary_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_manifest_check(mock_run, tmp_path):
    """Test that manifest_check option executes CMS baseline manifest audit step and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_manifest.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        manifest_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["manifest_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_dag_check(mock_run, tmp_path):
    """Test that dag_check option executes DAG topology contract check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_dag.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        dag_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["dag_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_temporal_check(mock_run, tmp_path):
    """Test that temporal_check option executes temporal consistency check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_temporal.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        temporal_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["temporal_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_evidence_check(mock_run, tmp_path):
    """Test that evidence_check option executes RKB evidence snapshot check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_evidence.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        evidence_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["evidence_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_accounting_check(mock_run, tmp_path):
    """Test that accounting_check option executes claim accounting verification check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_accounting.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        accounting_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["accounting_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_uniqueness_check(mock_run, tmp_path):
    """Test that uniqueness_check option executes primary key uniqueness check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_uniqueness.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        uniqueness_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["uniqueness_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_orphan_check(mock_run, tmp_path):
    """Test that orphan_check option executes orphan claim verification check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_orphan.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        orphan_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["orphan_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_privacy_check(mock_run, tmp_path):
    """Test that privacy_check option executes k-anonymity privacy check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_privacy.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        privacy_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["privacy_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_mortality_check(mock_run, tmp_path):
    """Test that mortality_check option executes mortality temporal check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_mortality.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        mortality_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["mortality_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_enrollment_check(mock_run, tmp_path):
    """Test that enrollment_check option executes enrollment consistency check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_enrollment.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        enrollment_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["enrollment_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_dob_check(mock_run, tmp_path):
    """Test that dob_check option executes beneficiary birth date temporal check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_dob.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        dob_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["dob_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_provider_check(mock_run, tmp_path):
    """Test that provider_check option executes provider NPI format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_provider.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        provider_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["provider_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_icd_check(mock_run, tmp_path):
    """Test that icd_check option executes ICD diagnosis code format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_icd.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        icd_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["icd_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_hcpcs_check(mock_run, tmp_path):
    """Test that hcpcs_check option executes HCPCS procedure code format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_hcpcs.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        hcpcs_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["hcpcs_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_ndc_check(mock_run, tmp_path):
    """Test that ndc_check option executes NDC code format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_ndc.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        ndc_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["ndc_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_drg_check(mock_run, tmp_path):
    """Test that drg_check option executes DRG code format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_drg.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        drg_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["drg_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_taxonomy_check(mock_run, tmp_path):
    """Test that taxonomy_check option executes Healthcare Provider Taxonomy Code format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_taxonomy.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        taxonomy_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["taxonomy_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_pos_check(mock_run, tmp_path):
    """Test that pos_check option executes Place of Service (POS) code format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_pos.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        pos_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["pos_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_claim_type_check(mock_run, tmp_path):
    """Test that claim_type_check option executes Claim Type Code format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_claim_type.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        claim_type_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["claim_type_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_rev_center_check(mock_run, tmp_path):
    """Test that rev_center_check option executes Revenue Center Code format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_rev.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        rev_center_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["rev_center_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_demographic_check(mock_run, tmp_path):
    """Test that demographic_check option executes Demographic Code format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_demog.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        demographic_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["demographic_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_mbsf_check(mock_run, tmp_path):
    """Test that mbsf_check option executes MBSF field constraint check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_mbsf.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        mbsf_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["mbsf_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_inpatient_check(mock_run, tmp_path):
    """Test that inpatient_check option executes Inpatient field constraint check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_inpatient.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        inpatient_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["inpatient_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_snf_check(mock_run, tmp_path):
    """Test that snf_check option executes SNF field constraint check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_snf.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        snf_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["snf_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_hha_check(mock_run, tmp_path):
    """Test that hha_check option executes HHA field constraint check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_hha.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        hha_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["hha_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_dme_check(mock_run, tmp_path):
    """Test that dme_check option executes DME field constraint check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_dme.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        dme_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["dme_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_hospice_check(mock_run, tmp_path):
    """Test that hospice_check option executes Hospice field constraint check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_hospice.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        hospice_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["hospice_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_pde_util_check(mock_run, tmp_path):
    """Test that pde_util_check option executes Part D PDE Utilization field constraint check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_pde_util.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        pde_util_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["pde_util_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_carrier_check(mock_run, tmp_path):
    """Test that carrier_check option executes Carrier field constraint check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_carrier.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        carrier_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["carrier_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_outpatient_check(mock_run, tmp_path):
    """Test that outpatient_check option executes Outpatient field constraint check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_outpatient.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        outpatient_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["outpatient_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_zip_check(mock_run, tmp_path):
    """Test that zip_check option executes Zip Code domain format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_zip.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        zip_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["zip_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_line_item_check(mock_run, tmp_path):
    """Test that line_item_check option executes Claim Line Item format check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_line_item.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        line_item_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["line_item_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_charge_check(mock_run, tmp_path):
    """Test that charge_check option executes Claim Charge accounting check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_charge.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        charge_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["charge_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_age_check(mock_run, tmp_path):
    """Test that age_check option executes Beneficiary Age temporal check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_age.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        age_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["age_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_utilization_check(mock_run, tmp_path):
    """Test that utilization_check option executes Claim Utilization day check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_utilization.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        utilization_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["utilization_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_disposition_check(mock_run, tmp_path):
    """Test that disposition_check option executes Claim Disposition Code check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_disp.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        disposition_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["disposition_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_state_check(mock_run, tmp_path):
    """Test that state_check option executes Beneficiary State Code check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_state.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        state_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["state_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_pde_check(mock_run, tmp_path):
    """Test that pde_check option executes Part D PDE field constraint check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_pde.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        pde_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["pde_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_county_check(mock_run, tmp_path):
    """Test that county_check option executes Beneficiary County Code check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_county.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        county_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["county_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_discharge_status_check(mock_run, tmp_path):
    """Test that discharge_status_check option executes Patient Discharge Status Code check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_discharge.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        discharge_status_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["discharge_status_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_admission_source_check(mock_run, tmp_path):
    """Test that admission_source_check option executes Claim Admission Source Code check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_admsn_src.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        admission_source_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["admission_source_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_primary_payer_check(mock_run, tmp_path):
    """Test that primary_payer_check option executes Claim Primary Payer Code check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_prmry_pyr.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        primary_payer_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["primary_payer_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_admission_type_check(mock_run, tmp_path):
    """Test that admission_type_check option executes Claim Admission Type Code check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_admsn_type.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        admission_type_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["admission_type_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_frequency_check(mock_run, tmp_path):
    """Test that frequency_check option executes Claim Frequency Code check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_freq.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        frequency_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["frequency_check"] is True


@patch("subprocess.run")
def test_run_autonomous_workflow_query_check(mock_run, tmp_path):
    """Test that query_check option executes Claim Query Code check and records status."""
    import json
    from medicare_synth.workflow import run_autonomous_workflow

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "feat/test-branch"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    report_file = tmp_path / "wf_report_query.json"
    res_code = run_autonomous_workflow(
        dry_run=True,
        json_report_path=str(report_file),
        query_check=True,
    )
    assert res_code == 0
    assert report_file.exists()

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["query_check"] is True

