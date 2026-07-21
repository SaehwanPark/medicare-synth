"""Tests for ResDAC Knowledge Base evidence snapshot contracts."""

from pathlib import Path
import pytest
from medicare_synth.evidence import RKBEvidenceSnapshot


@pytest.fixture
def sample_snapshot_path() -> Path:
    return Path("data/rkb_snapshots/rkb-v1.0-20211231.json")


def test_load_rkb_snapshot(sample_snapshot_path: Path) -> None:
    assert sample_snapshot_path.exists(), "RKB snapshot file must exist"
    snapshot = RKBEvidenceSnapshot.from_file(sample_snapshot_path)
    assert snapshot.rkb_version == "1.0.0"
    assert snapshot.schema_year == 2021
    assert "BENE_ID" in snapshot.variables
    assert "CLM_ID" in snapshot.variables


def test_get_variable_contract(sample_snapshot_path: Path) -> None:
    snapshot = RKBEvidenceSnapshot.from_file(sample_snapshot_path)
    var_contract = snapshot.get_variable("CLM_FROM_DT")
    assert var_contract is not None
    assert var_contract.data_type == "date"
    assert var_contract.provenance_status == "preserved"

    missing_var = snapshot.get_variable("NONEXISTENT_VAR")
    assert missing_var is None


def test_constraints_definition(sample_snapshot_path: Path) -> None:
    snapshot = RKBEvidenceSnapshot.from_file(sample_snapshot_path)
    assert len(snapshot.constraints) >= 2
    constraint_ids = [c.constraint_id for c in snapshot.constraints]
    assert "VAL_TEMP_01" in constraint_ids
    assert "VAL_REL_01" in constraint_ids
