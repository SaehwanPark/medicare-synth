"""Unit tests for ScenarioCatalog and CI fixture export."""

from pathlib import Path
import tempfile
from medicare_synth.catalog import ScenarioCatalog


def test_scenario_catalog_entries():
  catalog = ScenarioCatalog.get_catalog()
  assert len(catalog) == 13
  names = [e.name for e in catalog]
  assert "valid_baseline_cohort" in names
  assert "invalid_orphaned_claim" in names
  assert "invalid_inpatient_admission" in names
  assert "invalid_pde_days_supply" in names
  assert "invalid_snf_utilization_days" in names
  assert "invalid_hha_utilization_days" in names
  assert "invalid_dme_line_item_count" in names
  assert "invalid_hospice_utilization_days" in names
  assert "invalid_mbsf_chronic_condition_indicator" in names
  assert "invalid_mbsf_cost_use_payment" in names




def test_scenario_info_lookup():
  entry = ScenarioCatalog.get_scenario_info("valid_baseline_cohort")
  assert entry is not None
  assert entry.is_valid is True
  assert entry.expected_findings_count == 0

  missing = ScenarioCatalog.get_scenario_info("non_existent_scenario")
  assert missing is None


def test_export_ci_fixtures():
  with tempfile.TemporaryDirectory() as tmpdir:
    out_dir = Path(tmpdir) / "ci_fixtures"
    created = ScenarioCatalog.export_ci_fixtures(out_dir, file_format="parquet")
    assert len(created) > 0
    assert (out_dir / "valid_baseline_cohort" / "beneficiary_summary.parquet").exists()
