"""Unit tests for MBSF FFS Utilization Segment domain extension, validation, and release pipelines."""

import tempfile
from pathlib import Path
import pytest
from medicare_synth.cli import main
from medicare_synth.evidence import RKBEvidenceSnapshot
from medicare_synth.manifest import SourceManifest
from medicare_synth.models import MBSFFFSUtilizationRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator, Severity


def test_mbsf_ffs_model_validation():
    """Tests valid and invalid field assignments on MBSFFFSUtilizationRecord."""
    rec = MBSFFFSUtilizationRecord(
        bene_id="BENE_FFS_001",
        rfrnc_yr=2021,
        ip_adm_cnt=2,
        op_vist_cnt=5,
        snf_stay_cnt=1,
        car_srvc_cnt=10,
        hha_vist_cnt=0,
        hosp_stay_cnt=0,
        dme_srvc_cnt=2,
        val_mbsf_ffs_01=1.0,
    )
    assert rec.bene_id == "BENE_FFS_001"
    assert rec.ip_adm_cnt == 2
    assert rec.car_srvc_cnt == 10

    with pytest.raises(Exception):
        MBSFFFSUtilizationRecord(bene_id="BENE_FFS_002", ip_adm_cnt=-1)


def test_mbsf_ffs_manifest_and_evidence():
    """Verifies manifest entry and RKB snapshot variables/constraints for MBSF FFS Utilization Segment."""
    manifest = SourceManifest.load_default_manifest()
    ffs_file = next((f for f in manifest.files if f.file_domain == "mbsf_ffs"), None)
    assert ffs_file is not None
    assert ffs_file.file_id == "DE1_0_2021_MBSF_FFS_Utilization_Sample_1"
    assert ffs_file.primary_key == ["BENE_ID"]

    snapshot = RKBEvidenceSnapshot.load_default_snapshot()
    assert "IP_ADM_CNT" in snapshot.variables
    assert "OP_VIST_CNT" in snapshot.variables
    assert "SNF_STAY_CNT" in snapshot.variables
    assert "CAR_SRVC_CNT" in snapshot.variables

    ffs_constraint = next(
        (c for c in snapshot.constraints if c.constraint_id == "VAL_MBSF_FFS_01"), None
    )
    assert ffs_constraint is not None
    assert ffs_constraint.category == "field"


def test_mbsf_ffs_relational_validation():
    """Tests relational validator on valid cohort and utilization count anomaly scenario."""
    validator = RelationalValidator()

    valid_slice = ScenarioCompiler.valid_baseline_cohort()
    valid_report = validator.validate_slice(
        bene_df=valid_slice.bene_df,
        carrier_df=valid_slice.carrier_df,
        outpatient_df=valid_slice.outpatient_df,
        mbsf_ffs_df=valid_slice.mbsf_ffs_df,
    )
    assert valid_report.is_valid

    invalid_slice = ScenarioCompiler.invalid_mbsf_ffs_utilization_count()
    invalid_report = validator.validate_slice(
        bene_df=invalid_slice.bene_df,
        carrier_df=invalid_slice.carrier_df,
        outpatient_df=invalid_slice.outpatient_df,
        mbsf_ffs_df=invalid_slice.mbsf_ffs_df,
    )
    assert not invalid_report.is_valid
    fld_findings = [f for f in invalid_report.findings if f.rule_id == "FLD-014"]
    assert len(fld_findings) == 1
    assert fld_findings[0].severity == Severity.HIGH


def test_mbsf_ffs_normalizer():
    """Tests BaselineNormalizer.normalize_mbsf_ffs_utilization with raw record dictionaries."""
    records = [
        {
            "bene_id": "BENE_FFS_101",
            "rfrnc_yr": 2021,
            "ip_adm_cnt": 1,
            "op_vist_cnt": 3,
            "snf_stay_cnt": 0,
            "car_srvc_cnt": 4,
            "hha_vist_cnt": 0,
            "hosp_stay_cnt": 0,
            "dme_srvc_cnt": 1,
            "val_mbsf_ffs_01": 1.0,
        }
    ]
    df = BaselineNormalizer.normalize_mbsf_ffs_utilization(records)
    assert df.height == 1
    assert "ip_adm_cnt" in df.columns
    assert df["ip_adm_cnt"][0] == 1


def test_mbsf_ffs_exporter_and_cli():
    """Tests release exporter writing mbsf_ffs artifacts and CLI subcommand integration."""
    valid_slice = ScenarioCompiler.valid_baseline_cohort()
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "release"
        exporter = ReleaseExporter(output_dir=output_dir, release_id="test_release_ffs")
        manifest = exporter.export_slice(
            bene_df=valid_slice.bene_df,
            carrier_df=valid_slice.carrier_df,
            outpatient_df=valid_slice.outpatient_df,
            mbsf_ffs_df=valid_slice.mbsf_ffs_df,
        )
        assert manifest.validation_passed
        assert (output_dir / "mbsf_ffs.parquet").exists()
        assert (output_dir / "mbsf_ffs.csv").exists()

    with tempfile.TemporaryDirectory() as tmpdir:
        ret = main(
            [
                "export",
                "--scenario",
                "valid_baseline_cohort",
                "--output-dir",
                tmpdir,
                "--format",
                "parquet",
            ]
        )
        assert ret == 0
        assert (Path(tmpdir) / "mbsf_ffs.parquet").exists()
