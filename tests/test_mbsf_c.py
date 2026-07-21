"""Unit tests for MBSF Part C / Medicare Advantage Segment domain extension, validation, and release pipelines."""

import tempfile
from pathlib import Path
import pytest
from medicare_synth.cli import main
from medicare_synth.evidence import RKBEvidenceSnapshot
from medicare_synth.manifest import SourceManifest
from medicare_synth.models import MBSFPartCRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator, Severity


def test_mbsf_c_model_validation():
    """Tests valid and invalid field assignments on MBSFPartCRecord."""
    rec = MBSFPartCRecord(
        bene_id="BENE_C_001",
        rfrnc_yr=2021,
        ptc_cntrct_id_01="H0001",
        ptc_pbp_id_01="001",
        ptc_plan_type_cd_01="01",
        bene_ma_cvrage_tot_mons=12,
        val_mbsf_c_01=1.0,
    )
    assert rec.bene_id == "BENE_C_001"
    assert rec.ptc_cntrct_id_01 == "H0001"
    assert rec.bene_ma_cvrage_tot_mons == 12

    with pytest.raises(Exception):
        MBSFPartCRecord(bene_id="BENE_C_002", bene_ma_cvrage_tot_mons=15)


def test_mbsf_c_manifest_and_evidence():
    """Verifies manifest entry and RKB snapshot variables/constraints for MBSF Part C Segment."""
    manifest = SourceManifest.load_default_manifest()
    c_file = next((f for f in manifest.files if f.file_domain == "mbsf_c"), None)
    assert c_file is not None
    assert c_file.file_id == "DE1_0_2021_MBSF_Part_C_Sample_1"
    assert c_file.primary_key == ["BENE_ID"]

    snapshot = RKBEvidenceSnapshot.load_default_snapshot()
    assert "PTC_CNTRCT_ID_01" in snapshot.variables
    assert "PTC_PBP_ID_01" in snapshot.variables
    assert "PTC_PLAN_TYPE_CD_01" in snapshot.variables
    assert "BENE_MA_CVRAGE_TOT_MONS" in snapshot.variables

    c_constraint = next(
        (c for c in snapshot.constraints if c.constraint_id == "VAL_MBSF_C_01"), None
    )
    assert c_constraint is not None
    assert c_constraint.category == "field"


def test_mbsf_c_relational_validation():
    """Tests relational validator on valid cohort and coverage months anomaly scenario."""
    validator = RelationalValidator()

    valid_slice = ScenarioCompiler.valid_baseline_cohort()
    valid_report = validator.validate_slice(
        bene_df=valid_slice.bene_df,
        carrier_df=valid_slice.carrier_df,
        outpatient_df=valid_slice.outpatient_df,
        mbsf_c_df=valid_slice.mbsf_c_df,
    )
    assert valid_report.is_valid

    invalid_slice = ScenarioCompiler.invalid_mbsf_part_c_contract()
    invalid_report = validator.validate_slice(
        bene_df=invalid_slice.bene_df,
        carrier_df=invalid_slice.carrier_df,
        outpatient_df=invalid_slice.outpatient_df,
        mbsf_c_df=invalid_slice.mbsf_c_df,
    )
    assert not invalid_report.is_valid
    fld_findings = [f for f in invalid_report.findings if f.rule_id == "FLD-013"]
    assert len(fld_findings) == 1
    assert fld_findings[0].severity == Severity.HIGH


def test_mbsf_c_normalizer():
    """Tests BaselineNormalizer.normalize_mbsf_part_c with raw record dictionaries."""
    records = [
        {
            "bene_id": "BENE_C_101",
            "rfrnc_yr": 2021,
            "ptc_cntrct_id_01": "H0005",
            "ptc_pbp_id_01": "005",
            "ptc_plan_type_cd_01": "01",
            "bene_ma_cvrage_tot_mons": 12,
            "val_mbsf_c_01": 1.0,
        }
    ]
    df = BaselineNormalizer.normalize_mbsf_part_c(records)
    assert df.height == 1
    assert "ptc_cntrct_id_01" in df.columns
    assert df["ptc_cntrct_id_01"][0] == "H0005"


def test_mbsf_c_exporter_and_cli():
    """Tests release exporter writing mbsf_c artifacts and CLI subcommand integration."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir)
        slice_data = ScenarioCompiler.valid_baseline_cohort()

        exporter = ReleaseExporter(output_dir=out_dir)
        manifest = exporter.export_slice(
            bene_df=slice_data.bene_df,
            carrier_df=slice_data.carrier_df,
            outpatient_df=slice_data.outpatient_df,
            fmt="parquet",
            mbsf_c_df=slice_data.mbsf_c_df,
        )
        assert manifest.validation_passed
        assert (out_dir / "mbsf_c.parquet").exists()

        ret = main(["validate", "--scenario", "invalid_mbsf_part_c_contract"])
        assert ret == 1

        ret_valid = main(["validate", "--scenario", "valid_baseline_cohort"])
        assert ret_valid == 0
