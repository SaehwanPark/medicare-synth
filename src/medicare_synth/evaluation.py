"""Evaluation freeze for Phase 5/6: hard gates, graded metrics, holdout isolation.

Frozen before iterative packaging/fitting. Holdout and diagnostic partitions are
evaluate-only. Engines run without the agent harness. Graded evidence agreement
is not a Medicare finding.
"""

from __future__ import annotations

from enum import Enum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, model_validator

from medicare_synth.evidence_corpus import (
  EvidenceCorpus,
  PartitionName,
  default_mvp_corpus_path,
  load_corpus,
)
from medicare_synth.evidence_ir import EvidenceIRError

EVALUATION_FREEZE_SCHEMA_VERSION = "0.1"
MVP_EVALUATION_FREEZE_ID = "mvp-2021-om-ffs-diabetes-ip-eval-freeze-v1"


class EvaluationError(EvidenceIRError):
  """Recoverable evaluation configuration failure."""


class GateKind(str, Enum):
  HARD = "hard"
  GRADED = "graded"
  REPORTING_ONLY = "reporting_only"


class EvaluationGate(BaseModel):
  """One declared evaluation dimension."""

  model_config = ConfigDict(frozen=True)

  gate_id: str
  kind: GateKind
  description: str
  partition_roles: tuple[PartitionName, ...] = ()


class EvaluationFreeze(BaseModel):
  """Immutable evaluation protocol pinned before further calibration fitting."""

  model_config = ConfigDict(frozen=True)

  schema_version: str = EVALUATION_FREEZE_SCHEMA_VERSION
  freeze_id: str
  context_id: str
  corpus_id: str
  frozen: bool = True
  fit_allowed_partitions: tuple[PartitionName, ...] = (PartitionName.CALIBRATION,)
  evaluate_only_partitions: tuple[PartitionName, ...] = (
    PartitionName.HOLDOUT,
    PartitionName.DIAGNOSTIC,
  )
  excluded_partitions: tuple[PartitionName, ...] = (PartitionName.EXCLUDED,)
  calibration_finding_ids: tuple[str, ...]
  holdout_finding_ids: tuple[str, ...]
  diagnostic_finding_ids: tuple[str, ...]
  gates: tuple[EvaluationGate, ...]
  notes: tuple[str, ...] = (
    "Holdout and diagnostic findings are evaluate-only; never fit on them.",
    "Structural validity is a hard release gate; evidence MAE is graded.",
    "Synthetic agreement is not a Medicare finding.",
  )

  @model_validator(mode="after")
  def _partitions_disjoint(self) -> EvaluationFreeze:
    fit = set(self.fit_allowed_partitions)
    eval_only = set(self.evaluate_only_partitions)
    excl = set(self.excluded_partitions)
    if fit & eval_only:
      raise ValueError("fit and evaluate-only partitions must be disjoint")
    if fit & excl:
      raise ValueError("fit and excluded partitions must be disjoint")
    if PartitionName.HOLDOUT in fit:
      raise ValueError("holdout must never be fit-allowed")
    if not self.frozen:
      raise ValueError("EvaluationFreeze must be frozen=true")
    return self


def default_mvp_gates() -> tuple[EvaluationGate, ...]:
  return (
    EvaluationGate(
      gate_id="structural_validity",
      kind=GateKind.HARD,
      description=(
        "RelationalValidator passes on beneficiary, enrollment, chronic "
        "conditions, and inpatient claim linkage."
      ),
    ),
    EvaluationGate(
      gate_id="holdout_isolation",
      kind=GateKind.HARD,
      description="Fit paths refuse holdout and diagnostic finding IDs.",
      partition_roles=(PartitionName.HOLDOUT, PartitionName.DIAGNOSTIC),
    ),
    EvaluationGate(
      gate_id="calibration_mae",
      kind=GateKind.GRADED,
      description=(
        "Mean absolute error on frozen calibration moments "
        "(training diagnostic, not generalization proof)."
      ),
      partition_roles=(PartitionName.CALIBRATION,),
    ),
    EvaluationGate(
      gate_id="holdout_mae",
      kind=GateKind.REPORTING_ONLY,
      description=(
        "Holdout discrepancy may be reported for transparency; must not "
        "enter model selection or iterative retuning in Phase 5."
      ),
      partition_roles=(PartitionName.HOLDOUT,),
    ),
    EvaluationGate(
      gate_id="reweight_nondegeneracy",
      kind=GateKind.GRADED,
      description=(
        "For Level B worlds: ESS > 0, positive weights, no declared "
        "infeasibility; extreme weight collapse is a warning."
      ),
      partition_roles=(PartitionName.CALIBRATION,),
    ),
  )


def build_mvp_evaluation_freeze(corpus: EvidenceCorpus) -> EvaluationFreeze:
  """Build the pinned MVP evaluation freeze from a frozen corpus."""
  if not corpus.frozen:
    raise EvaluationError(
      "evaluation freeze requires a frozen evidence corpus"
    )
  return EvaluationFreeze(
    freeze_id=MVP_EVALUATION_FREEZE_ID,
    context_id=corpus.context_id,
    corpus_id=corpus.corpus_id,
    calibration_finding_ids=corpus.finding_ids(PartitionName.CALIBRATION),
    holdout_finding_ids=corpus.finding_ids(PartitionName.HOLDOUT),
    diagnostic_finding_ids=corpus.finding_ids(PartitionName.DIAGNOSTIC),
    gates=default_mvp_gates(),
  )


def load_evaluation_freeze(
  *,
  corpus: EvidenceCorpus | None = None,
) -> EvaluationFreeze:
  """Load the default MVP evaluation freeze (corpus from package fixtures)."""
  if corpus is None:
    corpus = load_corpus(default_mvp_corpus_path())
  return build_mvp_evaluation_freeze(corpus)


def assert_fit_roles_allowed(
  freeze: EvaluationFreeze,
  finding_ids: Sequence[str],
) -> None:
  """Refuse fit on evaluate-only or unknown IDs relative to the freeze."""
  allowed = set(freeze.calibration_finding_ids)
  holdout = set(freeze.holdout_finding_ids)
  diagnostic = set(freeze.diagnostic_finding_ids)
  for fid in finding_ids:
    if fid in holdout:
      raise EvaluationError(
        f"refusing to fit on holdout finding {fid!r} (evaluation freeze)"
      )
    if fid in diagnostic:
      raise EvaluationError(
        f"refusing to fit on diagnostic finding {fid!r} (evaluation freeze)"
      )
    if fid not in allowed:
      raise EvaluationError(
        f"finding {fid!r} is not in the frozen calibration fit set"
      )


def assert_hard_gates_documented(freeze: EvaluationFreeze) -> None:
  hard_ids = {g.gate_id for g in freeze.gates if g.kind == GateKind.HARD}
  required = {"structural_validity", "holdout_isolation"}
  missing = required - hard_ids
  if missing:
    raise EvaluationError(f"evaluation freeze missing hard gates: {sorted(missing)}")


def refuse_unfreeze(freeze: EvaluationFreeze) -> None:
  """Explicit mutation gate: unfreezing requires a human-approved new freeze."""
  raise EvaluationError(
    f"refusing to unfreeze {freeze.freeze_id!r}; register a new freeze_id "
    "after human approval of evaluation protocol changes"
  )


__all__ = [
  "EVALUATION_FREEZE_SCHEMA_VERSION",
  "MVP_EVALUATION_FREEZE_ID",
  "EvaluationError",
  "EvaluationFreeze",
  "EvaluationGate",
  "GateKind",
  "assert_fit_roles_allowed",
  "assert_hard_gates_documented",
  "build_mvp_evaluation_freeze",
  "default_mvp_gates",
  "load_evaluation_freeze",
  "refuse_unfreeze",
]
