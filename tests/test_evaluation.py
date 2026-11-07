"""Behavioral tests for Phase 5 evaluation freeze."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from medicare_synth.calibration import load_default_corpus
from medicare_synth.evaluation import (
  MVP_EVALUATION_FREEZE_ID,
  EvaluationError,
  EvaluationFreeze,
  GateKind,
  assert_fit_roles_allowed,
  assert_hard_gates_documented,
  load_evaluation_freeze,
  refuse_unfreeze,
)
from medicare_synth.evidence_corpus import PartitionName


@pytest.fixture(scope="module")
def corpus():
  corpus, _ = load_default_corpus()
  return corpus


def test_load_evaluation_freeze_is_frozen(corpus) -> None:
  freeze = load_evaluation_freeze(corpus=corpus)
  assert freeze.frozen is True
  assert freeze.freeze_id == MVP_EVALUATION_FREEZE_ID
  assert freeze.corpus_id == corpus.corpus_id
  assert freeze.calibration_finding_ids == corpus.finding_ids(
    PartitionName.CALIBRATION
  )
  assert freeze.holdout_finding_ids == corpus.finding_ids(PartitionName.HOLDOUT)
  assert PartitionName.HOLDOUT in freeze.evaluate_only_partitions
  assert PartitionName.HOLDOUT not in freeze.fit_allowed_partitions
  assert_hard_gates_documented(freeze)
  hard = [g for g in freeze.gates if g.kind == GateKind.HARD]
  assert {g.gate_id for g in hard} >= {
    "structural_validity",
    "holdout_isolation",
  }


def test_assert_fit_roles_refuse_holdout_and_diagnostic(corpus) -> None:
  freeze = load_evaluation_freeze(corpus=corpus)
  holdout_id = freeze.holdout_finding_ids[0]
  with pytest.raises(EvaluationError, match="holdout"):
    assert_fit_roles_allowed(freeze, [holdout_id])
  if freeze.diagnostic_finding_ids:
    diag_id = freeze.diagnostic_finding_ids[0]
    with pytest.raises(EvaluationError, match="diagnostic"):
      assert_fit_roles_allowed(freeze, [diag_id])
  assert_fit_roles_allowed(freeze, freeze.calibration_finding_ids)


def test_refuse_unfreeze(corpus) -> None:
  freeze = load_evaluation_freeze(corpus=corpus)
  with pytest.raises(EvaluationError, match="unfreeze"):
    refuse_unfreeze(freeze)


def test_cannot_construct_unfrozen_or_holdout_fit(corpus) -> None:
  freeze = load_evaluation_freeze(corpus=corpus)
  payload = freeze.model_dump(mode="json")
  payload["frozen"] = False
  with pytest.raises(ValidationError):
    EvaluationFreeze.model_validate(payload)
  payload = freeze.model_dump(mode="json")
  payload["fit_allowed_partitions"] = [
    PartitionName.CALIBRATION.value,
    PartitionName.HOLDOUT.value,
  ]
  with pytest.raises(ValidationError):
    EvaluationFreeze.model_validate(payload)
