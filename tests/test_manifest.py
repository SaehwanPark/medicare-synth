"""Tests for source baseline manifest loading and verification."""

from pathlib import Path
import pytest
from medicare_synth.manifest import FileManifest, SourceManifest


@pytest.fixture
def sample_manifest_path() -> Path:
  return Path("data/manifests/cms_2021_syn_claims_manifest.json")


def test_load_source_manifest(sample_manifest_path: Path) -> None:
  assert sample_manifest_path.exists(), "Source manifest file must exist"
  manifest = SourceManifest.from_file(sample_manifest_path)
  assert manifest.collection_id == "CMS-2021-SYN-CLAIMS"
  assert manifest.schema_year == 2021
  assert len(manifest.files) == 17






def test_get_file_manifest(sample_manifest_path: Path) -> None:
  manifest = SourceManifest.from_file(sample_manifest_path)
  bene_fm = manifest.get_file_manifest("DE1_0_2021_Beneficiary_Summary_File_Sample_1")
  assert bene_fm is not None
  assert bene_fm.file_domain == "beneficiary"
  assert bene_fm.grain == "beneficiary_year"
  assert bene_fm.primary_key == ["BENE_ID"]

  nonexistent = manifest.get_file_manifest("INVALID_ID")
  assert nonexistent is None


def test_checksum_verification(tmp_path: Path) -> None:
  test_file = tmp_path / "test.csv"
  test_file.write_text("header1,header2\nval1,val2\n", encoding="utf-8")

  # Empty hash should fail verification
  fm = FileManifest(
    file_id="test_file",
    filename="test.csv",
    file_domain="test",
    grain="test",
    format="csv",
    expected_record_count=1,
    sha256="0000000000000000000000000000000000000000000000000000000000000000",
    source_url="http://example.com/test.zip",
    primary_key=["header1"],
  )
  assert not fm.verify_checksum(test_file)
  assert not fm.verify_checksum(tmp_path / "nonexistent.csv")
