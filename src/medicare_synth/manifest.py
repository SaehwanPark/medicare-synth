"""Source baseline manifest models and verification functions.

Manages source metadata, file grain definitions, and SHA-256 checksum verification
for official CMS synthetic claims collections.
"""

import hashlib
import json
from pathlib import Path
import re
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
    delimiter: str = ","
    archive_member: Optional[str] = None

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "FileManifest":
        value = super().model_validate(obj, **kwargs)
        if not re.fullmatch(r"[0-9a-fA-F]{64}", value.sha256):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        if len(value.delimiter) != 1:
            raise ValueError("delimiter must be one character")
        return value

    def verify_checksum(self, file_path: Path) -> bool:
        """Verify SHA-256 checksum of an existing local file against manifest specification."""
        if not file_path.is_file():
            return False
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest().lower() == self.sha256.lower()

    def verify_rows_and_header(self, file_path: Path) -> bool:
        """Verify the declared delimiter, header, and row count for a delimited file."""
        if not file_path.is_file() or not self.verify_checksum(file_path):
            return False
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            header = handle.readline().rstrip("\r\n")
            if header.split(self.delimiter) != self.primary_key and not set(
                self.primary_key
            ).issubset(set(header.split(self.delimiter))):
                return False
            return sum(1 for _ in handle) == self.expected_record_count


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

    def verify_directory(self, source_dir: Path) -> list[str]:
        """Return deterministic verification errors for all declared source files."""
        errors: list[str] = []
        for file_manifest in self.files:
            path = source_dir / file_manifest.filename
            try:
                path.resolve().relative_to(source_dir.resolve())
            except ValueError:
                errors.append(
                    f"file is outside source directory: {file_manifest.filename}"
                )
                continue
            if not file_manifest.verify_checksum(path):
                errors.append(f"checksum or missing file: {file_manifest.filename}")
                continue
            if file_manifest.format.lower() in {
                "csv",
                "text",
                "txt",
            } and not file_manifest.verify_rows_and_header(path):
                errors.append(f"header or row count mismatch: {file_manifest.filename}")
        return errors
