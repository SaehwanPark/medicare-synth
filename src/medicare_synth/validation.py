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
  def check_admission_temporal_inversions(claim_df: pl.DataFrame, claim_type: str) -> list[Finding]:
    """Identifies claims where admission date (clm_admsn_dt) exceeds discharge date (nch_bene_dschrg_dt)."""
    if claim_df.is_empty() or "clm_admsn_dt" not in claim_df.columns or "nch_bene_dschrg_dt" not in claim_df.columns:
      return []

    inverted = claim_df.filter(pl.col("clm_admsn_dt") > pl.col("nch_bene_dschrg_dt"))
    inversion_count = inverted.height

    if inversion_count > 0:
      sample_ids = inverted.select("clm_id").slice(0, 5).to_series().to_list() if "clm_id" in inverted.columns else []
      return [
        Finding(
          rule_id="TMP-002",
          category=FindingCategory.TEMPORAL,
          severity=Severity.HIGH,
          message=f"Found {inversion_count} claims in {claim_type} with admission temporal inversion (clm_admsn_dt > nch_bene_dschrg_dt).",
          count=inversion_count,
          details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_pde_field_constraints(pde_df: pl.DataFrame) -> list[Finding]:
    """Identifies PDE events with negative days supply or total prescription cost."""
    if pde_df.is_empty() or "days_suply_num" not in pde_df.columns or "tot_rx_cst_amt" not in pde_df.columns:
      return []

    invalid = pde_df.filter((pl.col("days_suply_num") < 0) | (pl.col("tot_rx_cst_amt") < 0))
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("pde_id").slice(0, 5).to_series().to_list() if "pde_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-001",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} PDE events with invalid negative days supply or prescription cost amount.",
          count=invalid_count,
          details={"table_name": "Prescription Drug Events", "sample_pde_ids": sample_ids},
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

  @staticmethod
  def check_snf_field_constraints(snf_df: pl.DataFrame) -> list[Finding]:

    """Identifies SNF claims with negative utilization days or non-covered days."""
    if snf_df.is_empty() or "clm_utlztn_day_cnt" not in snf_df.columns or "ncvd_days_cnt" not in snf_df.columns:
      return []

    invalid = snf_df.filter((pl.col("clm_utlztn_day_cnt") < 0) | (pl.col("ncvd_days_cnt") < 0))
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("clm_id").slice(0, 5).to_series().to_list() if "clm_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-002",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} SNF claims with invalid negative utilization days or non-covered days count.",
          count=invalid_count,
          details={"table_name": "SNF Claims", "sample_clm_ids": sample_ids},
        )
      ]
    return []

  def validate_slice(
    self,
    bene_df: pl.DataFrame,
    carrier_df: Optional[pl.DataFrame] = None,
    outpatient_df: Optional[pl.DataFrame] = None,
    inpatient_df: Optional[pl.DataFrame] = None,
    pde_df: Optional[pl.DataFrame] = None,
    snf_df: Optional[pl.DataFrame] = None,
  ) -> ValidationReport:
    """Executes full suite of relational, temporal, field, and record-level checks over a dataset slice."""
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

    if inpatient_df is not None and not inpatient_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, inpatient_df, "Inpatient Claims"))
      findings.extend(self.check_admission_temporal_inversions(inpatient_df, "Inpatient Claims"))
      findings.extend(self.check_record_uniqueness(inpatient_df, ["clm_id"], "Inpatient Claims"))

    if pde_df is not None and not pde_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, pde_df, "Prescription Drug Events"))
      findings.extend(self.check_pde_field_constraints(pde_df))
      findings.extend(self.check_record_uniqueness(pde_df, ["pde_id"], "Prescription Drug Events"))

    if snf_df is not None and not snf_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, snf_df, "SNF Claims"))
      findings.extend(self.check_admission_temporal_inversions(snf_df, "SNF Claims"))
      findings.extend(self.check_snf_field_constraints(snf_df))
      findings.extend(self.check_record_uniqueness(snf_df, ["clm_id"], "SNF Claims"))

    return ValidationReport(findings=findings)
