"""Unit tests for SchemaDiffer and RKBEvidenceSnapshot comparison."""

from medicare_synth.diff import DiffSeverity, SchemaDiffer
from medicare_synth.evidence import RKBEvidenceSnapshot, VariableContract


def test_schema_differ_identical_snapshots():
  snap = RKBEvidenceSnapshot.load_default_snapshot()
  report = SchemaDiffer.compare_snapshots(snap, snap)
  assert report.has_breaking_changes is False
  assert report.total_changes == 0
  assert len(report.added_variables) == 0
  assert len(report.removed_variables) == 0


def test_schema_differ_modified_snapshot():
  snap1 = RKBEvidenceSnapshot.load_default_snapshot()

  # Create modified snapshot with data type change
  modified_vars = dict(snap1.variables)
  orig_bene = modified_vars["BENE_ID"]
  modified_vars["BENE_ID"] = VariableContract(
    name=orig_bene.name,
    label=orig_bene.label,
    data_type="INTEGER",  # Changed from VARCHAR
    format=orig_bene.format,
    max_length=orig_bene.max_length,
    nullable=orig_bene.nullable,
    provenance_status=orig_bene.provenance_status,
    description=orig_bene.description,
    valid_values=orig_bene.valid_values,
  )

  snap2 = RKBEvidenceSnapshot(
    rkb_version="v1.1-test",
    snapshot_date="2022-01-01",
    schema_year=2022,
    description="Test snapshot",
    source_repository="ResDAC",
    variables=modified_vars,
    constraints=snap1.constraints,
  )

  report = SchemaDiffer.compare_snapshots(snap1, snap2)
  assert report.has_breaking_changes is True
  assert report.total_changes == 1
  assert report.modified_variables[0].variable_name == "BENE_ID"
  assert report.modified_variables[0].severity == DiffSeverity.BREAKING
