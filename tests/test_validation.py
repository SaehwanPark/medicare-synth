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
