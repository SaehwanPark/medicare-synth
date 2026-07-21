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

  @staticmethod
  def check_hha_field_constraints(hha_df: pl.DataFrame) -> list[Finding]:
    """Identifies HHA claims with negative utilization days count."""
    if hha_df.is_empty() or "clm_utlztn_day_cnt" not in hha_df.columns:
      return []

    invalid = hha_df.filter(pl.col("clm_utlztn_day_cnt") < 0)
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("clm_id").slice(0, 5).to_series().to_list() if "clm_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-003",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} HHA claims with invalid negative utilization days count.",
          count=invalid_count,
          details={"table_name": "HHA Claims", "sample_clm_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_dme_field_constraints(dme_df: pl.DataFrame) -> list[Finding]:
    """Identifies DME claims with invalid line item count less than 1."""
    if dme_df.is_empty() or "dme_line_item_count" not in dme_df.columns:
      return []

    invalid = dme_df.filter(pl.col("dme_line_item_count") < 1)
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("clm_id").slice(0, 5).to_series().to_list() if "clm_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-004",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} DME claims with invalid line item count less than 1.",
          count=invalid_count,
          details={"table_name": "DME Claims", "sample_clm_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_hospice_field_constraints(hospice_df: pl.DataFrame) -> list[Finding]:
    """Identifies Hospice claims with negative utilization days count."""
    if hospice_df.is_empty() or "clm_utlztn_day_cnt" not in hospice_df.columns:
      return []

    invalid = hospice_df.filter(pl.col("clm_utlztn_day_cnt") < 0)
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("clm_id").slice(0, 5).to_series().to_list() if "clm_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-005",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} Hospice claims with invalid negative utilization days count.",
          count=invalid_count,
          details={"table_name": "Hospice Claims", "sample_clm_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_mbsf_cc_field_constraints(mbsf_cc_df: pl.DataFrame) -> list[Finding]:
    """Identifies MBSF Chronic Condition records with invalid indicator values not in {'0', '1', '2'}."""
    if mbsf_cc_df.is_empty():
      return []

    cc_cols = [col for col in mbsf_cc_df.columns if col.startswith("sp_")]
    if not cc_cols:
      return []

    invalid_expr = pl.any_horizontal([~pl.col(c).is_in(["0", "1", "2"]) for c in cc_cols])
    invalid = mbsf_cc_df.filter(invalid_expr)
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("bene_id").slice(0, 5).to_series().to_list() if "bene_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-006",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} MBSF Chronic Condition records with invalid indicator value outside {{'0', '1', '2'}}.",
          count=invalid_count,
          details={"table_name": "MBSF Chronic Conditions", "sample_bene_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_mbsf_cu_field_constraints(mbsf_cu_df: pl.DataFrame) -> list[Finding]:
    """Identifies MBSF Cost & Use records with negative payment/days metrics or total pay less than Medicare pay."""
    if mbsf_cu_df.is_empty():
      return []

    invalid = mbsf_cu_df.filter(
      (pl.col("bene_mdcr_pay_amt") < 0)
      | (pl.col("bene_tot_pay_amt") < 0)
      | (pl.col("bene_ip_ddctbl_amt") < 0)
      | (pl.col("bene_cvrd_dys_cnt") < 0)
      | (pl.col("bene_tot_pay_amt") < pl.col("bene_mdcr_pay_amt"))
    )
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("bene_id").slice(0, 5).to_series().to_list() if "bene_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-007",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} MBSF Cost & Use records violating non-negative payment or covered day constraints.",
          count=invalid_count,
          details={"table_name": "MBSF Cost & Use", "sample_bene_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_mbsf_d_field_constraints(mbsf_d_df: pl.DataFrame) -> list[Finding]:
    """Identifies MBSF Part D records with negative drug cost or out-of-pocket metrics."""
    if mbsf_d_df.is_empty():
      return []

    invalid = mbsf_d_df.filter(
      (pl.col("bene_ptd_trcc_amt") < 0)
      | (pl.col("bene_ptd_moop_amt") < 0)
    )
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("bene_id").slice(0, 5).to_series().to_list() if "bene_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-008",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} MBSF Part D records violating non-negative cost constraints.",
          count=invalid_count,
          details={"table_name": "MBSF Part D", "sample_bene_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_mbsf_base_field_constraints(mbsf_base_df: pl.DataFrame) -> list[Finding]:
    """Identifies MBSF Base records with invalid coverage month bounds (outside 0..12)."""
    if mbsf_base_df.is_empty():
      return []

    invalid = mbsf_base_df.filter(
      (pl.col("bene_hi_cvrage_tot_mons") < 0)
      | (pl.col("bene_hi_cvrage_tot_mons") > 12)
      | (pl.col("bene_smi_cvrage_tot_mons") < 0)
      | (pl.col("bene_smi_cvrage_tot_mons") > 12)
      | (pl.col("bene_hmo_cvrage_tot_mons") < 0)
      | (pl.col("bene_hmo_cvrage_tot_mons") > 12)
      | (pl.col("bene_ptd_cvrage_tot_mons") < 0)
      | (pl.col("bene_ptd_cvrage_tot_mons") > 12)
    )
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("bene_id").slice(0, 5).to_series().to_list() if "bene_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-009",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} MBSF Base records violating 0-12 coverage month constraints.",
          count=invalid_count,
          details={"table_name": "MBSF Base Enrollment", "sample_bene_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_mbsf_oc_field_constraints(mbsf_oc_df: pl.DataFrame) -> list[Finding]:
    """Identifies MBSF Other Chronic records with invalid indicator values (not in 0, 1, 2)."""
    if mbsf_oc_df.is_empty():
      return []

    indicators = [
      "sp_arthglau",
      "sp_asthma",
      "sp_atrialf",
      "sp_hyperl",
      "sp_hypert",
      "sp_hypot",
      "sp_osteop",
    ]
    valid_set = ["0", "1", "2"]
    filter_expr = pl.lit(False)
    for col_name in indicators:
      if col_name in mbsf_oc_df.columns:
        filter_expr = filter_expr | (~pl.col(col_name).is_in(valid_set))

    invalid = mbsf_oc_df.filter(filter_expr)
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("bene_id").slice(0, 5).to_series().to_list() if "bene_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-010",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} MBSF Other Chronic records with invalid chronic condition indicators.",
          count=invalid_count,
          details={"table_name": "MBSF Other Chronic Conditions", "sample_bene_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_mbsf_ndi_field_constraints(mbsf_ndi_df: pl.DataFrame) -> list[Finding]:
    """Identifies MBSF NDI records with invalid match indicator values (not in '0', '1', 'Y', 'N')."""
    if mbsf_ndi_df.is_empty():
      return []

    if "ndi_match_ind" not in mbsf_ndi_df.columns:
      return []

    valid_set = ["0", "1", "Y", "N"]
    invalid = mbsf_ndi_df.filter(~pl.col("ndi_match_ind").is_in(valid_set))
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("bene_id").slice(0, 5).to_series().to_list() if "bene_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-011",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} MBSF NDI records with invalid NDI match indicator.",
          count=invalid_count,
          details={"table_name": "MBSF NDI", "sample_bene_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_mbsf_ra_field_constraints(mbsf_ra_df: pl.DataFrame) -> list[Finding]:
    """Identifies MBSF Risk Adjustment records with negative risk scores or payment counts out of bounds."""
    if mbsf_ra_df.is_empty():
      return []

    invalid_expr = pl.lit(False)
    if "cms_hcc_risk_score" in mbsf_ra_df.columns:
      invalid_expr = invalid_expr | (pl.col("cms_hcc_risk_score") < 0)
    if "rxhcc_risk_score" in mbsf_ra_df.columns:
      invalid_expr = invalid_expr | (pl.col("rxhcc_risk_score") < 0)
    if "payment_count" in mbsf_ra_df.columns:
      invalid_expr = invalid_expr | (pl.col("payment_count") < 0) | (pl.col("payment_count") > 12)

    invalid = mbsf_ra_df.filter(invalid_expr)
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("bene_id").slice(0, 5).to_series().to_list() if "bene_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-012",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} MBSF Risk Adjustment records with negative risk scores or invalid payment count.",
          count=invalid_count,
          details={"table_name": "MBSF Risk Adjustment", "sample_bene_ids": sample_ids},
        )
      ]
    return []

  @staticmethod
  def check_mbsf_c_field_constraints(mbsf_c_df: pl.DataFrame) -> list[Finding]:
    """Identifies MBSF Part C records with coverage month count out of bounds (0..12)."""
    if mbsf_c_df.is_empty():
      return []

    if "bene_ma_cvrage_tot_mons" not in mbsf_c_df.columns:
      return []

    invalid = mbsf_c_df.filter(
      (pl.col("bene_ma_cvrage_tot_mons") < 0) | (pl.col("bene_ma_cvrage_tot_mons") > 12)
    )
    invalid_count = invalid.height

    if invalid_count > 0:
      sample_ids = invalid.select("bene_id").slice(0, 5).to_series().to_list() if "bene_id" in invalid.columns else []
      return [
        Finding(
          rule_id="FLD-013",
          category=FindingCategory.FIELD,
          severity=Severity.HIGH,
          message=f"Found {invalid_count} MBSF Part C records violating 0-12 coverage month constraints.",
          count=invalid_count,
          details={"table_name": "MBSF Part C", "sample_bene_ids": sample_ids},
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
    hha_df: Optional[pl.DataFrame] = None,
    dme_df: Optional[pl.DataFrame] = None,
    hospice_df: Optional[pl.DataFrame] = None,
    mbsf_cc_df: Optional[pl.DataFrame] = None,
    mbsf_cu_df: Optional[pl.DataFrame] = None,
    mbsf_d_df: Optional[pl.DataFrame] = None,
    mbsf_base_df: Optional[pl.DataFrame] = None,
    mbsf_oc_df: Optional[pl.DataFrame] = None,
    mbsf_ndi_df: Optional[pl.DataFrame] = None,
    mbsf_ra_df: Optional[pl.DataFrame] = None,
    mbsf_c_df: Optional[pl.DataFrame] = None,
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

    if hha_df is not None and not hha_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, hha_df, "HHA Claims"))
      findings.extend(self.check_admission_temporal_inversions(hha_df, "HHA Claims"))
      findings.extend(self.check_hha_field_constraints(hha_df))
      findings.extend(self.check_record_uniqueness(hha_df, ["clm_id"], "HHA Claims"))

    if dme_df is not None and not dme_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, dme_df, "DME Claims"))
      findings.extend(self.check_temporal_inversions(dme_df, "DME Claims"))
      findings.extend(self.check_dme_field_constraints(dme_df))
      if "line_num" in dme_df.columns:
        findings.extend(self.check_record_uniqueness(dme_df, ["clm_id", "line_num"], "DME Claims"))

    if hospice_df is not None and not hospice_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, hospice_df, "Hospice Claims"))
      findings.extend(self.check_admission_temporal_inversions(hospice_df, "Hospice Claims"))
      findings.extend(self.check_hospice_field_constraints(hospice_df))
      findings.extend(self.check_record_uniqueness(hospice_df, ["clm_id"], "Hospice Claims"))

    if mbsf_cc_df is not None and not mbsf_cc_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, mbsf_cc_df, "MBSF Chronic Conditions"))
      findings.extend(self.check_mbsf_cc_field_constraints(mbsf_cc_df))
      findings.extend(self.check_record_uniqueness(mbsf_cc_df, ["bene_id"], "MBSF Chronic Conditions"))

    if mbsf_cu_df is not None and not mbsf_cu_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, mbsf_cu_df, "MBSF Cost & Use"))
      findings.extend(self.check_mbsf_cu_field_constraints(mbsf_cu_df))
      findings.extend(self.check_record_uniqueness(mbsf_cu_df, ["bene_id"], "MBSF Cost & Use"))

    if mbsf_d_df is not None and not mbsf_d_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, mbsf_d_df, "MBSF Part D"))
      findings.extend(self.check_mbsf_d_field_constraints(mbsf_d_df))
      findings.extend(self.check_record_uniqueness(mbsf_d_df, ["bene_id"], "MBSF Part D"))

    if mbsf_base_df is not None and not mbsf_base_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, mbsf_base_df, "MBSF Base Enrollment"))
      findings.extend(self.check_mbsf_base_field_constraints(mbsf_base_df))
      findings.extend(self.check_record_uniqueness(mbsf_base_df, ["bene_id"], "MBSF Base Enrollment"))

    if mbsf_oc_df is not None and not mbsf_oc_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, mbsf_oc_df, "MBSF Other Chronic Conditions"))
      findings.extend(self.check_mbsf_oc_field_constraints(mbsf_oc_df))
      findings.extend(self.check_record_uniqueness(mbsf_oc_df, ["bene_id"], "MBSF Other Chronic Conditions"))

    if mbsf_ndi_df is not None and not mbsf_ndi_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, mbsf_ndi_df, "MBSF NDI"))
      findings.extend(self.check_mbsf_ndi_field_constraints(mbsf_ndi_df))
      findings.extend(self.check_record_uniqueness(mbsf_ndi_df, ["bene_id"], "MBSF NDI"))

    if mbsf_ra_df is not None and not mbsf_ra_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, mbsf_ra_df, "MBSF Risk Adjustment"))
      findings.extend(self.check_mbsf_ra_field_constraints(mbsf_ra_df))
      findings.extend(self.check_record_uniqueness(mbsf_ra_df, ["bene_id"], "MBSF Risk Adjustment"))

    if mbsf_c_df is not None and not mbsf_c_df.is_empty():
      findings.extend(self.check_orphaned_claims(bene_df, mbsf_c_df, "MBSF Part C"))
      findings.extend(self.check_mbsf_c_field_constraints(mbsf_c_df))
      findings.extend(self.check_record_uniqueness(mbsf_c_df, ["bene_id"], "MBSF Part C"))

    return ValidationReport(findings=findings)
