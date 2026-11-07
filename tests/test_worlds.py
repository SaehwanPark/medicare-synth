"""Behavioral tests for Phase 5 multi-world packaging."""

from __future__ import annotations

import pytest

from medicare_synth.calibration import load_default_corpus
from medicare_synth.evaluation import load_evaluation_freeze
from medicare_synth.worlds import (
  MVP_WORLD_FAMILY_ID,
  WorldsError,
  analyze_world_moments,
  emit_world_family,
  family_summary,
  get_world_preset,
  list_mvp_world_presets,
)


@pytest.fixture(scope="module")
def corpus_and_path():
  return load_default_corpus()


@pytest.fixture(scope="module")
def family(corpus_and_path):
  corpus, path = corpus_and_path
  freeze = load_evaluation_freeze(corpus=corpus)
  return emit_world_family(
    corpus=corpus,
    corpus_path=path,
    freeze=freeze,
    n_beneficiaries=2500,
    seed=42,
    diabetes_values=(0.18, 0.277, 0.32),
    hf_values=(0.04, 0.12),
    ip_diab_values=(0.05, 0.13),
  )


def test_presets_share_structure() -> None:
  presets = list_mvp_world_presets()
  assert len(presets) == 3
  ids = {p.world_id for p in presets}
  assert ids == {
    "mvp-w1-reweight-v1",
    "mvp-w2-generator-v1",
    "mvp-w3-generator-high-bg-ip-v1",
  }
  # Distinct free background IP assumptions across generator pair.
  w2 = get_world_preset("mvp-w2-generator-v1")
  w3 = get_world_preset("mvp-w3-generator-high-bg-ip-v1")
  assert w2.p_ip_given_no_diabetes == 0.04
  assert w3.p_ip_given_no_diabetes == 0.08
  with pytest.raises(WorldsError, match="unknown"):
    get_world_preset("not-a-world")


def test_family_shared_targets_and_structural_gates(family) -> None:
  assert family.family_id == MVP_WORLD_FAMILY_ID
  assert len(family.worlds) == 3
  shared = family.shared_calibration_finding_ids
  assert len(shared) == 3
  for w in family.worlds:
    assert w.calibration_finding_ids == shared
    assert w.structural_valid is True
    assert w.evaluation_freeze_id == family.evaluation_freeze_id
    assert w.holdout_finding_ids
    assert "holdout" in " ".join(w.run_manifest.assumptions).lower()


def test_calibrated_worlds_improve_and_differ_on_free_assumption(family) -> None:
  by_id = {w.world_id: w for w in family.worlds}
  w1 = by_id["mvp-w1-reweight-v1"]
  w2 = by_id["mvp-w2-generator-v1"]
  w3 = by_id["mvp-w3-generator-high-bg-ip-v1"]

  assert w1.improved_calibration is True
  assert w2.improved_calibration is True
  assert w3.improved_calibration is True
  assert w1.calibration_fitted.mean_absolute_error is not None
  assert w1.calibration_baseline.mean_absolute_error is not None
  assert (
    w1.calibration_fitted.mean_absolute_error
    < w1.calibration_baseline.mean_absolute_error
  )

  assert w2.params.p_ip_given_no_diabetes == 0.04
  assert w3.params.p_ip_given_no_diabetes == 0.08
  # Shared calibration knobs move toward the same targets.
  assert abs(w2.params.diabetes_prevalence - 0.277) <= 0.05
  assert abs(w3.params.diabetes_prevalence - 0.277) <= 0.05
  assert w2.sha256() != w3.sha256()


def test_identical_downstream_analysis_api(family, corpus_and_path) -> None:
  corpus, _ = corpus_and_path
  finding_sets: list[tuple[str, ...]] = []
  for w in family.worlds:
    cal, hold = analyze_world_moments(
      w.tables(), corpus, weights=w.weights
    )
    assert len(cal.rows) == 3
    assert len(hold.rows) == 1
    finding_sets.append(tuple(r.finding_id for r in cal.rows))
    # Weighted/fitted analysis should match the release fitted report closely.
    assert cal.mean_absolute_error is not None
    assert abs(cal.mean_absolute_error - (w.calibration_fitted.mean_absolute_error or 0)) < 1e-6
  assert len(set(finding_sets)) == 1


def test_family_summary_and_determinism(corpus_and_path) -> None:
  corpus, path = corpus_and_path
  freeze = load_evaluation_freeze(corpus=corpus)
  world_ids = (
    "mvp-w2-generator-v1",
    "mvp-w3-generator-high-bg-ip-v1",
  )
  a = emit_world_family(
    corpus=corpus,
    corpus_path=path,
    freeze=freeze,
    n_beneficiaries=1500,
    seed=7,
    diabetes_values=(0.18, 0.277),
    hf_values=(0.04, 0.12),
    ip_diab_values=(0.05, 0.13),
    world_ids=world_ids,
  )
  b = emit_world_family(
    corpus=corpus,
    corpus_path=path,
    freeze=freeze,
    n_beneficiaries=1500,
    seed=7,
    diabetes_values=(0.18, 0.277),
    hf_values=(0.04, 0.12),
    ip_diab_values=(0.05, 0.13),
    world_ids=world_ids,
  )
  assert a.sha256() == b.sha256()
  summary = family_summary(a)
  assert summary["family_sha256"] == a.sha256()
  assert len(summary["worlds"]) == 2
  assert summary["worlds"][0]["structural_valid"] is True
