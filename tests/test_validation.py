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
