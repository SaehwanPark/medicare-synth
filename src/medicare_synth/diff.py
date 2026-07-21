"""Schema and evidence snapshot diffing module.

Compares RKB evidence snapshots or schema contracts across annual updates to prevent
silent baseline corruption and breaking structural changes.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from medicare_synth.evidence import RKBEvidenceSnapshot, VariableContract


class DiffChangeType(str, Enum):
    """Type of structural change in schema diffing."""

    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"


class DiffSeverity(str, Enum):
    """Severity of schema modification impact."""

    INFO = "INFO"
    WARNING = "WARNING"
    BREAKING = "BREAKING"


class VariableChange(BaseModel):
    """Detail of a single variable change between two evidence snapshots."""

    variable_name: str
    change_type: DiffChangeType
    severity: DiffSeverity
    attribute_name: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    description: str


class DiffReport(BaseModel):
    """Report summarizing differences between two evidence snapshots."""

    snapshot_a_version: str
    snapshot_b_version: str
    has_breaking_changes: bool
    total_changes: int
    added_variables: List[str]
    removed_variables: List[str]
    modified_variables: List[VariableChange]


class SchemaDiffer:
    """Diffing engine for comparing RKB evidence snapshots and detecting structural drifts."""

    @staticmethod
    def compare_snapshots(
        snap_a: RKBEvidenceSnapshot, snap_b: RKBEvidenceSnapshot
    ) -> DiffReport:
        """Compares two RKBEvidenceSnapshot instances and returns a structured DiffReport."""
        vars_a: Dict[str, VariableContract] = snap_a.variables
        vars_b: Dict[str, VariableContract] = snap_b.variables

        keys_a = set(vars_a.keys())
        keys_b = set(vars_b.keys())

        added_keys = sorted(list(keys_b - keys_a))
        removed_keys = sorted(list(keys_a - keys_b))
        common_keys = sorted(list(keys_a & keys_b))

        modified_changes: List[VariableChange] = []
        has_breaking = False

        # Removed variables are breaking if deleted
        if removed_keys:
            has_breaking = True

        for var_name in common_keys:
            v_a = vars_a[var_name]
            v_b = vars_b[var_name]

            # Check data_type change
            if v_a.data_type != v_b.data_type:
                has_breaking = True
                modified_changes.append(
                    VariableChange(
                        variable_name=var_name,
                        change_type=DiffChangeType.MODIFIED,
                        severity=DiffSeverity.BREAKING,
                        attribute_name="data_type",
                        old_value=v_a.data_type,
                        new_value=v_b.data_type,
                        description=f"Variable '{var_name}' data type changed from '{v_a.data_type}' to '{v_b.data_type}'.",
                    )
                )

            # Check nullability change
            if v_a.nullable != v_b.nullable:
                sev = (
                    DiffSeverity.BREAKING
                    if (not v_b.nullable and v_a.nullable)
                    else DiffSeverity.WARNING
                )
                if sev == DiffSeverity.BREAKING:
                    has_breaking = True
                modified_changes.append(
                    VariableChange(
                        variable_name=var_name,
                        change_type=DiffChangeType.MODIFIED,
                        severity=sev,
                        attribute_name="nullable",
                        old_value=v_a.nullable,
                        new_value=v_b.nullable,
                        description=f"Variable '{var_name}' nullability changed from {v_a.nullable} to {v_b.nullable}.",
                    )
                )

            # Check valid_values change
            if v_a.valid_values != v_b.valid_values:
                modified_changes.append(
                    VariableChange(
                        variable_name=var_name,
                        change_type=DiffChangeType.MODIFIED,
                        severity=DiffSeverity.WARNING,
                        attribute_name="valid_values",
                        old_value=v_a.valid_values,
                        new_value=v_b.valid_values,
                        description=f"Variable '{var_name}' valid values updated.",
                    )
                )

        total_count = len(added_keys) + len(removed_keys) + len(modified_changes)

        return DiffReport(
            snapshot_a_version=snap_a.rkb_version,
            snapshot_b_version=snap_b.rkb_version,
            has_breaking_changes=has_breaking,
            total_changes=total_count,
            added_variables=added_keys,
            removed_variables=removed_keys,
            modified_variables=modified_changes,
        )

    @classmethod
    def compare_files(cls, path_a: Path, path_b: Path) -> DiffReport:
        """Loads snapshots from JSON files and performs comparison."""
        snap_a = RKBEvidenceSnapshot.from_file(path_a)
        snap_b = RKBEvidenceSnapshot.from_file(path_b)
        return cls.compare_snapshots(snap_a, snap_b)
