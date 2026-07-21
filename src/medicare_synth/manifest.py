"""Source baseline manifest models and verification functions.

Manages source metadata, file grain definitions, and SHA-256 checksum verification
for official CMS synthetic claims collections.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ForeignKeyContract(BaseModel):
    """Foreign key relationship specification between source files."""

    model_config = ConfigDict(frozen=True)

    field: str
    target_file_id: str
    target_field: str


class FileManifest(BaseModel):
    """Manifest specification for a single synthetic baseline file."""

    model_config = ConfigDict(frozen=True)

    file_id: str
    filename: str
    file_domain: str
    grain: str
    format: str
    expected_record_count: int = Field(gt=0)
    sha256: str
    source_url: str
    primary_key: List[str]
    foreign_keys: Optional[List[ForeignKeyContract]] = None

    def verify_checksum(self, file_path: Path) -> bool:
        """Verify SHA-256 checksum of an existing local file against manifest specification."""
        if not file_path.is_file():
            return False
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest().lower() == self.sha256.lower()


class SourceManifest(BaseModel):
    """Top-level manifest contract for a CMS synthetic baseline collection release."""

    model_config = ConfigDict(frozen=True)

    collection_id: str
    title: str
    schema_year: int
    version: str
    description: str
    source_organization: str
    retrieval_date: str
    license: str
    files: List[FileManifest]

    @classmethod
    def from_file(cls, manifest_path: Path) -> "SourceManifest":
        """Load and validate a SourceManifest from a JSON file path."""
        with open(manifest_path, "r", encoding="utf-8") as f:
            data: Any = json.load(f)
        return cls.model_validate(data)

    @classmethod
    def load_default_manifest(cls, base_dir: Optional[Path] = None) -> "SourceManifest":
        """Loads default CMS 2021 Synthetic Claims manifest from data/manifests/."""
        target_dir = base_dir or Path("data/manifests")
        default_path = target_dir / "cms_2021_syn_claims_manifest.json"
        return cls.from_file(default_path)

    def get_file_manifest(self, file_id: str) -> Optional[FileManifest]:
        """Retrieve file manifest by file_id if present."""
        for fm in self.files:
            if fm.file_id == file_id:
                return fm
        return None
