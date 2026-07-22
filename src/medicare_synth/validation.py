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
    category: FindingCategory = Field(
        ..., description="Category of validation constraint"
    )
    severity: Severity = Field(..., description="Severity level of the finding")
    message: str = Field(..., description="Human-readable explanation of the finding")
    count: int = Field(default=1, ge=0, description="Number of violating records")
    details: Optional[dict[str, Any]] = Field(
        default=None, description="Optional context or key samples"
    )


class ValidationReport(BaseModel):
    """Aggregated validation report containing findings across a dataset slice."""

    model_config = ConfigDict(frozen=True)

    findings: list[Finding] = Field(
        default_factory=list, description="List of recorded validation findings"
    )

    @property
    def is_valid(self) -> bool:
        """Returns True if there are no HIGH or CRITICAL findings."""
        return not any(
            f.severity in (Severity.HIGH, Severity.CRITICAL) for f in self.findings
        )

    def count_by_severity(self) -> dict[Severity, int]:
        """Returns a breakdown of finding counts grouped by severity."""
        counts = {sev: 0 for sev in Severity}
        for f in self.findings:
            counts[f.severity] += f.count
        return counts


class RelationalValidator:
    """Polars-backed relational and temporal validator for Medicare dataset slices."""

    @staticmethod
    def check_orphaned_claims(
        bene_df: pl.DataFrame, claim_df: pl.DataFrame, claim_type: str
    ) -> list[Finding]:
        """Identifies claims with BENE_ID not present in the Beneficiary Summary table."""
        if (
            claim_df.is_empty()
            or "bene_id" not in claim_df.columns
            or "bene_id" not in bene_df.columns
        ):
            return []

        orphaned = claim_df.join(bene_df, on="bene_id", how="anti")
        orphan_count = orphaned.height

        if orphan_count > 0:
            sample_ids = (
                orphaned.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in orphaned.columns
                else []
            )
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
    def check_temporal_inversions(
        claim_df: pl.DataFrame, claim_type: str
    ) -> list[Finding]:
        """Identifies claims where service start date (clm_from_dt) exceeds service end date (clm_thru_dt)."""
        if (
            claim_df.is_empty()
            or "clm_from_dt" not in claim_df.columns
            or "clm_thru_dt" not in claim_df.columns
        ):
            return []

        inverted = claim_df.filter(pl.col("clm_from_dt") > pl.col("clm_thru_dt"))
        inversion_count = inverted.height

        if inversion_count > 0:
            sample_ids = (
                inverted.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in inverted.columns
                else []
            )
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
    def check_admission_temporal_inversions(
        claim_df: pl.DataFrame, claim_type: str
    ) -> list[Finding]:
        """Identifies claims where admission date (clm_admsn_dt) exceeds discharge date (nch_bene_dschrg_dt)."""
        if (
            claim_df.is_empty()
            or "clm_admsn_dt" not in claim_df.columns
            or "nch_bene_dschrg_dt" not in claim_df.columns
        ):
            return []

        inverted = claim_df.filter(
            pl.col("clm_admsn_dt") > pl.col("nch_bene_dschrg_dt")
        )
        inversion_count = inverted.height

        if inversion_count > 0:
            sample_ids = (
                inverted.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in inverted.columns
                else []
            )
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
        if (
            pde_df.is_empty()
            or "days_suply_num" not in pde_df.columns
            or "tot_rx_cst_amt" not in pde_df.columns
        ):
            return []

        invalid = pde_df.filter(
            (pl.col("days_suply_num") < 0) | (pl.col("tot_rx_cst_amt") < 0)
        )
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("pde_id").slice(0, 5).to_series().to_list()
                if "pde_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-001",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} PDE events with invalid negative days supply or prescription cost amount.",
                    count=invalid_count,
                    details={
                        "table_name": "Prescription Drug Events",
                        "sample_pde_ids": sample_ids,
                    },
                )
            ]
        return []

    @staticmethod
    def check_record_uniqueness(
        df: pl.DataFrame, keys: list[str], table_name: str
    ) -> list[Finding]:
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
    def check_inpatient_field_constraints(
        inpatient_df: pl.DataFrame,
    ) -> list[Finding]:
        """Identifies Inpatient claims with negative utilization days or non-covered days."""
        if (
            inpatient_df.is_empty()
            or "clm_utlztn_day_cnt" not in inpatient_df.columns
            or "ncvd_days_cnt" not in inpatient_df.columns
        ):
            return []

        invalid = inpatient_df.filter(
            (pl.col("clm_utlztn_day_cnt") < 0) | (pl.col("ncvd_days_cnt") < 0)
        )
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-006",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} Inpatient claims with invalid negative utilization days or non-covered days count.",
                    count=invalid_count,
                    details={
                        "table_name": "Inpatient Claims",
                        "sample_clm_ids": sample_ids,
                    },
                )
            ]
        return []

    @staticmethod
    def check_snf_field_constraints(snf_df: pl.DataFrame) -> list[Finding]:
        """Identifies SNF claims with negative utilization days or non-covered days."""
        if (
            snf_df.is_empty()
            or "clm_utlztn_day_cnt" not in snf_df.columns
            or "ncvd_days_cnt" not in snf_df.columns
        ):
            return []

        invalid = snf_df.filter(
            (pl.col("clm_utlztn_day_cnt") < 0) | (pl.col("ncvd_days_cnt") < 0)
        )
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
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
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
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
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
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
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-005",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} Hospice claims with invalid negative utilization days count.",
                    count=invalid_count,
                    details={
                        "table_name": "Hospice Claims",
                        "sample_clm_ids": sample_ids,
                    },
                )
            ]
        return []

    @staticmethod
    def check_carrier_field_constraints(carrier_df: pl.DataFrame) -> list[Finding]:
        """Identifies Carrier claims with line item numbers < 1 or temporal inversions."""
        if carrier_df.is_empty():
            return []

        conditions = []
        if "line_num" in carrier_df.columns:
            conditions.append(pl.col("line_num") < 1)
        if "clm_from_dt" in carrier_df.columns and "clm_thru_dt" in carrier_df.columns:
            conditions.append(pl.col("clm_from_dt") > pl.col("clm_thru_dt"))

        if not conditions:
            return []

        combined_condition = conditions[0]
        for cond in conditions[1:]:
            combined_condition = combined_condition | cond

        invalid = carrier_df.filter(combined_condition)
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-007",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} Carrier claim line items with invalid line number or date inversion.",
                    count=invalid_count,
                    details={
                        "table_name": "Carrier Claim Lines",
                        "sample_clm_ids": sample_ids,
                    },
                )
            ]
        return []

    @staticmethod
    def check_outpatient_field_constraints(
        outpatient_df: pl.DataFrame,
    ) -> list[Finding]:
        """Identifies Outpatient claims with negative payment amounts or temporal inversions."""
        if outpatient_df.is_empty():
            return []

        conditions = []
        if "clm_pmt_amt" in outpatient_df.columns:
            conditions.append(pl.col("clm_pmt_amt") < 0)
        if (
            "clm_from_dt" in outpatient_df.columns
            and "clm_thru_dt" in outpatient_df.columns
        ):
            conditions.append(pl.col("clm_from_dt") > pl.col("clm_thru_dt"))

        if not conditions:
            return []

        combined_condition = conditions[0]
        for cond in conditions[1:]:
            combined_condition = combined_condition | cond

        invalid = outpatient_df.filter(combined_condition)
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-008",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} Outpatient claims with negative payment amount or date inversion.",
                    count=invalid_count,
                    details={
                        "table_name": "Outpatient Claims",
                        "sample_clm_ids": sample_ids,
                    },
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

        invalid_expr = pl.any_horizontal(
            [~pl.col(c).is_in(["0", "1", "2"]) for c in cc_cols]
        )
        invalid = mbsf_cc_df.filter(invalid_expr)
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-006",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} MBSF Chronic Condition records with invalid indicator value outside {{'0', '1', '2'}}.",
                    count=invalid_count,
                    details={
                        "table_name": "MBSF Chronic Conditions",
                        "sample_bene_ids": sample_ids,
                    },
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
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-007",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} MBSF Cost & Use records violating non-negative payment or covered day constraints.",
                    count=invalid_count,
                    details={
                        "table_name": "MBSF Cost & Use",
                        "sample_bene_ids": sample_ids,
                    },
                )
            ]
        return []

    @staticmethod
    def check_mbsf_d_field_constraints(mbsf_d_df: pl.DataFrame) -> list[Finding]:
        """Identifies MBSF Part D records with negative drug cost or out-of-pocket metrics."""
        if mbsf_d_df.is_empty():
            return []

        invalid = mbsf_d_df.filter(
            (pl.col("bene_ptd_trcc_amt") < 0) | (pl.col("bene_ptd_moop_amt") < 0)
        )
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-008",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} MBSF Part D records violating non-negative cost constraints.",
                    count=invalid_count,
                    details={
                        "table_name": "MBSF Part D",
                        "sample_bene_ids": sample_ids,
                    },
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
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-009",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} MBSF Base records violating 0-12 coverage month constraints.",
                    count=invalid_count,
                    details={
                        "table_name": "MBSF Base Enrollment",
                        "sample_bene_ids": sample_ids,
                    },
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
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-010",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} MBSF Other Chronic records with invalid chronic condition indicators.",
                    count=invalid_count,
                    details={
                        "table_name": "MBSF Other Chronic Conditions",
                        "sample_bene_ids": sample_ids,
                    },
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
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
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
            invalid_expr = (
                invalid_expr
                | (pl.col("payment_count") < 0)
                | (pl.col("payment_count") > 12)
            )

        invalid = mbsf_ra_df.filter(invalid_expr)
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-012",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} MBSF Risk Adjustment records with negative risk scores or invalid payment count.",
                    count=invalid_count,
                    details={
                        "table_name": "MBSF Risk Adjustment",
                        "sample_bene_ids": sample_ids,
                    },
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
            (pl.col("bene_ma_cvrage_tot_mons") < 0)
            | (pl.col("bene_ma_cvrage_tot_mons") > 12)
        )
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-013",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} MBSF Part C records violating 0-12 coverage month constraints.",
                    count=invalid_count,
                    details={
                        "table_name": "MBSF Part C",
                        "sample_bene_ids": sample_ids,
                    },
                )
            ]
        return []

    @staticmethod
    def check_mbsf_ffs_field_constraints(mbsf_ffs_df: pl.DataFrame) -> list[Finding]:
        """Identifies MBSF FFS Utilization records with negative utilization counts."""
        if mbsf_ffs_df.is_empty():
            return []

        cols = [
            "ip_adm_cnt",
            "op_vist_cnt",
            "snf_stay_cnt",
            "car_srvc_cnt",
            "hha_vist_cnt",
            "hosp_stay_cnt",
            "dme_srvc_cnt",
        ]
        present_cols = [c for c in cols if c in mbsf_ffs_df.columns]
        if not present_cols:
            return []

        cond = pl.lit(False)
        for c in present_cols:
            cond = cond | (pl.col(c) < 0)

        invalid = mbsf_ffs_df.filter(cond)
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-014",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} MBSF FFS Utilization records violating non-negative count constraints.",
                    count=invalid_count,
                    details={
                        "table_name": "MBSF FFS Utilization",
                        "sample_bene_ids": sample_ids,
                    },
                )
            ]
        return []

    @staticmethod
    def check_mbsf_pde_util_field_constraints(
        mbsf_pde_util_df: pl.DataFrame,
    ) -> list[Finding]:
        """Identifies MBSF Part D PDE Utilization records with negative fill counts or cost amounts."""
        if mbsf_pde_util_df.is_empty():
            return []

        cols = [
            "pde_tot_fill_cnt",
            "pde_brand_fill_cnt",
            "pde_generic_fill_cnt",
            "pde_tot_cst_amt",
            "pde_ptnt_pay_amt",
            "pde_lis_pay_amt",
        ]
        present_cols = [c for c in cols if c in mbsf_pde_util_df.columns]
        if not present_cols:
            return []

        cond = pl.lit(False)
        for c in present_cols:
            cond = cond | (pl.col(c) < 0)

        invalid = mbsf_pde_util_df.filter(cond)
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-015",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} MBSF Part D PDE Utilization records violating non-negative count/amount constraints.",
                    count=invalid_count,
                    details={
                        "table_name": "MBSF Part D PDE Utilization",
                        "sample_bene_ids": sample_ids,
                    },
                )
            ]
        return []

    @staticmethod
    def check_demographic_code_constraints(bene_df: pl.DataFrame) -> list[Finding]:
        """Identifies Beneficiary records with invalid sex identification or race codes."""
        if bene_df.is_empty():
            return []

        valid_sex = ["0", "1", "2"]
        valid_race = ["0", "1", "2", "3", "4", "5", "6"]

        filter_expr = pl.lit(False)
        if "bene_sex_ident_cd" in bene_df.columns:
            filter_expr = filter_expr | (~pl.col("bene_sex_ident_cd").is_in(valid_sex))
        if "bene_race_cd" in bene_df.columns:
            filter_expr = filter_expr | (~pl.col("bene_race_cd").is_in(valid_race))

        invalid = bene_df.filter(filter_expr)
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="FLD-016",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} beneficiary records with invalid demographic sex or race code format.",
                    count=invalid_count,
                    details={
                        "table_name": "Beneficiary Summary",
                        "sample_bene_ids": sample_ids,
                    },
                )
            ]
        return []

    @staticmethod
    def check_claim_accounting_constraints(
        claim_df: pl.DataFrame, claim_type: str
    ) -> list[Finding]:
        """Identifies claims with negative payment amounts (clm_pmt_amt < 0)."""
        if claim_df.is_empty() or "clm_pmt_amt" not in claim_df.columns:
            return []

        invalid = claim_df.filter(pl.col("clm_pmt_amt") < 0)
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="ACC-001",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} claims in {claim_type} with negative payment amount (clm_pmt_amt < 0).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_charge_accounting_constraints(
        claim_df: pl.DataFrame, claim_type: str
    ) -> list[Finding]:
        """Identifies claims with negative total charges or deductible/coinsurance amounts (< 0)."""
        if claim_df.is_empty():
            return []

        charge_cols = [
            "clm_tot_chrg_amt",
            "nch_bene_ip_ddctbl_amt",
            "nch_bene_ptb_ddctbl_amt",
            "nch_bene_ptb_coinsrnc_amt",
            "nch_bene_blood_ddctbl_amt",
        ]
        present_cols = [c for c in charge_cols if c in claim_df.columns]
        if not present_cols:
            return []

        conditions = [pl.col(c).is_not_null() & (pl.col(c) < 0) for c in present_cols]
        combined_cond = conditions[0]
        for cond in conditions[1:]:
            combined_cond = combined_cond | cond

        invalid = claim_df.filter(combined_cond)
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="ACC-002",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} claims in {claim_type} with negative total charge or deductible/coinsurance amount (< 0).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_mortality_temporal_constraints(
        bene_df: pl.DataFrame, claim_df: pl.DataFrame, claim_type: str
    ) -> list[Finding]:
        """Identifies post-mortem claims where service start date (clm_from_dt) exceeds beneficiary death date."""
        if (
            bene_df.is_empty()
            or claim_df.is_empty()
            or "bene_id" not in bene_df.columns
            or "bene_id" not in claim_df.columns
        ):
            return []

        date_col = None
        for col in ["clm_from_dt", "srvc_dt"]:
            if col in claim_df.columns:
                date_col = col
                break
        if date_col is None:
            return []

        death_col = None
        for col in ["bene_death_dt", "bene_dod"]:
            if col in bene_df.columns:
                death_col = col
                break
        if death_col is None:
            return []

        bene_deceased = bene_df.filter(pl.col(death_col).is_not_null()).select(
            ["bene_id", death_col]
        )
        if bene_deceased.is_empty():
            return []

        joined = claim_df.join(bene_deceased, on="bene_id", how="inner")
        invalid = joined.filter(pl.col(date_col) > pl.col(death_col))
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="TMP-003",
                    category=FindingCategory.TEMPORAL,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} post-mortem claims in {claim_type} with service date exceeding beneficiary death date ({date_col} > {death_col}).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_dob_temporal_constraints(
        bene_df: pl.DataFrame, claim_df: pl.DataFrame, claim_type: str
    ) -> list[Finding]:
        """Identifies claims where service start date (clm_from_dt) precedes beneficiary birth date."""
        if (
            bene_df.is_empty()
            or claim_df.is_empty()
            or "bene_id" not in bene_df.columns
            or "bene_id" not in claim_df.columns
        ):
            return []

        date_col = None
        for col in ["clm_from_dt", "srvc_dt"]:
            if col in claim_df.columns:
                date_col = col
                break
        if date_col is None:
            return []

        dob_col = None
        for col in ["bene_birth_dt", "bene_dob"]:
            if col in bene_df.columns:
                dob_col = col
                break
        if dob_col is None:
            return []

        bene_dob_df = bene_df.filter(pl.col(dob_col).is_not_null()).select(
            ["bene_id", dob_col]
        )
        if bene_dob_df.is_empty():
            return []

        joined = claim_df.join(bene_dob_df, on="bene_id", how="inner")
        invalid = joined.filter(pl.col(date_col) < pl.col(dob_col))
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="TMP-004",
                    category=FindingCategory.TEMPORAL,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} claims in {claim_type} with service date preceding beneficiary birth date ({date_col} < {dob_col}).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_enrollment_consistency_constraints(
        mbsf_base_df: pl.DataFrame,
    ) -> list[Finding]:
        """Identifies MBSF Base records violating beneficiary entitlement or coverage month consistency."""
        if mbsf_base_df.is_empty():
            return []

        invalid_conditions = []
        for col in [
            "bene_hi_cvrage_tot_mons",
            "bene_smi_cvrage_tot_mons",
            "bene_hmo_cvrage_tot_mons",
            "bene_ptd_cvrage_tot_mons",
        ]:
            if col in mbsf_base_df.columns:
                invalid_conditions.append((pl.col(col) < 0) | (pl.col(col) > 12))

        if not invalid_conditions:
            return []

        combined_condition = invalid_conditions[0]
        for cond in invalid_conditions[1:]:
            combined_condition = combined_condition | cond

        invalid = mbsf_base_df.filter(combined_condition)
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="ENR-001",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} MBSF Base records violating 0-12 coverage month consistency constraints.",
                    count=invalid_count,
                    details={
                        "table_name": "MBSF Base Enrollment",
                        "sample_bene_ids": sample_ids,
                    },
                )
            ]
        return []

    @staticmethod
    def check_provider_npi_constraints(
        claim_df: pl.DataFrame, claim_type: str
    ) -> list[Finding]:
        """Identifies claims with invalid National Provider Identifier (NPI) format (not 10 numeric digits when present)."""
        if claim_df.is_empty():
            return []

        npi_col = None
        for col in ["prvdr_npi", "npi", "nch_prvdr_npi_num"]:
            if col in claim_df.columns:
                npi_col = col
                break
        if npi_col is None:
            return []

        non_null_npi = claim_df.filter(pl.col(npi_col).is_not_null())
        if non_null_npi.is_empty():
            return []

        invalid = non_null_npi.filter(
            ~pl.col(npi_col).str.contains(r"^\d{10}$")
        )
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="NPI-001",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} claims in {claim_type} with invalid NPI format (must be 10 numeric digits).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_icd_code_constraints(
        claim_df: pl.DataFrame, claim_type: str
    ) -> list[Finding]:
        """Identifies claims with invalid ICD diagnosis code format (must be 3 to 7 alphanumeric characters when present)."""
        if claim_df.is_empty():
            return []

        icd_col = None
        for col in ["icd_dgns_cd1", "icd_dgns_cd_1", "icd9_dgns_cd_1"]:
            if col in claim_df.columns:
                icd_col = col
                break
        if icd_col is None:
            return []

        non_null_icd = claim_df.filter(pl.col(icd_col).is_not_null())
        if non_null_icd.is_empty():
            return []

        invalid = non_null_icd.filter(
            ~pl.col(icd_col).str.contains(r"^[A-Za-z0-9]{3,7}$")
        )
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="ICD-001",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} claims in {claim_type} with invalid ICD diagnosis code format (must be 3-7 alphanumeric characters).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_hcpcs_code_constraints(
        claim_df: pl.DataFrame, claim_type: str
    ) -> list[Finding]:
        """Identifies claims with invalid HCPCS procedure code format (must be 5 alphanumeric characters when present)."""
        if claim_df.is_empty():
            return []

        hcpcs_col = None
        for col in ["hcpcs_cd", "hcpcs_cd_1", "line_hcpcs_cd"]:
            if col in claim_df.columns:
                hcpcs_col = col
                break
        if hcpcs_col is None:
            return []

        non_null_hcpcs = claim_df.filter(pl.col(hcpcs_col).is_not_null())
        if non_null_hcpcs.is_empty():
            return []

        invalid = non_null_hcpcs.filter(
            ~pl.col(hcpcs_col).str.contains(r"^[A-Za-z0-9]{5}$")
        )
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="HCPCS-001",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} claims in {claim_type} with invalid HCPCS procedure code format (must be 5 alphanumeric characters).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_ndc_code_constraints(
        pde_df: pl.DataFrame, dataset_name: str = "Prescription Drug Events"
    ) -> list[Finding]:
        """Identifies PDE records with invalid National Drug Code (NDC) format (must be 11 alphanumeric characters when present)."""
        if pde_df.is_empty():
            return []

        ndc_col = None
        for col in ["prod_srvc_id", "PROD_SRVC_ID", "ndc_cd"]:
            if col in pde_df.columns:
                ndc_col = col
                break
        if ndc_col is None:
            return []

        non_null_ndc = pde_df.filter(pl.col(ndc_col).is_not_null())
        if non_null_ndc.is_empty():
            return []

        invalid = non_null_ndc.filter(
            ~pl.col(ndc_col).str.contains(r"^[A-Za-z0-9]{11}$")
        )
        invalid_count = invalid.height

        if invalid_count > 0:
            sample_ids = (
                invalid.select("pde_id").slice(0, 5).to_series().to_list()
                if "pde_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="NDC-001",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} records in {dataset_name} with invalid NDC format (must be 11 alphanumeric characters).",
                    count=invalid_count,
                    details={"dataset_name": dataset_name, "sample_pde_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_drg_code_constraints(
        claim_df: pl.DataFrame, claim_type: str = "Inpatient Claims"
    ) -> list[Finding]:
        """Identifies claims with invalid Diagnosis Related Group (DRG) code format (must be 3 alphanumeric characters when present)."""
        if claim_df.is_empty():
            return []

        drg_col = None
        for col in ["clm_drg_cd", "CLM_DRG_CD", "drg_cd", "DRG_CD"]:
            if col in claim_df.columns:
                drg_col = col
                break
        if drg_col is None:
            return []

        non_null_drg = claim_df.filter(pl.col(drg_col).is_not_null())
        if non_null_drg.is_empty():
            return []

        invalid = non_null_drg.filter(
            ~pl.col(drg_col).cast(pl.Utf8).str.contains(r"^[0-9A-Za-z]{3}$")
        )
        invalid_count = len(invalid)

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="DRG-001",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} claims in {claim_type} with invalid DRG code format (must be 3 alphanumeric characters).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_taxonomy_code_constraints(
        claim_df: pl.DataFrame, claim_type: str = "Claim Records"
    ) -> list[Finding]:
        """Identifies claims with invalid Healthcare Provider Taxonomy Code format (must be 10 alphanumeric characters when present)."""
        if claim_df.is_empty():
            return []

        tax_col = None
        for col in [
            "prvdr_taxonomy_cd",
            "PRVDR_TAXONOMY_CD",
            "tax_cd",
            "TAX_CD",
            "taxonomy_cd",
            "TAXONOMY_CD",
            "provider_taxonomy_code",
            "PROVIDER_TAXONOMY_CODE",
        ]:
            if col in claim_df.columns:
                tax_col = col
                break
        if tax_col is None:
            return []

        non_null_tax = claim_df.filter(pl.col(tax_col).is_not_null())
        if non_null_tax.is_empty():
            return []

        invalid = non_null_tax.filter(
            ~pl.col(tax_col).cast(pl.Utf8).str.contains(r"^[0-9A-Za-z]{10}$")
        )
        invalid_count = len(invalid)

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="TAX-001",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} records in {claim_type} with invalid Healthcare Provider Taxonomy Code format (must be 10 alphanumeric characters).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_pos_code_constraints(
        claim_df: pl.DataFrame, claim_type: str = "Claim Records"
    ) -> list[Finding]:
        """Identifies claims with invalid Place of Service (POS) code format (must be 2 numeric digits when present)."""
        if claim_df.is_empty():
            return []

        pos_col = None
        for col in [
            "place_of_service_cd",
            "PLACE_OF_SERVICE_CD",
            "line_place_of_service_cd",
            "LINE_PLACE_OF_SERVICE_CD",
            "pos_cd",
            "POS_CD",
            "clm_pos_cd",
            "CLM_POS_CD",
        ]:
            if col in claim_df.columns:
                pos_col = col
                break
        if pos_col is None:
            return []

        non_null_pos = claim_df.filter(pl.col(pos_col).is_not_null())
        if non_null_pos.is_empty():
            return []

        invalid = non_null_pos.filter(
            ~pl.col(pos_col).cast(pl.Utf8).str.contains(r"^[0-9]{2}$")
        )
        invalid_count = len(invalid)

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="POS-001",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} records in {claim_type} with invalid Place of Service (POS) code format (must be 2 numeric digits).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_rev_center_code_constraints(
        claim_df: pl.DataFrame, claim_type: str = "Claim Records"
    ) -> list[Finding]:
        """Identifies claims with invalid Revenue Center (REV_CNTR) code format (must be 4 numeric digits when present)."""
        if claim_df.is_empty():
            return []

        rev_col = None
        for col in [
            "rev_cntr",
            "REV_CNTR",
            "rev_cntr_cd",
            "REV_CNTR_CD",
            "clm_rev_cntr_cd",
            "CLM_REV_CNTR_CD",
            "line_rev_cntr_cd",
            "LINE_REV_CNTR_CD",
        ]:
            if col in claim_df.columns:
                rev_col = col
                break
        if rev_col is None:
            return []

        non_null_rev = claim_df.filter(pl.col(rev_col).is_not_null())
        if non_null_rev.is_empty():
            return []

        invalid = non_null_rev.filter(
            ~pl.col(rev_col).cast(pl.Utf8).str.contains(r"^[0-9]{4}$")
        )
        invalid_count = len(invalid)

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="REV-001",
                    category=FindingCategory.ADMINISTRATIVE,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} records in {claim_type} with invalid Revenue Center Code format (must be 4 numeric digits).",
                    count=invalid_count,
                    details={"claim_type": claim_type, "sample_clm_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_zip_code_constraints(
        df: pl.DataFrame, table_type: str = "Dataset Records"
    ) -> list[Finding]:
        """Identifies records with invalid Zip Code format (must be 5 or 9 numeric digits, or 5+4 with hyphen)."""
        if df.is_empty():
            return []

        zip_col = None
        for col in [
            "bene_zip_cd",
            "BENE_ZIP_CD",
            "zip_cd",
            "ZIP_CD",
            "clm_zip_cd",
            "CLM_ZIP_CD",
            "bene_zip",
            "BENE_ZIP",
        ]:
            if col in df.columns:
                zip_col = col
                break
        if zip_col is None:
            return []

        non_null_zip = df.filter(pl.col(zip_col).is_not_null())
        if non_null_zip.is_empty():
            return []

        invalid = non_null_zip.filter(
            ~pl.col(zip_col).cast(pl.Utf8).str.contains(r"^([0-9]{5}|[0-9]{9}|[0-9]{5}-[0-9]{4})$")
        )
        invalid_count = len(invalid)

        if invalid_count > 0:
            sample_ids = (
                invalid.select("bene_id").slice(0, 5).to_series().to_list()
                if "bene_id" in invalid.columns
                else (
                    invalid.select("clm_id").slice(0, 5).to_series().to_list()
                    if "clm_id" in invalid.columns
                    else []
                )
            )
            return [
                Finding(
                    rule_id="ZIP-001",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} records in {table_type} with invalid Zip Code format (must be 5 or 9 numeric digits).",
                    count=invalid_count,
                    details={"table_type": table_type, "sample_ids": sample_ids},
                )
            ]
        return []

    @staticmethod
    def check_claim_line_item_constraints(
        df: pl.DataFrame, table_type: str
    ) -> list[Finding]:
        """Identifies claim line items with invalid line number or line item count (< 1)."""
        if df.is_empty():
            return []

        line_col = None
        for candidate in ["line_num", "dme_line_item_count", "line_srvc_cnt"]:
            if candidate in df.columns:
                line_col = candidate
                break

        if line_col is None:
            return []

        invalid = df.filter(pl.col(line_col).is_not_null() & (pl.col(line_col) < 1))
        invalid_count = len(invalid)

        if invalid_count > 0:
            sample_ids = (
                invalid.select("clm_id").slice(0, 5).to_series().to_list()
                if "clm_id" in invalid.columns
                else []
            )
            return [
                Finding(
                    rule_id="LINE-001",
                    category=FindingCategory.FIELD,
                    severity=Severity.HIGH,
                    message=f"Found {invalid_count} records in {table_type} with invalid line item count or number (< 1).",
                    count=invalid_count,
                    details={"table_type": table_type, "sample_clm_ids": sample_ids},
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
        mbsf_ffs_df: Optional[pl.DataFrame] = None,
        mbsf_pde_util_df: Optional[pl.DataFrame] = None,
    ) -> ValidationReport:
        """Executes full suite of relational, temporal, field, and record-level checks over a dataset slice."""
        findings: list[Finding] = []

        # Record uniqueness
        findings.extend(
            self.check_record_uniqueness(bene_df, ["bene_id"], "Beneficiary Summary")
        )
        findings.extend(self.check_demographic_code_constraints(bene_df))
        findings.extend(self.check_zip_code_constraints(bene_df, "Beneficiary Summary"))

        if carrier_df is not None and not carrier_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, carrier_df, "Carrier Claims")
            )
            findings.extend(
                self.check_temporal_inversions(carrier_df, "Carrier Claims")
            )
            findings.extend(
                self.check_mortality_temporal_constraints(
                    bene_df, carrier_df, "Carrier Claims"
                )
            )
            findings.extend(
                self.check_dob_temporal_constraints(
                    bene_df, carrier_df, "Carrier Claims"
                )
            )
            findings.extend(
                self.check_claim_accounting_constraints(carrier_df, "Carrier Claims")
            )
            findings.extend(
                self.check_charge_accounting_constraints(carrier_df, "Carrier Claims")
            )
            findings.extend(
                self.check_provider_npi_constraints(carrier_df, "Carrier Claims")
            )
            findings.extend(
                self.check_icd_code_constraints(carrier_df, "Carrier Claims")
            )
            findings.extend(
                self.check_hcpcs_code_constraints(carrier_df, "Carrier Claims")
            )
            findings.extend(
                self.check_taxonomy_code_constraints(carrier_df, "Carrier Claims")
            )
            findings.extend(
                self.check_pos_code_constraints(carrier_df, "Carrier Claims")
            )
            findings.extend(
                self.check_claim_line_item_constraints(carrier_df, "Carrier Claims")
            )
            if "line_num" in carrier_df.columns:
                findings.extend(
                    self.check_record_uniqueness(
                        carrier_df, ["clm_id", "line_num"], "Carrier Claims"
                    )
                )

        if outpatient_df is not None and not outpatient_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, outpatient_df, "Outpatient Claims")
            )
            findings.extend(
                self.check_temporal_inversions(outpatient_df, "Outpatient Claims")
            )
            findings.extend(
                self.check_mortality_temporal_constraints(
                    bene_df, outpatient_df, "Outpatient Claims"
                )
            )
            findings.extend(
                self.check_dob_temporal_constraints(
                    bene_df, outpatient_df, "Outpatient Claims"
                )
            )
            findings.extend(
                self.check_claim_accounting_constraints(
                    outpatient_df, "Outpatient Claims"
                )
            )
            findings.extend(
                self.check_charge_accounting_constraints(
                    outpatient_df, "Outpatient Claims"
                )
            )
            findings.extend(
                self.check_provider_npi_constraints(
                    outpatient_df, "Outpatient Claims"
                )
            )
            findings.extend(
                self.check_icd_code_constraints(
                    outpatient_df, "Outpatient Claims"
                )
            )
            findings.extend(
                self.check_hcpcs_code_constraints(
                    outpatient_df, "Outpatient Claims"
                )
            )
            findings.extend(
                self.check_taxonomy_code_constraints(
                    outpatient_df, "Outpatient Claims"
                )
            )
            findings.extend(
                self.check_pos_code_constraints(
                    outpatient_df, "Outpatient Claims"
                )
            )
            findings.extend(
                self.check_rev_center_code_constraints(
                    outpatient_df, "Outpatient Claims"
                )
            )
            findings.extend(
                self.check_record_uniqueness(
                    outpatient_df, ["clm_id"], "Outpatient Claims"
                )
            )

        if inpatient_df is not None and not inpatient_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, inpatient_df, "Inpatient Claims")
            )
            findings.extend(
                self.check_admission_temporal_inversions(
                    inpatient_df, "Inpatient Claims"
                )
            )
            findings.extend(
                self.check_mortality_temporal_constraints(
                    bene_df, inpatient_df, "Inpatient Claims"
                )
            )
            findings.extend(
                self.check_dob_temporal_constraints(
                    bene_df, inpatient_df, "Inpatient Claims"
                )
            )
            findings.extend(
                self.check_claim_accounting_constraints(
                    inpatient_df, "Inpatient Claims"
                )
            )
            findings.extend(
                self.check_charge_accounting_constraints(
                    inpatient_df, "Inpatient Claims"
                )
            )
            findings.extend(
                self.check_record_uniqueness(
                    inpatient_df, ["clm_id"], "Inpatient Claims"
                )
            )
            findings.extend(
                self.check_drg_code_constraints(inpatient_df, "Inpatient Claims")
            )
            findings.extend(self.check_inpatient_field_constraints(inpatient_df))

        if pde_df is not None and not pde_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, pde_df, "Prescription Drug Events")
            )
            findings.extend(
                self.check_mortality_temporal_constraints(
                    bene_df, pde_df, "Prescription Drug Events"
                )
            )
            findings.extend(
                self.check_dob_temporal_constraints(
                    bene_df, pde_df, "Prescription Drug Events"
                )
            )
            findings.extend(self.check_pde_field_constraints(pde_df))
            findings.extend(self.check_ndc_code_constraints(pde_df))
            findings.extend(
                self.check_claim_accounting_constraints(
                    pde_df, "Prescription Drug Events"
                )
            )
            findings.extend(
                self.check_record_uniqueness(
                    pde_df, ["pde_id"], "Prescription Drug Events"
                )
            )

        if snf_df is not None and not snf_df.is_empty():
            findings.extend(self.check_orphaned_claims(bene_df, snf_df, "SNF Claims"))
            findings.extend(
                self.check_admission_temporal_inversions(snf_df, "SNF Claims")
            )
            findings.extend(
                self.check_mortality_temporal_constraints(bene_df, snf_df, "SNF Claims")
            )
            findings.extend(
                self.check_dob_temporal_constraints(bene_df, snf_df, "SNF Claims")
            )
            findings.extend(self.check_snf_field_constraints(snf_df))
            findings.extend(
                self.check_claim_accounting_constraints(snf_df, "SNF Claims")
            )
            findings.extend(
                self.check_charge_accounting_constraints(snf_df, "SNF Claims")
            )
            findings.extend(
                self.check_record_uniqueness(snf_df, ["clm_id"], "SNF Claims")
            )

        if hha_df is not None and not hha_df.is_empty():
            findings.extend(self.check_orphaned_claims(bene_df, hha_df, "HHA Claims"))
            findings.extend(
                self.check_admission_temporal_inversions(hha_df, "HHA Claims")
            )
            findings.extend(
                self.check_mortality_temporal_constraints(bene_df, hha_df, "HHA Claims")
            )
            findings.extend(
                self.check_dob_temporal_constraints(bene_df, hha_df, "HHA Claims")
            )
            findings.extend(self.check_hha_field_constraints(hha_df))
            findings.extend(
                self.check_claim_accounting_constraints(hha_df, "HHA Claims")
            )
            findings.extend(
                self.check_charge_accounting_constraints(hha_df, "HHA Claims")
            )
            findings.extend(
                self.check_record_uniqueness(hha_df, ["clm_id"], "HHA Claims")
            )

        if dme_df is not None and not dme_df.is_empty():
            findings.extend(self.check_orphaned_claims(bene_df, dme_df, "DME Claims"))
            findings.extend(self.check_temporal_inversions(dme_df, "DME Claims"))
            findings.extend(
                self.check_mortality_temporal_constraints(bene_df, dme_df, "DME Claims")
            )
            findings.extend(
                self.check_dob_temporal_constraints(bene_df, dme_df, "DME Claims")
            )
            findings.extend(self.check_dme_field_constraints(dme_df))
            findings.extend(
                self.check_claim_line_item_constraints(dme_df, "DME Claims")
            )
            findings.extend(
                self.check_claim_accounting_constraints(dme_df, "DME Claims")
            )
            findings.extend(
                self.check_charge_accounting_constraints(dme_df, "DME Claims")
            )
            if "line_num" in dme_df.columns:
                findings.extend(
                    self.check_record_uniqueness(
                        dme_df, ["clm_id", "line_num"], "DME Claims"
                    )
                )

        if hospice_df is not None and not hospice_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, hospice_df, "Hospice Claims")
            )
            findings.extend(
                self.check_admission_temporal_inversions(hospice_df, "Hospice Claims")
            )
            findings.extend(
                self.check_mortality_temporal_constraints(
                    bene_df, hospice_df, "Hospice Claims"
                )
            )
            findings.extend(
                self.check_dob_temporal_constraints(
                    bene_df, hospice_df, "Hospice Claims"
                )
            )
            findings.extend(self.check_hospice_field_constraints(hospice_df))
            findings.extend(
                self.check_claim_accounting_constraints(hospice_df, "Hospice Claims")
            )
            findings.extend(
                self.check_charge_accounting_constraints(hospice_df, "Hospice Claims")
            )
            findings.extend(
                self.check_record_uniqueness(hospice_df, ["clm_id"], "Hospice Claims")
            )

        if mbsf_cc_df is not None and not mbsf_cc_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(
                    bene_df, mbsf_cc_df, "MBSF Chronic Conditions"
                )
            )
            findings.extend(self.check_mbsf_cc_field_constraints(mbsf_cc_df))
            findings.extend(
                self.check_record_uniqueness(
                    mbsf_cc_df, ["bene_id"], "MBSF Chronic Conditions"
                )
            )

        if mbsf_cu_df is not None and not mbsf_cu_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, mbsf_cu_df, "MBSF Cost & Use")
            )
            findings.extend(self.check_mbsf_cu_field_constraints(mbsf_cu_df))
            findings.extend(
                self.check_record_uniqueness(mbsf_cu_df, ["bene_id"], "MBSF Cost & Use")
            )

        if mbsf_d_df is not None and not mbsf_d_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, mbsf_d_df, "MBSF Part D")
            )
            findings.extend(self.check_mbsf_d_field_constraints(mbsf_d_df))
            findings.extend(
                self.check_record_uniqueness(mbsf_d_df, ["bene_id"], "MBSF Part D")
            )

        if mbsf_base_df is not None and not mbsf_base_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(
                    bene_df, mbsf_base_df, "MBSF Base Enrollment"
                )
            )
            findings.extend(self.check_mbsf_base_field_constraints(mbsf_base_df))
            findings.extend(self.check_enrollment_consistency_constraints(mbsf_base_df))
            findings.extend(
                self.check_record_uniqueness(
                    mbsf_base_df, ["bene_id"], "MBSF Base Enrollment"
                )
            )

        if mbsf_oc_df is not None and not mbsf_oc_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(
                    bene_df, mbsf_oc_df, "MBSF Other Chronic Conditions"
                )
            )
            findings.extend(self.check_mbsf_oc_field_constraints(mbsf_oc_df))
            findings.extend(
                self.check_record_uniqueness(
                    mbsf_oc_df, ["bene_id"], "MBSF Other Chronic Conditions"
                )
            )

        if mbsf_ndi_df is not None and not mbsf_ndi_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, mbsf_ndi_df, "MBSF NDI")
            )
            findings.extend(self.check_mbsf_ndi_field_constraints(mbsf_ndi_df))
            findings.extend(
                self.check_record_uniqueness(mbsf_ndi_df, ["bene_id"], "MBSF NDI")
            )

        if mbsf_ra_df is not None and not mbsf_ra_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, mbsf_ra_df, "MBSF Risk Adjustment")
            )
            findings.extend(self.check_mbsf_ra_field_constraints(mbsf_ra_df))
            findings.extend(
                self.check_record_uniqueness(
                    mbsf_ra_df, ["bene_id"], "MBSF Risk Adjustment"
                )
            )

        if mbsf_c_df is not None and not mbsf_c_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, mbsf_c_df, "MBSF Part C")
            )
            findings.extend(self.check_mbsf_c_field_constraints(mbsf_c_df))
            findings.extend(
                self.check_record_uniqueness(mbsf_c_df, ["bene_id"], "MBSF Part C")
            )

        if mbsf_ffs_df is not None and not mbsf_ffs_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(bene_df, mbsf_ffs_df, "MBSF FFS Utilization")
            )
            findings.extend(self.check_mbsf_ffs_field_constraints(mbsf_ffs_df))
            findings.extend(
                self.check_record_uniqueness(
                    mbsf_ffs_df, ["bene_id"], "MBSF FFS Utilization"
                )
            )

        if mbsf_pde_util_df is not None and not mbsf_pde_util_df.is_empty():
            findings.extend(
                self.check_orphaned_claims(
                    bene_df, mbsf_pde_util_df, "MBSF Part D PDE Utilization"
                )
            )
            findings.extend(
                self.check_mbsf_pde_util_field_constraints(mbsf_pde_util_df)
            )
            findings.extend(
                self.check_record_uniqueness(
                    mbsf_pde_util_df, ["bene_id"], "MBSF Part D PDE Utilization"
                )
            )

        return ValidationReport(findings=findings)
