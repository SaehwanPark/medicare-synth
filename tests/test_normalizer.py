"""Behavioral tests for BaselineNormalizer."""

from datetime import date
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.models import ProvenanceStatus


def test_normalize_beneficiaries():
    records = [
        {
            "bene_id": "BENE_100",
            "bene_birth_dt": "1955-04-12",
            "bene_death_dt": None,
            "bene_sex_ident_cd": "1",
            "bene_race_cd": "2",
        }
    ]
    df = BaselineNormalizer.normalize_beneficiaries(records)
    assert df.height == 1
    assert df["bene_id"][0] == "BENE_100"
    assert df["bene_birth_dt"][0] == date(1955, 4, 12)

    meta = BaselineNormalizer.attach_provenance_metadata(
        df, ProvenanceStatus.NORMALIZED
    )
    assert meta["row_count"] == 1
    assert meta["provenance_status"] == "NORMALIZED"


def test_normalize_carrier_claims():
    records = [
        {
            "clm_id": "CLM_99",
            "line_num": 1,
            "bene_id": "BENE_100",
            "clm_from_dt": "2021-02-01",
            "clm_thru_dt": "2021-02-05",
            "prvdr_npi": "1234567890",
            "icd_dgns_cd1": "I10",
        }
    ]
    df = BaselineNormalizer.normalize_carrier_claims(records)
    assert df.height == 1
    assert df["clm_id"][0] == "CLM_99"
    assert df["clm_from_dt"][0] == date(2021, 2, 1)


def test_normalize_outpatient_claims():
    records = [
        {
            "clm_id": "CLM_OUT1",
            "bene_id": "BENE_100",
            "clm_from_dt": "2021-03-10",
            "clm_thru_dt": "2021-03-10",
            "prvdr_npi": "0987654321",
            "icd_dgns_cd1": "Z0000",
        }
    ]
    df = BaselineNormalizer.normalize_outpatient_claims(records)
    assert df.height == 1
    assert df["clm_id"][0] == "CLM_OUT1"
    assert df["clm_thru_dt"][0] == date(2021, 3, 10)
