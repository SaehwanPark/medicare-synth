"""Behavioral tests for the bounded CMS PUF importer using synthetic fixtures."""

import hashlib
import json
from pathlib import Path

import polars as pl

from medicare_synth.puf import PufImporter
from medicare_synth.validation import RelationalValidator


def _write_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    beneficiary = (
        "BENE_ID|BENE_BIRTH_DT|BENE_DEATH_DT|BENE_SEX_IDENT_CD|BENE_RACE_CD\n"
        "0001|1940-01-01||1|1\n"
    )
    carrier = (
        "CLM_ID|LINE_NUM|BENE_ID|CLM_FROM_DT|CLM_THRU_DT|PRVDR_NPI|ICD_DGNS_CD1\n"
        "C1|1|0001|2022-02-01|2022-02-02|1234567890|A123\n"
        "C1|2|0001|2022-02-01|2022-02-02|1234567890|A124\n"
        "C2|1|0001|2021-01-01|2021-01-01|1234567890|A125\n"
    )
    paths = {}
    for name, content in (("beneficiary_2022.csv", beneficiary), ("carrier.csv", carrier)):
        path = tmp_path / name
        path.write_text(content, encoding="utf-8")
        paths[name] = path

    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    manifest = {
        "collection_id": "CMS-2022-SYNTHETIC-PUF",
        "title": "fixture",
        "schema_year": 2022,
        "version": "fixture",
        "description": "fixture",
        "source_organization": "CMS",
        "retrieval_date": "2026-07-26",
        "license": "CMS public-use terms",
        "files": [
            {"file_id": "beneficiary_2022", "filename": "beneficiary_2022.csv", "file_domain": "beneficiary", "grain": "beneficiary_year", "format": "csv", "expected_record_count": 1, "sha256": digest(paths["beneficiary_2022.csv"]), "source_url": "https://example.invalid/b", "primary_key": ["BENE_ID"], "delimiter": "|"},
            {"file_id": "carrier", "filename": "carrier.csv", "file_domain": "carrier", "grain": "claim_line", "format": "csv", "expected_record_count": 3, "sha256": digest(paths["carrier.csv"]), "source_url": "https://example.invalid/c", "primary_key": ["CLM_ID", "LINE_NUM"], "delimiter": "|"},
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps({"rkb_version": "fixture", "snapshot_date": "2026-07-26", "schema_year": 2022, "description": "fixture", "source_repository": "CMS", "variables": {name: {"name": name, "label": name, "data_type": "date", "format": "YYYY-MM-DD", "provenance_status": "preserved", "description": "fixture"} for name in ("BENE_BIRTH_DT", "BENE_DEATH_DT", "CLM_FROM_DT", "CLM_THRU_DT")}, "constraints": []}), encoding="utf-8")
    return tmp_path, manifest_path, evidence_path


def test_import_preserves_carrier_lines_and_filters_service_year(tmp_path: Path) -> None:
    source_dir, manifest_path, evidence_path = _write_fixture(tmp_path)
    result = PufImporter().load(source_dir, manifest_path, evidence_path)
    assert result.beneficiary_df.get_column("bene_id").to_list() == ["0001"]
    assert result.carrier_df.height == 2
    assert result.carrier_df.select(["clm_id", "line_num"]).rows() == [("C1", 1), ("C1", 2)]


def test_validator_reports_orphan_and_duplicate_line(tmp_path: Path) -> None:
    bene = pl.DataFrame({"bene_id": ["0001"]})
    carrier = pl.DataFrame({"clm_id": ["C1", "C1"], "line_num": [1, 1], "bene_id": ["0001", "9999"], "clm_from_dt": ["2022-01-01", "2022-01-01"], "clm_thru_dt": ["2022-01-01", "2022-01-01"]})
    report = RelationalValidator().validate_beneficiary_carrier_slice(bene, carrier)
    assert not report.is_valid
    assert {finding.rule_id for finding in report.findings} >= {"REC-001", "REL-001"}
