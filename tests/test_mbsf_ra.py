"""Unit tests for MBSF Risk Adjustment Segment domain extension, validation, and release pipelines."""

import tempfile
from pathlib import Path
import pytest
from medicare_synth.cli import main
from medicare_synth.evidence import RKBEvidenceSnapshot
from medicare_synth.manifest import SourceManifest
from medicare_synth.models import MBSFRiskAdjustmentRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator, Severity


def test_mbsf_ra_model_validation():
    """Tests valid and invalid field assignments on MBSFRiskAdjustmentRecord."""
    rec = MBSFRiskAdjustmentRecord(
        bene_id="BENE_RA_001",
        rfrnc_yr=2021,
        cms_hcc_risk_score=1.450,
        rxhcc_risk_score=1.200,
        payment_count=12,
        val_mbsf_ra_01=1.0,
    )
    assert rec.bene_id == "BENE_RA_001"
    assert rec.cms_hcc_risk_score == 1.450
    assert rec.payment_count == 12

    with pytest.raises(Exception):
        MBSFRiskAdjustmentRecord(bene_id="BENE_RA_002", cms_hcc_risk_score=-0.500)


def test_mbsf_ra_manifest_and_evidence():
    """Verifies manifest entry and RKB snapshot variables/constraints for MBSF Risk Adjustment Segment."""
    manifest = SourceManifest.load_default_manifest()
    ra_file = next((f for f in manifest.files if f.file_domain == "mbsf_ra"), None)
    assert ra_file is not None
    assert ra_file.file_id == "DE1_0_2021_MBSF_Risk_Adjustment_Sample_1"
    assert ra_file.primary_key == ["BENE_ID"]

    snapshot = RKBEvidenceSnapshot.load_default_snapshot()
    assert "CMS_HCC_RISK_SCORE" in snapshot.variables
    assert "RXHCC_RISK_SCORE" in snapshot.variables
    assert "PAYMENT_COUNT" in snapshot.variables

    ra_constraint = next(
        (c for c in snapshot.constraints if c.constraint_id == "VAL_MBSF_RA_01"), None
    )
    assert ra_constraint is not None
    assert ra_constraint.category == "field"


def test_mbsf_ra_relational_validation():
    """Tests relational validator on valid cohort and negative risk score anomaly scenario."""
    validator = RelationalValidator()

    valid_slice = ScenarioCompiler.valid_baseline_cohort()
    valid_report = validator.validate_slice(
        bene_df=valid_slice.bene_df,
        carrier_df=valid_slice.carrier_df,
        outpatient_df=valid_slice.outpatient_df,
        mbsf_ra_df=valid_slice.mbsf_ra_df,
    )
    assert valid_report.is_valid

    invalid_slice = ScenarioCompiler.invalid_mbsf_risk_adjustment_score()
    invalid_report = validator.validate_slice(
        bene_df=invalid_slice.bene_df,
        carrier_df=invalid_slice.carrier_df,
        outpatient_df=invalid_slice.outpatient_df,
        mbsf_ra_df=invalid_slice.mbsf_ra_df,
    )
    assert not invalid_report.is_valid
    fld_findings = [f for f in invalid_report.findings if f.rule_id == "FLD-012"]
    assert len(fld_findings) == 1
    assert fld_findings[0].severity == Severity.HIGH


def test_mbsf_ra_normalizer():
    """Tests BaselineNormalizer.normalize_mbsf_ra with raw record dictionaries."""
    records = [
        {
            "bene_id": "BENE_RA_101",
            "rfrnc_yr": 2021,
            "cms_hcc_risk_score": 1.150,
            "rxhcc_risk_score": 1.050,
            "payment_count": 12,
            "val_mbsf_ra_01": 1.0,
        }
    ]
    df = BaselineNormalizer.normalize_mbsf_ra(records)
    assert df.height == 1
    assert "cms_hcc_risk_score" in df.columns
    assert df["cms_hcc_risk_score"][0] == 1.150


def test_mbsf_ra_exporter_and_cli():
    """Tests release exporter writing mbsf_ra artifacts and CLI subcommand integration."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir)
        slice_data = ScenarioCompiler.valid_baseline_cohort()
        exporter = ReleaseExporter(output_dir=out_dir, release_id="test_ra_release")
        manifest = exporter.export_slice(
            bene_df=slice_data.bene_df,
            carrier_df=slice_data.carrier_df,
            outpatient_df=slice_data.outpatient_df,
            mbsf_ra_df=slice_data.mbsf_ra_df,
            fmt="all",
        )
        assert manifest.validation_passed
        assert "mbsf_ra_csv" in manifest.files
        assert "mbsf_ra_parquet" in manifest.files
        assert (out_dir / "mbsf_ra.csv").exists()
        assert (out_dir / "mbsf_ra.parquet").exists()

        # CLI subcommand test
        ret = main(["validate", "--scenario", "invalid_mbsf_risk_adjustment_score"])
        assert ret == 1
