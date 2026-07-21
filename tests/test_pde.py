"""Unit tests for Part D Prescription Drug Event (PDE) domain models, validators, scenarios, and pipelines."""

from datetime import date
import pytest
from pydantic import ValidationError

from medicare_synth.audit import AuditEngine
from medicare_synth.expansion import HorizontalExpander
from medicare_synth.models import PrescriptionDrugEventRecord
from medicare_synth.normalizer import BaselineNormalizer

from medicare_synth.release import ReleaseExporter
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator, Severity


def test_pde_record_valid():
    """Tests instantiation of a valid PrescriptionDrugEventRecord."""
    record = PrescriptionDrugEventRecord(
        pde_id="PDE_1001",
        bene_id="BENE_001",
        srvc_dt=date(2021, 5, 10),
        prod_srvc_id="00093015001",
        qty_dspnsd_num=30.0,
        days_suply_num=30,
        ptnt_pay_amt=12.50,
        tot_rx_cst_amt=50.00,
    )
    assert record.pde_id == "PDE_1001"
    assert record.bene_id == "BENE_001"
    assert record.days_suply_num == 30


def test_pde_record_invalid_days_supply():
    """Tests that negative days supply raises validation error."""
    with pytest.raises(ValidationError):
        PrescriptionDrugEventRecord(
            pde_id="PDE_1001",
            bene_id="BENE_001",
            srvc_dt=date(2021, 5, 10),
            days_suply_num=-5,
        )


def test_baseline_normalizer_pde():
    """Tests normalization of raw PDE dictionary records into a Polars DataFrame."""
    raw_records = [
        {
            "pde_id": "PDE_1001",
            "bene_id": "BENE_001",
            "srvc_dt": date(2021, 5, 10),
            "prod_srvc_id": "00093015001",
            "qty_dspnsd_num": 30.0,
            "days_suply_num": 30,
            "ptnt_pay_amt": 12.50,
            "tot_rx_cst_amt": 50.00,
        }
    ]
    df = BaselineNormalizer.normalize_pde_events(raw_records)
    assert df.height == 1
    assert "pde_id" in df.columns
    assert "days_suply_num" in df.columns


def test_validator_pde_field_constraint():
    """Tests detection of invalid negative days supply in RelationalValidator."""
    slice_data = ScenarioCompiler.get_scenario("invalid_pde_days_supply")
    validator = RelationalValidator()
    report = validator.validate_slice(
        bene_df=slice_data.bene_df,
        carrier_df=slice_data.carrier_df,
        outpatient_df=slice_data.outpatient_df,
        inpatient_df=slice_data.inpatient_df,
        pde_df=slice_data.pde_df,
    )
    assert not report.is_valid
    fld_findings = [f for f in report.findings if f.rule_id == "FLD-001"]
    assert len(fld_findings) == 1
    assert fld_findings[0].severity == Severity.HIGH


def test_exporter_with_pde(tmp_path):
    """Tests ReleaseExporter inclusion of PDE table and metadata."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    exporter = ReleaseExporter(output_dir=tmp_path, release_id="v1.0.0-test")
    manifest = exporter.export_slice(
        bene_df=slice_data.bene_df,
        carrier_df=slice_data.carrier_df,
        outpatient_df=slice_data.outpatient_df,
        fmt="csv",
        inpatient_df=slice_data.inpatient_df,
        pde_df=slice_data.pde_df,
    )
    assert manifest.validation_passed
    assert "pde_csv" in manifest.files
    assert (tmp_path / "pde.csv").exists()


def test_horizontal_expansion_pde():
    """Tests horizontal subgraph scaling with PDE table re-keying."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    tables = {
        "beneficiary_summary": slice_data.bene_df,
        "carrier_claims": slice_data.carrier_df,
        "outpatient_claims": slice_data.outpatient_df,
        "inpatient_claims": slice_data.inpatient_df,
        "pde_events": slice_data.pde_df,
    }
    expander = HorizontalExpander()
    scaled = expander.expand_subgraph(tables, scale_factor=2)
    assert scaled["pde_events"].height == slice_data.pde_df.height * 2
    assert any(
        "_H1" in pid for pid in scaled["pde_events"].get_column("pde_id").to_list()
    )


def test_audit_engine_pde():
    """Tests AuditEngine join coverage and metrics for PDE tables."""
    slice_data = ScenarioCompiler.valid_baseline_cohort()
    tables = {
        "beneficiary": slice_data.bene_df,
        "carrier": slice_data.carrier_df,
        "outpatient": slice_data.outpatient_df,
        "inpatient": slice_data.inpatient_df,
        "pde": slice_data.pde_df,
    }
    engine = AuditEngine(dataset=tables, scenario_name="valid_baseline_cohort")
    report = engine.run_audit()
    assert "beneficiary_pde_coverage" in report.join_coverage
    assert report.join_coverage["beneficiary_pde_coverage"] == 1.0
    assert "pde" in report.column_metrics
