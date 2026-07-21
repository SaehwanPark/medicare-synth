"""ResDAC Knowledge Base (RKB) evidence snapshot contracts and models.

Encapsulates variable definitions, provenance tags, data types, and constraint definitions
sourced from versioned RKB snapshots.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class VariableContract(BaseModel):
    """Contract specification for a single CCW variable in the RKB evidence snapshot."""

    model_config = ConfigDict(frozen=True)

    name: str
    label: str
    data_type: str
    format: Optional[str] = None
    max_length: Optional[int] = None
    nullable: bool = True
    provenance_status: str
    description: str
    valid_values: Optional[List[str]] = None


class ConstraintContract(BaseModel):
    """Constraint definition for relational, temporal, or administrative rules."""

    model_config = ConfigDict(frozen=True)

    constraint_id: str
    category: str
    description: str
    rule: str


class RKBEvidenceSnapshot(BaseModel):
    """Snapshot contract representing versioned ResDAC Knowledge Base evidence."""

    model_config = ConfigDict(frozen=True)

    rkb_version: str
    snapshot_date: str
    schema_year: int
    description: str
    source_repository: str
    variables: Dict[str, VariableContract]
    constraints: List[ConstraintContract]

    @classmethod
    def from_file(cls, snapshot_path: Path) -> "RKBEvidenceSnapshot":
        """Load and validate an RKBEvidenceSnapshot from a JSON file path."""
        with open(snapshot_path, "r", encoding="utf-8") as f:
            data: Any = json.load(f)
        return cls.model_validate(data)

    @classmethod
    def load_default_snapshot(
        cls, base_dir: Optional[Path] = None
    ) -> "RKBEvidenceSnapshot":
        """Loads default RKB snapshot from data/rkb_snapshots/."""
        target_dir = base_dir or Path("data/rkb_snapshots")
        default_path = target_dir / "rkb-v1.0-20211231.json"
        return cls.from_file(default_path)

    def get_variable(self, variable_name: str) -> Optional[VariableContract]:
        """Look up a variable contract by CCW variable name."""
        return self.variables.get(variable_name)
