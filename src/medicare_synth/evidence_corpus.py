"""Versioned Evidence IR corpus registry with frozen partitions and checksums.

Phase 3: curate train / holdout / diagnostic / excluded findings before
calibration. Frozen corpora refuse mutation. Engines run without the harness.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

from medicare_synth.evidence_ir import (
  ComparabilityGrade,
  ComparisonReport,
  EvidenceIRError,
  EvidenceRole,
  FindingIR,
  compile_finding,
  execute_finding,
  load_finding,
  package_fixtures_dir,
)

CORPUS_SCHEMA_VERSION = "1.0"


class PartitionName(str, Enum):
  CALIBRATION = "calibration"
  HOLDOUT = "holdout"
  DIAGNOSTIC = "diagnostic"
  EXCLUDED = "excluded"


class Executability(str, Enum):
  EXECUTABLE = "executable"
  APPROXIMATED = "approximated"
  NON_EXECUTABLE = "non_executable"


class CorpusEntry(BaseModel):
  """One registry row linking a finding fixture into a partition."""

  model_config = ConfigDict(frozen=True)

  finding_id: str
  inventory_id: str | None = None
  partition: PartitionName
  relative_path: str
  sha256: str
  comparability_grade: ComparabilityGrade
  executability: Executability
  rationale: str


class EvidenceCorpus(BaseModel):
  """Frozen or draft MVP evidence corpus."""

  model_config = ConfigDict(frozen=True)

  schema_version: str = CORPUS_SCHEMA_VERSION
  corpus_id: str
  context_id: str = "mvp-2021-om-ffs-diabetes-ip"
  title: str
  frozen: bool = False
  frozen_at: str | None = None
  reviewer: str | None = None
  review_rationale: str | None = None
  entries: tuple[CorpusEntry, ...] = Field(..., min_length=1)

  @model_validator(mode="after")
  def _check_freeze_metadata(self) -> EvidenceCorpus:
    if self.schema_version != CORPUS_SCHEMA_VERSION:
      raise ValueError(
        f"unsupported corpus schema_version {self.schema_version!r}; "
        f"expected {CORPUS_SCHEMA_VERSION!r}"
      )
    if self.frozen:
      if not self.frozen_at or not self.reviewer:
        raise ValueError("frozen corpora require frozen_at and reviewer")
    ids = [e.finding_id for e in self.entries]
    if len(ids) != len(set(ids)):
      raise ValueError("duplicate finding_id in corpus entries")
    return self

  def partition_entries(self, partition: PartitionName) -> tuple[CorpusEntry, ...]:
    return tuple(e for e in self.entries if e.partition == partition)

  def finding_ids(self, partition: PartitionName | None = None) -> tuple[str, ...]:
    if partition is None:
      return tuple(e.finding_id for e in self.entries)
    return tuple(e.finding_id for e in self.partition_entries(partition))


class CorpusError(EvidenceIRError):
  """Corpus load / verify / freeze failure."""


def sha256_file(path: Path) -> str:
  digest = hashlib.sha256()
  digest.update(path.read_bytes())
  return digest.hexdigest()


def sha256_text(text: str) -> str:
  return hashlib.sha256(text.encode("utf-8")).hexdigest()


def package_corpus_dir() -> Path:
  return Path(__file__).resolve().parent / "fixtures" / "evidence_corpus"


def load_corpus(path: Path | str) -> EvidenceCorpus:
  p = Path(path)
  try:
    raw = json.loads(p.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as exc:
    raise CorpusError(f"failed to load corpus from {p}: {exc}") from exc
  if not isinstance(raw, dict):
    raise CorpusError(f"corpus root must be an object: {p}")
  try:
    return EvidenceCorpus.model_validate(raw)
  except Exception as exc:  # noqa: BLE001
    raise CorpusError(f"invalid corpus: {exc}") from exc


def resolve_finding_path(entry: CorpusEntry, *, fixtures_root: Path) -> Path:
  return (fixtures_root / entry.relative_path).resolve()


def verify_corpus_checksums(
  corpus: EvidenceCorpus,
  *,
  fixtures_root: Path | None = None,
) -> list[str]:
  """Return checksum mismatch / missing-file errors (empty if OK)."""
  root = fixtures_root or package_fixtures_dir().parent
  # fixtures_root should contain evidence_ir/ and evidence_corpus/
  errors: list[str] = []
  for entry in corpus.entries:
    path = resolve_finding_path(entry, fixtures_root=root)
    if not path.is_file():
      errors.append(f"{entry.finding_id}: missing file {path}")
      continue
    actual = sha256_file(path)
    if actual != entry.sha256:
      errors.append(
        f"{entry.finding_id}: sha256 mismatch "
        f"(expected {entry.sha256}, got {actual})"
      )
  return errors


def ensure_corpus_checksums(
  corpus: EvidenceCorpus,
  *,
  fixtures_root: Path | None = None,
) -> EvidenceCorpus:
  errors = verify_corpus_checksums(corpus, fixtures_root=fixtures_root)
  if errors:
    raise CorpusError("; ".join(errors))
  return corpus


def load_corpus_finding(
  corpus: EvidenceCorpus,
  finding_id: str,
  *,
  fixtures_root: Path | None = None,
) -> FindingIR:
  root = fixtures_root or package_fixtures_dir().parent
  for entry in corpus.entries:
    if entry.finding_id == finding_id:
      path = resolve_finding_path(entry, fixtures_root=root)
      if not path.is_file():
        raise CorpusError(f"{finding_id}: missing file {path}")
      actual = sha256_file(path)
      if actual != entry.sha256:
        raise CorpusError(
          f"{finding_id}: sha256 mismatch (expected {entry.sha256}, got {actual})"
        )
      finding = load_finding(path)
      if finding.finding_id != finding_id:
        raise CorpusError(
          f"fixture finding_id {finding.finding_id!r} != registry {finding_id!r}"
        )
      return finding
  raise CorpusError(f"finding_id not in corpus: {finding_id}")


def load_partition_findings(
  corpus: EvidenceCorpus,
  partition: PartitionName,
  *,
  fixtures_root: Path | None = None,
) -> tuple[FindingIR, ...]:
  return tuple(
    load_corpus_finding(corpus, e.finding_id, fixtures_root=fixtures_root)
    for e in corpus.partition_entries(partition)
  )


def classify_executability(finding: FindingIR, *, context_year: int = 2021) -> Executability:
  compiled = compile_finding(finding, context_year=context_year)
  if not compiled.compatibility.executable:
    return Executability.NON_EXECUTABLE
  if compiled.compatibility.approximating_algorithms or any(
    i.severity == "warning" for i in compiled.compatibility.issues
  ):
    return Executability.APPROXIMATED
  return Executability.EXECUTABLE


def assert_active_partition_support(
  corpus: EvidenceCorpus,
  *,
  fixtures_root: Path | None = None,
  context_year: int = 2021,
) -> list[str]:
  """Active (calibration+holdout) findings must be executable or approximated."""
  errors: list[str] = []
  for part in (PartitionName.CALIBRATION, PartitionName.HOLDOUT):
    for entry in corpus.partition_entries(part):
      finding = load_corpus_finding(
        corpus, entry.finding_id, fixtures_root=fixtures_root
      )
      status = classify_executability(finding, context_year=context_year)
      if status == Executability.NON_EXECUTABLE:
        errors.append(
          f"{entry.finding_id} in {part.value} is non-executable"
        )
      if entry.executability == Executability.NON_EXECUTABLE:
        errors.append(
          f"{entry.finding_id} registry executability is non_executable "
          f"but partition is {part.value}"
        )
      # Registry role on FindingIR should align with partition
      expected_role = {
        PartitionName.CALIBRATION: EvidenceRole.CALIBRATION,
        PartitionName.HOLDOUT: EvidenceRole.HOLDOUT,
      }[part]
      if finding.role != expected_role:
        errors.append(
          f"{entry.finding_id}: finding.role={finding.role.value} "
          f"!= partition {part.value}"
        )
  return errors


def execute_partition(
  corpus: EvidenceCorpus,
  partition: PartitionName,
  tables: Mapping[str, Any],
  *,
  fixtures_root: Path | None = None,
  context_year: int = 2021,
) -> tuple[ComparisonReport, ...]:
  """Execute all findings in a partition against synthetic tables."""
  if partition == PartitionName.EXCLUDED:
    raise CorpusError("refusing to execute excluded partition")
  findings = load_partition_findings(
    corpus, partition, fixtures_root=fixtures_root
  )
  return tuple(
    execute_finding(f, tables, context_year=context_year) for f in findings
  )


def freeze_corpus(
  corpus: EvidenceCorpus,
  *,
  frozen_at: str,
  reviewer: str,
  rationale: str,
) -> EvidenceCorpus:
  """Return a frozen copy; refuses if already frozen."""
  if corpus.frozen:
    raise CorpusError(f"corpus {corpus.corpus_id} is already frozen")
  return corpus.model_copy(
    update={
      "frozen": True,
      "frozen_at": frozen_at,
      "reviewer": reviewer,
      "review_rationale": rationale,
    }
  )


def replace_entry(
  corpus: EvidenceCorpus,
  entry: CorpusEntry,
) -> EvidenceCorpus:
  """Replace or append an entry; refused when frozen."""
  if corpus.frozen:
    raise CorpusError(f"cannot mutate frozen corpus {corpus.corpus_id}")
  others = [e for e in corpus.entries if e.finding_id != entry.finding_id]
  return corpus.model_copy(update={"entries": tuple([*others, entry])})


def build_entry_from_finding_file(
  *,
  path: Path,
  partition: PartitionName,
  relative_path: str,
  rationale: str,
  context_year: int = 2021,
) -> CorpusEntry:
  """Helper to construct a registry entry from a finding JSON file."""
  finding = load_finding(path)
  status = classify_executability(finding, context_year=context_year)
  return CorpusEntry(
    finding_id=finding.finding_id,
    inventory_id=finding.inventory_id,
    partition=partition,
    relative_path=relative_path,
    sha256=sha256_file(path),
    comparability_grade=finding.comparability.grade,
    executability=status,
    rationale=rationale,
  )


def default_mvp_corpus_path() -> Path:
  return package_corpus_dir() / "mvp_2021_om_ffs_diabetes_ip_corpus_v1.json"
