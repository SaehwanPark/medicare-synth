"""Unit tests for LimitationsProfiler and dataset disclosures."""

from pathlib import Path
import tempfile
from medicare_synth.profile import LimitationsCategory, LimitationsProfiler


def test_default_limitations_profile():
  profile = LimitationsProfiler.default_profile()
  assert len(profile.statements) == 6

  categories = [s.category for s in profile.statements]
  assert LimitationsCategory.STRUCTURAL in categories
  assert LimitationsCategory.RELATIONAL in categories
  assert LimitationsCategory.TEMPORAL in categories
  assert LimitationsCategory.ACCOUNTING in categories
  assert LimitationsCategory.DISTRIBUTIONAL in categories
  assert LimitationsCategory.INFERENTIAL in categories


def test_limitations_profile_save():
  with tempfile.TemporaryDirectory() as tmpdir:
    profile = LimitationsProfiler.default_profile()
    out_file = Path(tmpdir) / "profile.json"
    saved = profile.save_file(out_file)
    assert saved.exists()

    json_str = profile.to_json()
    assert "Beneficiary-Year and Claim Line/Header Scope Boundary" in json_str
