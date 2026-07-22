"""Unit tests for relational, temporal, and record validation routines."""

from datetime import date
import polars as pl

from medicare_synth.validation import FindingCategory, RelationalValidator, Severity


def test_relational_validator_valid_slice() -> None:
    bene_df = pl.DataFrame(
        {
            "bene_id": ["BENE001", "BENE002"],
            "bene_birth_dt": [date(1950, 1, 1), date(1945, 5, 12)],
        }
    )

    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002"],
            "line_num": [1, 1],
            "bene_id": ["BENE001", "BENE002"],
            "clm_from_dt": [date(2021, 3, 1), date(2021, 4, 10)],
            "clm_thru_dt": [date(2021, 3, 5), date(2021, 4, 15)],
        }
    )

    outpatient_df = pl.DataFrame(
        {
            "clm_id": ["OPT001"],
            "bene_id": ["BENE001"],
            "clm_from_dt": [date(2021, 6, 1)],
            "clm_thru_dt": [date(2021, 6, 1)],
        }
    )

    validator = RelationalValidator()
    report = validator.validate_slice(bene_df, carrier_df, outpatient_df)

    assert report.is_valid is True
    assert len(report.findings) == 0


def test_relational_validator_orphaned_claim_scenario() -> None:
    bene_df = pl.DataFrame(
        {
            "bene_id": ["BENE001"],
        }
    )

    # Carrier claim references non-existent BENE999 (invalid_orphaned_claim scenario)
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM999"],
            "line_num": [1],
            "bene_id": ["BENE999"],
            "clm_from_dt": [date(2021, 1, 1)],
            "clm_thru_dt": [date(2021, 1, 2)],
        }
    )

    validator = RelationalValidator()
    report = validator.validate_slice(bene_df, carrier_df)

    assert report.is_valid is False
    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.rule_id == "REL-001"
    assert finding.category == FindingCategory.RELATIONAL
    assert finding.severity == Severity.CRITICAL
    assert finding.count == 1


def test_relational_validator_temporal_inversion_scenario() -> None:
    bene_df = pl.DataFrame(
        {
            "bene_id": ["BENE001"],
        }
    )

    # Outpatient claim has clm_from_dt > clm_thru_dt (invalid_temporal_inversion scenario)
    outpatient_df = pl.DataFrame(
        {
            "clm_id": ["OPT888"],
            "bene_id": ["BENE001"],
            "clm_from_dt": [date(2021, 5, 20)],
            "clm_thru_dt": [date(2021, 5, 10)],
        }
    )

    validator = RelationalValidator()
    report = validator.validate_slice(bene_df, outpatient_df=outpatient_df)

    assert report.is_valid is False
    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.rule_id == "TMP-001"
    assert finding.category == FindingCategory.TEMPORAL
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_relational_validator_record_uniqueness() -> None:
    bene_df = pl.DataFrame(
        {
            "bene_id": ["BENE001", "BENE001"],  # Duplicate key
        }
    )

    validator = RelationalValidator()
    report = validator.validate_slice(bene_df)

    assert report.is_valid is False
    assert any(f.rule_id == "REC-001" for f in report.findings)


def test_check_claim_accounting_constraints() -> None:
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002"],
            "clm_pmt_amt": [150.0, -10.0],
        }
    )
    findings = RelationalValidator.check_claim_accounting_constraints(
        carrier_df, "Carrier Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "ACC-001"
    assert finding.category == FindingCategory.ADMINISTRATIVE
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_mortality_temporal_constraints() -> None:
    bene_df = pl.DataFrame(
        {
            "bene_id": ["BENE001", "BENE002"],
            "bene_death_dt": [date(2021, 6, 1), None],
        }
    )
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002"],
            "bene_id": ["BENE001", "BENE002"],
            "clm_from_dt": [date(2021, 7, 1), date(2021, 8, 1)],
        }
    )
    findings = RelationalValidator.check_mortality_temporal_constraints(
        bene_df, carrier_df, "Carrier Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "TMP-003"
    assert finding.category == FindingCategory.TEMPORAL
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_enrollment_consistency_constraints() -> None:
    mbsf_base_df = pl.DataFrame(
        {
            "bene_id": ["BENE001", "BENE002"],
            "bene_hi_cvrage_tot_mons": [12, 14],  # 14 violates 0..12 bounds
            "bene_smi_cvrage_tot_mons": [12, 12],
            "bene_hmo_cvrage_tot_mons": [0, 0],
            "bene_ptd_cvrage_tot_mons": [12, 12],
        }
    )
    findings = RelationalValidator.check_enrollment_consistency_constraints(
        mbsf_base_df
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "ENR-001"
    assert finding.category == FindingCategory.ADMINISTRATIVE
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_dob_temporal_constraints() -> None:
    bene_df = pl.DataFrame(
        {
            "bene_id": ["BENE001", "BENE002"],
            "bene_birth_dt": [date(1950, 1, 1), date(1960, 5, 10)],
        }
    )
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002"],
            "bene_id": ["BENE001", "BENE002"],
            "clm_from_dt": [date(1949, 12, 31), date(2021, 8, 1)],  # 1949 violates DOB
        }
    )
    findings = RelationalValidator.check_dob_temporal_constraints(
        bene_df, carrier_df, "Carrier Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "TMP-004"
    assert finding.category == FindingCategory.TEMPORAL
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_provider_npi_constraints() -> None:
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002", "CLM003"],
            "bene_id": ["BENE001", "BENE002", "BENE003"],
            "prvdr_npi": ["1234567890", "INVALID_NPI", None],
        }
    )
    findings = RelationalValidator.check_provider_npi_constraints(
        carrier_df, "Carrier Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "NPI-001"
    assert finding.category == FindingCategory.ADMINISTRATIVE
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_icd_code_constraints() -> None:
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002", "CLM003"],
            "bene_id": ["BENE001", "BENE002", "BENE003"],
            "icd_dgns_cd1": ["I10", "INVALID_ICD_TOO_LONG", None],
        }
    )
    findings = RelationalValidator.check_icd_code_constraints(
        carrier_df, "Carrier Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "ICD-001"
    assert finding.category == FindingCategory.ADMINISTRATIVE
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_hcpcs_code_constraints() -> None:
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002", "CLM003"],
            "bene_id": ["BENE001", "BENE002", "BENE003"],
            "hcpcs_cd": ["99213", "INVALID_HCPCS_TOO_LONG", None],
        }
    )
    findings = RelationalValidator.check_hcpcs_code_constraints(
        carrier_df, "Carrier Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "HCPCS-001"
    assert finding.category == FindingCategory.ADMINISTRATIVE
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_ndc_code_constraints() -> None:
    pde_df = pl.DataFrame(
        {
            "pde_id": ["PDE001", "PDE002", "PDE003"],
            "bene_id": ["BENE001", "BENE002", "BENE003"],
            "prod_srvc_id": ["00002322930", "INVALID_NDC_TOO_LONG", None],
        }
    )
    findings = RelationalValidator.check_ndc_code_constraints(
        pde_df, "Prescription Drug Events"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "NDC-001"
    assert finding.category == FindingCategory.ADMINISTRATIVE
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_drg_code_constraints() -> None:
    inpatient_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002", "CLM003"],
            "bene_id": ["BENE001", "BENE002", "BENE003"],
            "clm_drg_cd": ["001", "INVALID_DRG_TOO_LONG", None],
        }
    )
    findings = RelationalValidator.check_drg_code_constraints(
        inpatient_df, "Inpatient Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "DRG-001"
    assert finding.category == FindingCategory.ADMINISTRATIVE
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_taxonomy_code_constraints() -> None:
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002", "CLM003"],
            "bene_id": ["BENE001", "BENE002", "BENE003"],
            "prvdr_taxonomy_cd": ["207Q00000X", "INVALID_TAXONOMY_CODE", None],
        }
    )
    findings = RelationalValidator.check_taxonomy_code_constraints(
        carrier_df, "Carrier Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "TAX-001"
    assert finding.category == FindingCategory.ADMINISTRATIVE
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_pos_code_constraints() -> None:
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002", "CLM003"],
            "bene_id": ["BENE001", "BENE002", "BENE003"],
            "place_of_service_cd": ["11", "999_INVALID", None],
        }
    )
    findings = RelationalValidator.check_pos_code_constraints(
        carrier_df, "Carrier Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "POS-001"
    assert finding.category == FindingCategory.ADMINISTRATIVE
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_rev_center_code_constraints() -> None:
    outpatient_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002", "CLM003"],
            "bene_id": ["BENE001", "BENE002", "BENE003"],
            "rev_cntr": ["0300", "INVALID_REV_CNTR", None],
        }
    )
    findings = RelationalValidator.check_rev_center_code_constraints(
        outpatient_df, "Outpatient Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "REV-001"
    assert finding.category == FindingCategory.ADMINISTRATIVE
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_demographic_code_constraints() -> None:
    bene_df = pl.DataFrame(
        {
            "bene_id": ["BENE001", "BENE002", "BENE003"],
            "bene_sex_ident_cd": ["1", "9", "2"],  # "9" is invalid
            "bene_race_cd": ["1", "2", "X"],  # "X" is invalid
        }
    )
    findings = RelationalValidator.check_demographic_code_constraints(bene_df)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "FLD-016"
    assert finding.category == FindingCategory.FIELD
    assert finding.severity == Severity.HIGH
    assert finding.count == 2


def test_check_inpatient_field_constraints() -> None:
    inpatient_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002", "CLM003"],
            "bene_id": ["BENE001", "BENE002", "BENE003"],
            "clm_utlztn_day_cnt": [5, -1, 3],  # -1 is invalid
            "ncvd_days_cnt": [0, 0, -2],  # -2 is invalid
        }
    )
    findings = RelationalValidator.check_inpatient_field_constraints(inpatient_df)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "FLD-006"
    assert finding.category == FindingCategory.FIELD
    assert finding.severity == Severity.HIGH
    assert finding.count == 2


def test_check_carrier_field_constraints() -> None:
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002"],
            "line_num": [0, 1],  # 0 is invalid
            "clm_from_dt": [date(2021, 5, 10), date(2021, 5, 20)],
            "clm_thru_dt": [date(2021, 5, 5), date(2021, 5, 25)],  # first row date inversion
        }
    )
    findings = RelationalValidator.check_carrier_field_constraints(carrier_df)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "FLD-007"
    assert finding.category == FindingCategory.FIELD
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_outpatient_field_constraints() -> None:
    outpatient_df = pl.DataFrame(
        {
            "clm_id": ["OPT001", "OPT002"],
            "clm_pmt_amt": [-50.0, 100.0],  # -50.0 is invalid
            "clm_from_dt": [date(2021, 6, 1), date(2021, 6, 15)],
            "clm_thru_dt": [date(2021, 6, 5), date(2021, 6, 10)],  # second row date inversion
        }
    )
    findings = RelationalValidator.check_outpatient_field_constraints(outpatient_df)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "FLD-008"
    assert finding.category == FindingCategory.FIELD
    assert finding.severity == Severity.HIGH
    assert finding.count == 2


def test_check_zip_code_constraints() -> None:
    bene_df = pl.DataFrame(
        {
            "bene_id": ["BENE001", "BENE002", "BENE003", "BENE004"],
            "bene_zip_cd": ["12345", "123456789", "12345-6789", "INVALID_ZIP"],
        }
    )
    findings = RelationalValidator.check_zip_code_constraints(
        bene_df, "Beneficiary Summary"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "ZIP-001"
    assert finding.category == FindingCategory.FIELD
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


def test_check_claim_line_item_constraints() -> None:
    carrier_df = pl.DataFrame(
        {
            "clm_id": ["CLM001", "CLM002", "CLM003"],
            "line_num": [1, 0, 2],  # 0 is invalid
        }
    )
    findings = RelationalValidator.check_claim_line_item_constraints(
        carrier_df, "Carrier Claims"
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "LINE-001"
    assert finding.category == FindingCategory.FIELD
    assert finding.severity == Severity.HIGH
    assert finding.count == 1


