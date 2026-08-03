"""Unit tests for MBSF Base Enrollment Segment domain extension, validators, normalizer, and scenarios."""

from pathlib import Path
import tempfile

import polars as pl
import pytest
from pydantic import ValidationError

from medicare_synth.cli import main
from medicare_synth.models import MBSFBaseEnrollmentRecord
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator


def test_mbsf_base_record_validation():
    """Tests valid and invalid MBSFBaseEnrollmentRecord model instantiations."""
    rec = MBSFBaseEnrollmentRecord(
        bene_id="BENE_BASE_01",
        rfrnc_yr=2021,
        bene_hi_cvrage_tot_mons=12,
        bene_smi_cvrage_tot_mons=12,
        bene_hmo_cvrage_tot_mons=0,
        bene_ptd_cvrage_tot_mons=12,
        mdcr_entlmt_buyin_ind_01="C",
        dual_stus_cd_01="00",
    )
    assert rec.bene_id == "BENE_BASE_01"
    assert rec.bene_hi_cvrage_tot_mons == 12

    with pytest.raises(ValidationError):
        MBSFBaseEnrollmentRecord(
            bene_id="BENE_ERR",
            bene_hi_cvrage_tot_mons=15,  # Invalid coverage months (>12)
        )


def test_check_mbsf_base_field_constraints():
    """Tests RelationalValidator field constraint checking for MBSF Base Enrollment records."""
    validator = RelationalValidator()

    valid_df = pl.DataFrame(
        [
            {
                "bene_id": "BENE_001",
                "rfrnc_yr": 2021,
                "bene_hi_cvrage_tot_mons": 12,
                "bene_smi_cvrage_tot_mons": 12,
                "bene_hmo_cvrage_tot_mons": 0,
                "bene_ptd_cvrage_tot_mons": 12,
            }
        ]
    )
    findings = validator.check_mbsf_base_field_constraints(valid_df)
    assert len(findings) == 0

    invalid_df = pl.DataFrame(
        [
            {
                "bene_id": "BENE_001",
                "rfrnc_yr": 2021,
                "bene_hi_cvrage_tot_mons": 14,  # Invalid (>12)
                "bene_smi_cvrage_tot_mons": 12,
                "bene_hmo_cvrage_tot_mons": 0,
                "bene_ptd_cvrage_tot_mons": 12,
            }
        ]
    )
    findings = validator.check_mbsf_base_field_constraints(invalid_df)
    assert len(findings) == 1
    assert findings[0].rule_id == "FLD-009"


def test_normalize_mbsf_base():
    """Tests BaselineNormalizer.normalize_mbsf_base for dictionary record conversion."""
    raw_records = [
        {
            "bene_id": "BENE_NORM_01",
            "rfrnc_yr": 2021,
            "bene_hi_cvrage_tot_mons": 12,
            "bene_smi_cvrage_tot_mons": 10,
            "bene_hmo_cvrage_tot_mons": 2,
            "bene_ptd_cvrage_tot_mons": 12,
        }
    ]
    df = BaselineNormalizer.normalize_mbsf_base(raw_records)
    assert isinstance(df, pl.DataFrame)
    assert df.height == 1
    assert "bene_hi_cvrage_tot_mons" in df.columns


def test_scenario_compiler_mbsf_base():
    """Tests compilation and validation of MBSF Base Enrollment scenario fixtures."""
    valid_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
    assert valid_slice.mbsf_base_df.height == 3

    validator = RelationalValidator()
    report = validator.validate_slice(
        bene_df=valid_slice.bene_df,
        carrier_df=valid_slice.carrier_df,
        outpatient_df=valid_slice.outpatient_df,
        inpatient_df=valid_slice.inpatient_df,
        pde_df=valid_slice.pde_df,
        snf_df=valid_slice.snf_df,
        hha_df=valid_slice.hha_df,
        dme_df=valid_slice.dme_df,
        hospice_df=valid_slice.hospice_df,
        mbsf_cc_df=valid_slice.mbsf_cc_df,
        mbsf_cu_df=valid_slice.mbsf_cu_df,
        mbsf_d_df=valid_slice.mbsf_d_df,
        mbsf_base_df=valid_slice.mbsf_base_df,
    )
    assert report.is_valid

    anomaly_slice = ScenarioCompiler.get_scenario("invalid_mbsf_base_coverage_months")
    report_anomaly = validator.validate_slice(
        bene_df=anomaly_slice.bene_df,
        carrier_df=anomaly_slice.carrier_df,
        outpatient_df=anomaly_slice.outpatient_df,
        mbsf_base_df=anomaly_slice.mbsf_base_df,
    )
    assert not report_anomaly.is_valid
    assert any(f.rule_id == "FLD-009" for f in report_anomaly.findings)


def test_release_exporter_mbsf_base():
    """Tests ReleaseExporter inclusion of MBSF Base Enrollment table in export bundle."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = ReleaseExporter(output_dir=Path(tmpdir))
        manifest = exporter.export_slice(
            bene_df=slice_data.bene_df,
            carrier_df=slice_data.carrier_df,
            outpatient_df=slice_data.outpatient_df,
            mbsf_base_df=slice_data.mbsf_base_df,
            fmt="parquet",
        )
        assert manifest.validation_passed
        assert "mbsf_base_parquet" in manifest.files
        assert (Path(tmpdir) / "mbsf_base.parquet").exists()


def test_cli_mbsf_base_scenario():
    """Tests CLI execution of validate and scenario subcommands with MBSF Base anomaly."""
    ret_valid = main(["validate", "--scenario", "valid_baseline_cohort"])
    assert ret_valid == 0

    ret_invalid = main(["validate", "--scenario", "invalid_mbsf_base_coverage_months"])
    assert ret_invalid == 1


def test_check_mbsf_enrollment_buyin_indicator_constraints_valid():
    """Tests ENR-002: valid buy-in indicator codes produce no findings."""
    validator = RelationalValidator()

    valid_df = pl.DataFrame(
        {
            "bene_id": ["BENE_A", "BENE_B"],
            "mdcr_entlmt_buyin_ind_01": ["3", "C"],
            "mdcr_entlmt_buyin_ind_02": ["A", "B"],
            "mdcr_entlmt_buyin_ind_03": [None, "0"],  # NULL is valid (no enrollment)
        }
    )
    findings = validator.check_mbsf_enrollment_buyin_indicator_constraints(valid_df)
    assert len(findings) == 0


def test_check_mbsf_enrollment_buyin_indicator_constraints_invalid():
    """Tests ENR-002: invalid buy-in indicator code produces exactly one ENR-002 finding."""
    validator = RelationalValidator()

    invalid_df = pl.DataFrame(
        {
            "bene_id": ["BENE_X"],
            "mdcr_entlmt_buyin_ind_01": ["X"],   # Invalid: not in {"0","1","2","3","A","B","C"}
            "mdcr_entlmt_buyin_ind_02": ["3"],
        }
    )
    findings = validator.check_mbsf_enrollment_buyin_indicator_constraints(invalid_df)
    assert len(findings) == 1
    assert findings[0].rule_id == "ENR-002"
    assert findings[0].count == 1


def test_check_mbsf_enrollment_buyin_indicator_constraints_no_columns():
    """Tests ENR-002: empty column set returns no findings (early-exit path)."""
    validator = RelationalValidator()

    # DataFrame with no monthly buy-in columns present.
    df_no_cols = pl.DataFrame({"bene_id": ["BENE_A"], "rfrnc_yr": [2021]})
    findings = validator.check_mbsf_enrollment_buyin_indicator_constraints(df_no_cols)
    assert len(findings) == 0


def test_check_mbsf_dual_status_code_constraints_valid():
    """Tests ENR-003: valid dual status codes produce no findings."""
    validator = RelationalValidator()

    valid_df = pl.DataFrame(
        {
            "bene_id": ["BENE_A", "BENE_B"],
            "dual_stus_cd_01": ["00", "02"],
            "dual_stus_cd_02": ["99", None],  # NULL is valid
            "dual_stus_cd_03": ["10", "08"],
        }
    )
    findings = validator.check_mbsf_dual_status_code_constraints(valid_df)
    assert len(findings) == 0


def test_check_mbsf_dual_status_code_constraints_invalid():
    """Tests ENR-003: invalid dual status code produces exactly one ENR-003 finding."""
    validator = RelationalValidator()

    invalid_df = pl.DataFrame(
        {
            "bene_id": ["BENE_Y"],
            "dual_stus_cd_01": ["ZZ"],   # Invalid: not in valid CMS-MIS set
            "dual_stus_cd_02": ["00"],
        }
    )
    findings = validator.check_mbsf_dual_status_code_constraints(invalid_df)
    assert len(findings) == 1
    assert findings[0].rule_id == "ENR-003"
    assert findings[0].count == 1


def test_check_mbsf_dual_status_code_constraints_no_columns():
    """Tests ENR-003: empty column set returns no findings (early-exit path)."""
    validator = RelationalValidator()

    df_no_cols = pl.DataFrame({"bene_id": ["BENE_A"], "rfrnc_yr": [2021]})
    findings = validator.check_mbsf_dual_status_code_constraints(df_no_cols)
    assert len(findings) == 0


def test_cli_auto_workflow_mbsf_buyin_and_dual_status_check():
    """Tests that --mbsf-enrollment-buyin-check and --mbsf-dual-status-check flags are accepted by the CLI."""
    ret = main(
        [
            "auto-workflow",
            "--dry-run",
            "--mbsf-enrollment-buyin-check",
            "--mbsf-dual-status-check",
            "--mbsf-entitlement-reason-check",
        ]
    )
    assert ret == 0


def test_check_mbsf_entitlement_reason_code_constraints_valid():
    """Tests ENR-004: valid entitlement reason codes produce no findings."""
    validator = RelationalValidator()

    valid_df = pl.DataFrame(
        {
            "bene_id": ["BENE_A", "BENE_B"],
            "entlmt_rsn_orig": ["10", "0"],
            "entlmt_rsn_curr": ["20", None],  # NULL is valid
        }
    )
    findings = validator.check_mbsf_entitlement_reason_code_constraints(valid_df)
    assert len(findings) == 0


def test_check_mbsf_entitlement_reason_code_constraints_invalid():
    """Tests ENR-004: invalid entitlement reason code produces exactly one ENR-004 finding."""
    validator = RelationalValidator()

    invalid_df = pl.DataFrame(
        {
            "bene_id": ["BENE_Z"],
            "entlmt_rsn_orig": ["999"],  # Invalid: not in CCW valid set
            "entlmt_rsn_curr": ["10"],
        }
    )
    findings = validator.check_mbsf_entitlement_reason_code_constraints(invalid_df)
    assert len(findings) == 1
    assert findings[0].rule_id == "ENR-004"
    assert findings[0].count == 1


def test_check_mbsf_entitlement_reason_code_constraints_no_columns():
    """Tests ENR-004: empty column set returns no findings (early-exit path)."""
    validator = RelationalValidator()

    df_no_cols = pl.DataFrame({"bene_id": ["BENE_A"], "rfrnc_yr": [2021]})
    findings = validator.check_mbsf_entitlement_reason_code_constraints(df_no_cols)
    assert len(findings) == 0


def test_check_mbsf_entitlement_reason_code_constraints_all_null():
    """Tests ENR-004: all-null column DataFrame returns no findings."""
    validator = RelationalValidator()

    df_null = pl.DataFrame(
        {"bene_id": ["BENE_A"], "entlmt_rsn_orig": [None]},
        schema={"bene_id": pl.String, "entlmt_rsn_orig": pl.Null},
    )
    findings = validator.check_mbsf_entitlement_reason_code_constraints(df_null)
    assert len(findings) == 0


def test_check_mbsf_hmo_indicator_constraints_valid():
    """Tests ENR-005: valid monthly HMO indicator codes produce no findings."""
    validator = RelationalValidator()

    valid_df = pl.DataFrame(
        {
            "bene_id": ["BENE_A", "BENE_B"],
            "hmo_ind_01": ["0", "A"],
            "hmo_ind_02": ["1", None],  # NULL is valid
            "hmo_ind_12": ["C", "N"],
        }
    )
    findings = validator.check_mbsf_hmo_indicator_constraints(valid_df)
    assert len(findings) == 0


def test_check_mbsf_hmo_indicator_constraints_invalid():
    """Tests ENR-005: invalid monthly HMO indicator code produces exactly one ENR-005 finding."""
    validator = RelationalValidator()

    invalid_df = pl.DataFrame(
        {
            "bene_id": ["BENE_Z"],
            "hmo_ind_01": ["X"],  # Invalid: not in CCW valid set
            "hmo_ind_02": ["0"],
        }
    )
    findings = validator.check_mbsf_hmo_indicator_constraints(invalid_df)
    assert len(findings) == 1
    assert findings[0].rule_id == "ENR-005"
    assert findings[0].count == 1


def test_check_mbsf_hmo_indicator_constraints_no_columns():
    """Tests ENR-005: empty column set returns no findings (early-exit path)."""
    validator = RelationalValidator()

    df_no_cols = pl.DataFrame({"bene_id": ["BENE_A"], "rfrnc_yr": [2021]})
    findings = validator.check_mbsf_hmo_indicator_constraints(df_no_cols)
    assert len(findings) == 0


def test_check_mbsf_hmo_indicator_constraints_all_null():
    """Tests ENR-005: all-null column DataFrame returns no findings."""
    validator = RelationalValidator()

    df_null = pl.DataFrame(
        {"bene_id": ["BENE_A"], "hmo_ind_01": [None]},
        schema={"bene_id": pl.String, "hmo_ind_01": pl.Null},
    )
    findings = validator.check_mbsf_hmo_indicator_constraints(df_null)
    assert len(findings) == 0
