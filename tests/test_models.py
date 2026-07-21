"""Tests for domain entity record Pydantic models."""

from datetime import date
import pytest
from pydantic import ValidationError

from medicare_synth.models import (
    BeneficiaryRecord,
    CarrierClaimLineRecord,
    OutpatientClaimHeaderRecord,
)


def test_beneficiary_record_valid() -> None:
    record = BeneficiaryRecord(
        bene_id="BENE_1001",
        bene_birth_dt=date(1950, 5, 12),
        bene_sex_ident_cd="1",
        bene_race_cd="1",
    )
    assert record.bene_id == "BENE_1001"
    assert record.bene_death_dt is None


def test_carrier_claim_line_record_valid() -> None:
    record = CarrierClaimLineRecord(
        clm_id="CLM_2001",
        line_num=1,
        bene_id="BENE_1001",
        clm_from_dt=date(2021, 3, 1),
        clm_thru_dt=date(2021, 3, 1),
        prvdr_npi="1234567890",
    )
    assert record.clm_id == "CLM_2001"
    assert record.line_num == 1


def test_carrier_claim_line_invalid_line_num() -> None:
    with pytest.raises(ValidationError):
        CarrierClaimLineRecord(
            clm_id="CLM_2001",
            line_num=0,  # line_num must be >= 1
            bene_id="BENE_1001",
            clm_from_dt=date(2021, 3, 1),
            clm_thru_dt=date(2021, 3, 1),
        )


def test_outpatient_claim_header_record_valid() -> None:
    record = OutpatientClaimHeaderRecord(
        clm_id="CLM_3001",
        bene_id="BENE_1001",
        clm_from_dt=date(2021, 4, 10),
        clm_thru_dt=date(2021, 4, 12),
        icd_dgns_cd1="I10",
    )
    assert record.clm_id == "CLM_3001"
    assert record.icd_dgns_cd1 == "I10"
