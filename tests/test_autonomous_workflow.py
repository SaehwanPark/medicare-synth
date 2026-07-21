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

    # Should run successfully and not raise SystemExit
    main()

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
    mock_run.assert_called_once_with(["uv", "run", "ruff", "check", "."], capture_output=True, text=True)
