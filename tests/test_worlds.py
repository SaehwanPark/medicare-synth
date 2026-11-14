"""Behavioral tests for Phase 5 multi-world packaging."""

from __future__ import annotations

import polars as pl
import pytest

from medicare_synth.calibration import load_default_corpus
from medicare_synth.evaluation import load_evaluation_freeze
from medicare_synth.worlds import (
  MVP_WORLD_FAMILY_ID,
  WorldsError,
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
    "mvp-w1-reweight-v2",
    "mvp-w2-generator-v2",
    "mvp-w3-generator-high-bg-ip-v2",
  }
  # Distinct free background IP assumptions across generator pair.
  w2 = get_world_preset("mvp-w2-generator-v2")
  w3 = get_world_preset("mvp-w3-generator-high-bg-ip-v2")
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
  w1 = by_id["mvp-w1-reweight-v2"]
  w2 = by_id["mvp-w2-generator-v2"]
  w3 = by_id["mvp-w3-generator-high-bg-ip-v2"]

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


def test_nonconverged_reweight_is_never_packaged(
  corpus_and_path, monkeypatch: pytest.MonkeyPatch
) -> None:
  import medicare_synth.worlds as worlds
  from medicare_synth.calibration import calibrate_reweight

  corpus, path = corpus_and_path
  def one_sweep(tables, corpus):
    return calibrate_reweight(tables, corpus, max_iterations=1, tolerance=1e-6)
  def no_early_holdout(*args, **kwargs):
    raise AssertionError("holdout evaluated before successful fitting")
  monkeypatch.setattr(worlds, "calibrate_reweight", one_sweep)
  monkeypatch.setattr(worlds, "level_a_baseline", no_early_holdout)
  with pytest.raises(WorldsError, match="did not converge"):
    worlds.emit_world(worlds.get_world_preset("mvp-w1-reweight-v2"),
                      corpus=corpus, corpus_path=path, n_beneficiaries=6000, seed=42)


def test_reweight_records_require_explicit_raw_access_and_weights(family, corpus_and_path) -> None:
  corpus, _ = corpus_and_path
  w = family.worlds[0]
  with pytest.raises(WorldsError, match="raw"):
    w.tables()
  raw = w.tables(raw=True)
  assert raw["beneficiary_summary"].equals(w.world.beneficiary_summary)
  assert w.weight_key == "bene_id"
  assert w.weight_method == "iterative_proportional_fitting"
  assert w.nondegeneracy.ess is not None
  assert w.run_manifest.diagnostics["weights_sha256"]
  with pytest.raises(WorldsError, match="weights"):
    w.model_copy(update={"weights": None}).analyze(corpus)
  assert w.weights is not None
  changed_weights = w.weights.with_columns((pl.col("weight") * 2).alias("weight"))
  with pytest.raises(WorldsError, match="weight"):
    w.model_copy(update={"weights": changed_weights}).analyze(corpus)
  weighted, _ = w.analyze(corpus)
  from medicare_synth.worlds import analyze_world_moments
  unweighted, _ = analyze_world_moments(raw, corpus)
  assert weighted.rows[0].synthetic_estimate != unweighted.rows[0].synthetic_estimate


def test_identical_downstream_analysis_api(family, corpus_and_path) -> None:
  corpus, _ = corpus_and_path
  finding_sets: list[tuple[str, ...]] = []
  for w in family.worlds:
    cal, hold = w.analyze(corpus)
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
    "mvp-w2-generator-v2",
    "mvp-w3-generator-high-bg-ip-v2",
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
