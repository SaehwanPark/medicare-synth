"""Validation framework and relational validators for Medicare synthetic data.

Provides typed validation findings, validation reports, and high-performance Polars-backed
relational and temporal validators across beneficiary and claim tables.
"""

from enum import Enum
from typing import Any, Optional

import polars as pl
from pydantic import BaseModel, ConfigDict, Field


class Severity(str, Enum):
  """Severity levels for validation findings."""

  INFO = "INFO"
  WARNING = "WARNING"
  HIGH = "HIGH"
  CRITICAL = "CRITICAL"


class FindingCategory(str, Enum):
  """Categories of validation rules per Foundation decision set."""

  FIELD = "FIELD"
  RECORD = "RECORD"
  RELATIONAL = "RELATIONAL"
  TEMPORAL = "TEMPORAL"
  ADMINISTRATIVE = "ADMINISTRATIVE"


class Finding(BaseModel):
  """Single validation finding describing a constraint violation or anomaly."""

  model_config = ConfigDict(frozen=True)

  rule_id: str = Field(..., description="Unique code identifying the validation rule")
  category: FindingCategory = Field(..., description="Category of validation constraint")
  severity: Severity = Field(..., description="Severity level of the finding")
  message: str = Field(..., description="Human-readable explanation of the finding")
  count: int = Field(default=1, ge=0, description="Number of violating records")
  details: Optional[dict[str, Any]] = Field(default=None, description="Optional context or key samples")


class ValidationReport(BaseModel):
  """Aggregated validation report containing findings across a dataset slice."""

  model_config = ConfigDict(frozen=True)

  findings: list[Finding] = Field(default_factory=list, description="List of recorded validation findings")

  @property
  def is_valid(self) -> bool:
    """Returns True if there are no HIGH or CRITICAL findings."""
    return not any(f.severity in (Severity.HIGH, Severity.CRITICAL) for f in self.findings)

  def count_by_severity(self) -> dict[Severity, int]:
    """Returns a breakdown of finding counts grouped by severity."""
    counts = {sev: 0 for sev in Severity}
    for f in self.findings:
      counts[f.severity] += f.count
    return counts


class RelationalValidator:
  """Polars-backed relational and temporal validator for Medicare dataset slices."""

  @staticmethod
  def check_orphaned_claims(bene_df: pl.DataFrame, claim_df: pl.DataFrame, claim_type: str) -> list[Finding]:
    """Identifies claims with BENE_ID not present in the Beneficiary Summary table."""
    if claim_df.is_empty() or "bene_id" not in claim_df.columns or "bene_id" not in bene_df.columns:
      return []

    orphaned = claim_df.join(bene_df, on="bene_id", how="anti")
    orphan_count = orphaned.height

    if orphan_count > 0:
      sample_ids = orphaned.select("clm_id").slice(0, 5).to_series().to_list() if "clm_id" in orphaned.columns else []
      return [
        Finding(
          rule_id="REL-001",
          category=FindingCategory.RELATIONAL,
          severity=Severity.CRITICAL,
          message=f"Found {orphan_count} orphaned claim records in {claim_type} without a valid beneficiary entry.",
          count=orphan_count,
          details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_temporal_inversions(claim_df: pl.DataFrame, claim_type: str) -> list[Finding]:
    """Identifies claims where service start date (clm_from_dt) exceeds service end date (clm_thru_dt)."""
    if claim_df.is_empty() or "clm_from_dt" not in claim_df.columns or "clm_thru_dt" not in claim_df.columns:
      return []

    inverted = claim_df.filter(pl.col("clm_from_dt") > pl.col("clm_thru_dt"))
    inversion_count = inverted.height

    if inversion_count > 0:
      sample_ids = inverted.select("clm_id").slice(0, 5).to_series().to_list() if "clm_id" in inverted.columns else []
      return [
        Finding(
          rule_id="TMP-001",
          category=FindingCategory.TEMPORAL,
          severity=Severity.HIGH,
          message=f"Found {inversion_count} claims in {claim_type} with temporal inversion (clm_from_dt > clm_thru_dt).",
          count=inversion_count,
          details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_record_uniqueness(df: pl.DataFrame, keys: list[str], table_name: str) -> list[Finding]:
    """Verifies uniqueness of specified primary or composite key columns."""
    if df.is_empty() or not set(keys).issubset(set(df.columns)):
      return []

    duplicates = df.filter(df.select(keys).is_duplicated())
    dup_count = duplicates.height

    if dup_count > 0:
      return [
        Finding(
          rule_id="REC-001",
          category=FindingCategory.RECORD,
          severity=Severity.CRITICAL,
          message=f"Found {dup_count} non-unique records in {table_name} matching keys {keys}.",
          count=dup_count,
          details={"table_name": table_name, "keys": keys},
        )
      ]
    return []

  def validate_slice(
    self,
    bene_df: pl.DataFrame,
    carrier_df: Optional[pl.DataFrame] = None,
    outpatient_df: Optional[pl.DataFrame] = None,
  ) -> ValidationReport:
    """Executes full suite of relational, temporal, and record-level checks over a dataset slice."""
    findings: list[Finding] = []

    # Record uniqueness
    findings.extend(self.check_record_uniqueness(bene_df, ["bene_id"], "Beneficiary Summary"))

    if carrier_df is not None and not carrier_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, carrier_df, "Carrier Claims"))
      findings.extend(self.check_temporal_inversions(carrier_df, "Carrier Claims"))
      if "line_num" in carrier_df.columns:
        findings.extend(self.check_record_uniqueness(carrier_df, ["clm_id", "line_num"], "Carrier Claims"))

    if outpatient_df is not None and not outpatient_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, outpatient_df, "Outpatient Claims"))
      findings.extend(self.check_temporal_inversions(outpatient_df, "Outpatient Claims"))
      findings.extend(self.check_record_uniqueness(outpatient_df, ["clm_id"], "Outpatient Claims"))

    return ValidationReport(findings=findings)
