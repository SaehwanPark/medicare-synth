"""Calibration engine: Level A/B/C against a frozen evidence corpus.

Level A — baseline discrepancy. Level B — beneficiary reweighting (IPF/raking).
Level C — generator-parameter search. Holdout findings are never fit targets.
Engines run without the agent harness. Synthetic agreement is not a Medicare
finding.
"""

from __future__ import annotations

import hashlib
import json
import math
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

import polars as pl
from pydantic import BaseModel, ConfigDict

from medicare_synth.evidence_corpus import (
  EvidenceCorpus,
  PartitionName,
  default_mvp_corpus_path,
  load_corpus,
  load_corpus_finding,
  load_partition_findings,
  sha256_file,
)
from medicare_synth.evidence_ir import (
  AlgorithmId,
  EligibilityPlan,
  EstimandType,
  EvidenceIRError,
  FindingIR,
  admissions_in_year,
  compile_finding,
  eligible_bene_ids,
  validate_analysis_tables,
)
from medicare_synth.synthesis import (
  ConditionalWorld,
  ConditionalWorldParams,
  generate_diabetes_ip_world,
)
from medicare_synth.validation import RelationalValidator

CALIBRATION_SCHEMA_VERSION = "0.2"


class CalibrationLevel(str, Enum):
  A_NONE = "A_none"
  B_REWEIGHT = "B_reweight"
  C_GENERATOR_PARAMS = "C_generator_params"


class AgentRole(str, Enum):
  DISCOVERY = "discovery"
  EXTRACTION = "extraction"
  FORMALIZATION = "formalization"
  COMPATIBILITY_REVIEWER = "compatibility_reviewer"
  CALIBRATION_OPERATOR = "calibration_operator"
  EVALUATION = "evaluation"
  RELEASE = "release"


class AgentRoleContract(BaseModel):
  """Declarative agent permissions; engines do not require agents."""

  model_config = ConfigDict(frozen=True)

  role: AgentRole
  may: tuple[str, ...]
  must_not: tuple[str, ...]
  requires_human_approval: tuple[str, ...]


AGENT_ROLE_CONTRACTS: tuple[AgentRoleContract, ...] = (
  AgentRoleContract(
    role=AgentRole.DISCOVERY,
    may=("search candidate CMS aggregates and Medicare-only literature",),
    must_not=("claim eligibility/comparability without source inspection",),
    requires_human_approval=("screening inclusion into a corpus",),
  ),
  AgentRoleContract(
    role=AgentRole.EXTRACTION,
    may=("extract estimates, uncertainty, definitions, provenance anchors",),
    must_not=("invent missing SEs, eligibility rules, or covariates",),
    requires_human_approval=("new evidence record values",),
  ),
  AgentRoleContract(
    role=AgentRole.FORMALIZATION,
    may=("propose Evidence IR and variable mappings",),
    must_not=("approve unsupported semantics or fabricate estimators",),
    requires_human_approval=("new estimand implementations",),
  ),
  AgentRoleContract(
    role=AgentRole.COMPATIBILITY_REVIEWER,
    may=("flag cohort/year/program mismatch, overlap, contradictions",),
    must_not=("quietly discard inconsistent findings",),
    requires_human_approval=("transport assumption changes",),
  ),
  AgentRoleContract(
    role=AgentRole.CALIBRATION_OPERATOR,
    may=(
      "execute approved configurations and reproducible calibration runs",
      "write run manifests and diagnostics",
    ),
    must_not=(
      "change evidence values",
      "mutate train/holdout partitions to improve metrics",
      "fit on holdout findings",
    ),
    requires_human_approval=(
      "revised calibration targets",
      "holdout partition changes",
    ),
  ),
  AgentRoleContract(
    role=AgentRole.EVALUATION,
    may=("run discrepancy and robustness reports",),
    must_not=("declare evidence match without declared thresholds",),
    requires_human_approval=("public evaluation claims",),
  ),
  AgentRoleContract(
    role=AgentRole.RELEASE,
    may=("assemble manifests and limitations reports",),
    must_not=("publish unapproved representativeness claims",),
    requires_human_approval=("public evidence-calibrated releases",),
  ),
)


class CalibrationError(EvidenceIRError):
  """Recoverable calibration configuration or execution failure."""


class MomentTarget(BaseModel):
  """One calibration moment derived from a finding."""

  model_config = ConfigDict(frozen=True)

  plan_version: Literal["1"] = "1"
  finding_id: str
  estimand_type: EstimandType
  evidence_estimate: float
  feature: str  # diabetes | hf | ip_given_diabetes
  eligibility: EligibilityPlan
  compatibility: str


class DiscrepancyRow(BaseModel):
  model_config = ConfigDict(frozen=True)

  finding_id: str
  evidence_estimate: float
  synthetic_estimate: float | None
  absolute_difference: float | None
  partition: PartitionName
  status: str = "defined"
  reason: str | None = None
  denominator_count: int | None = None
  denominator_weight: float | None = None
  tolerance: float | None = None
  compatibility: str | None = None


class DiscrepancyReport(BaseModel):
  model_config = ConfigDict(frozen=True)

  rows: tuple[DiscrepancyRow, ...]
  mean_absolute_error: float | None
  diagnostic_subset_mae: float | None = None
  n_missing: int = 0

  @staticmethod
  def from_rows(rows: Sequence[DiscrepancyRow]) -> DiscrepancyReport:
    diffs = [
      abs(r.absolute_difference)
      for r in rows
      if r.absolute_difference is not None
    ]
    missing = sum(1 for r in rows if r.synthetic_estimate is None)
    mae = (sum(diffs) / len(diffs)) if diffs else None
    return DiscrepancyReport(
      rows=tuple(rows),
      mean_absolute_error=None if mae is None or missing else round(mae, 12),
      diagnostic_subset_mae=None if mae is None else round(mae, 12),
      n_missing=missing,
    )


class ReweightDiagnostics(BaseModel):
  model_config = ConfigDict(frozen=True)

  n_beneficiaries: int
  ess: float
  min_weight: float
  max_weight: float
  sum_weights: float
  iterations: int
  converged: bool
  infeasible: bool
  infeasibility_notes: tuple[str, ...] = ()
  solve_status: str = "unknown"
  solver_tolerance: float = 1e-6
  dependence_notes: tuple[str, ...] = (
    "Calibration targets may share overlapping CCW/FFS source populations; "
    "treat discrepancies as dependent, not independent likelihood terms.",
  )


class ReweightResult(BaseModel):
  model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

  weights: pl.DataFrame  # bene_id, weight
  diagnostics: ReweightDiagnostics
  before: DiscrepancyReport
  after: DiscrepancyReport
  targets: tuple[MomentTarget, ...]


class ParamSearchPoint(BaseModel):
  model_config = ConfigDict(frozen=True)

  diabetes_prevalence: float
  hf_prevalence: float
  p_ip_given_diabetes: float
  calibration_mae: float | None
  eligible: bool
  n_missing: int = 0
  reason: str | None = None
  targets: tuple[DiscrepancyRow, ...] = ()


class ParamCalibrationResult(BaseModel):
  model_config = ConfigDict(frozen=True)

  baseline_params: ConditionalWorldParams
  fitted_params: ConditionalWorldParams
  baseline: DiscrepancyReport
  fitted: DiscrepancyReport
  corpus_id: str
  calibration_finding_ids: tuple[str, ...]
  calibration_findings_sha256: str
  search_trace: tuple[ParamSearchPoint, ...]
  improved_calibration: bool


class ParamEvaluation(BaseModel):
  model_config = ConfigDict(frozen=True)

  holdout_baseline: DiscrepancyReport
  holdout_fitted: DiscrepancyReport


class CalibrationRunManifest(BaseModel):
  """Deterministic run record for a calibration experiment."""

  model_config = ConfigDict(frozen=True)

  schema_version: str = CALIBRATION_SCHEMA_VERSION
  run_id: str
  level: CalibrationLevel
  context_id: str
  corpus_id: str
  corpus_sha256: str
  calibration_finding_ids: tuple[str, ...]
  holdout_finding_ids: tuple[str, ...]
  seed: int
  method_hyperparameters: Mapping[str, Any]
  diagnostics: Mapping[str, Any]
  calibration_mae_before: float | None
  calibration_mae_after: float | None
  holdout_mae_before: float | None = None
  holdout_mae_after: float | None = None
  structural_valid: bool | None = None
  notes: tuple[str, ...] = ()
  assumptions: tuple[str, ...] = (
    "Holdout findings are evaluation-only and must not enter the fit objective.",
    "Synthetic agreement is not a Medicare finding.",
  )

  def to_json(self) -> str:
    return self.model_dump_json(indent=2)

  def sha256(self) -> str:
    # Canonical JSON for stable checksums (sorted keys via pydantic dump).
    payload = json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# --- Feature construction ------------------------------------------------------


def _diabetes_flag(tables: Mapping[str, pl.DataFrame]) -> pl.DataFrame:
  cc = tables["mbsf_chronic_conditions"]
  return cc.select(
    "bene_id",
    (pl.col("sp_diabetes").is_in(["1", "2"])).alias("diabetes"),
  )


def _hf_flag(tables: Mapping[str, pl.DataFrame]) -> pl.DataFrame:
  cc = tables["mbsf_chronic_conditions"]
  return cc.select(
    "bene_id",
    (pl.col("sp_chf").is_in(["1", "2"])).alias("hf"),
  )


def _ip_flag(tables: Mapping[str, pl.DataFrame], reference_year: int) -> pl.DataFrame:
  ip = admissions_in_year(tables["inpatient_claims"], reference_year)
  if ip.height == 0:
    return pl.DataFrame(
      {
        "bene_id": pl.Series([], dtype=pl.Utf8),
        "ip": pl.Series([], dtype=pl.Boolean),
      }
    )
  return (
    ip.select("bene_id").unique().with_columns(pl.lit(True).alias("ip"))
  )


def beneficiary_feature_frame(
  tables: Mapping[str, pl.DataFrame], *, reference_year: int = 2021
) -> pl.DataFrame:
  """One row per beneficiary with diabetes / HF / IP flags."""
  validate_analysis_tables(
    tables,
    reference_year,
    ("beneficiary_summary", "mbsf_base_enrollment", "mbsf_chronic_conditions", "inpatient_claims"),
  )
  bene = tables["beneficiary_summary"].select("bene_id")
  frame = (
    bene.join(_diabetes_flag(tables), on="bene_id", how="left")
    .join(_hf_flag(tables), on="bene_id", how="left")
    .join(_ip_flag(tables, reference_year), on="bene_id", how="left")
    .with_columns(
      pl.col("diabetes").fill_null(False),
      pl.col("hf").fill_null(False),
      pl.col("ip").fill_null(False),
    )
  )
  return frame


def _weighted_mean(frame: pl.DataFrame, col: str, weight_col: str = "weight") -> float:
  w = frame[weight_col]
  x = frame[col].cast(pl.Float64)
  sw = float(w.sum())
  if sw <= 0.0:
    raise CalibrationError("sum of weights is non-positive")
  return float((w * x).sum()) / sw


def _weighted_conditional(
  frame: pl.DataFrame,
  outcome: str,
  cond: str,
  weight_col: str = "weight",
) -> float | None:
  sub = frame.filter(pl.col(cond))
  if sub.height == 0 or float(sub[weight_col].sum()) <= 0.0:
    return None
  return _weighted_mean(sub, outcome, weight_col)


def evaluate_moment(
  frame: pl.DataFrame,
  target: MomentTarget,
  weight_col: str = "weight",
) -> float | None:
  if target.feature == "diabetes":
    return _weighted_mean(frame, "diabetes", weight_col)
  if target.feature == "hf":
    return _weighted_mean(frame, "hf", weight_col)
  if target.feature == "ip_given_diabetes":
    return _weighted_conditional(frame, "ip", "diabetes", weight_col)
  raise CalibrationError(f"unknown moment feature {target.feature!r}")


def moment_target_from_finding(
  finding: FindingIR, *, context_year: int = 2021
) -> MomentTarget:
  compiled = compile_finding(finding, context_year=context_year)
  if not compiled.compatibility.executable:
    issues = "; ".join(f"{issue.code}: {issue.message}" for issue in compiled.compatibility.errors)
    raise CalibrationError(f"{finding.finding_id} is not executable: {issues}")
  et = finding.estimand.type
  if et == EstimandType.PREVALENCE:
    concept = finding.estimand.numerator.concept.value
    if concept == "diabetes" and compiled.derivation.numerator_algorithm == AlgorithmId.MBSF_SP_DIABETES_V1:
      feature = "diabetes"
    elif concept == "heart_failure" and compiled.derivation.numerator_algorithm == AlgorithmId.MBSF_SP_CHF_V1:
      feature = "hf"
    else:
      raise CalibrationError(
        f"unsupported prevalence concept for calibration: {concept}"
      )
  elif et == EstimandType.BINARY_RISK:
    # Expect outcome IP conditioned on diabetes (LIT-07 shape).
    if (
      finding.estimand.conditioning is None
      or finding.estimand.conditioning.concept.value != "diabetes"
      or compiled.derivation.conditioning_algorithm != AlgorithmId.MBSF_SP_DIABETES_V1
    ):
      raise CalibrationError(
        f"{finding.finding_id}: binary_risk calibration requires "
        "conditioning on diabetes"
      )
    if finding.estimand.numerator.algorithm not in {
      AlgorithmId.IP_CLAIM_PRESENCE_V1,
    }:
      raise CalibrationError(
        f"{finding.finding_id}: binary_risk calibration requires IP presence"
      )
    feature = "ip_given_diabetes"
  else:
    raise CalibrationError(
      f"{finding.finding_id}: estimand type {et.value} not supported "
      "for Phase 4 moment calibration"
    )
  return MomentTarget(
    finding_id=finding.finding_id,
    estimand_type=et,
    evidence_estimate=finding.result.estimate,
    feature=feature,
    eligibility=compiled.eligibility,
    compatibility=finding.comparability.grade.value,
  )


def _uniform_weights(frame: pl.DataFrame) -> pl.DataFrame:
  n = frame.height
  if n == 0:
    raise CalibrationError("empty beneficiary frame")
  return frame.select("bene_id").with_columns(pl.lit(1.0).alias("weight"))


def feature_frame_for_finding(
  tables: Mapping[str, pl.DataFrame],
  finding: FindingIR,
  *,
  context_year: int = 2021,
) -> pl.DataFrame:
  """Beneficiary feature rows restricted to the finding's eligible cohort.

  Aligns calibration moment evaluation with ``execute_finding`` eligibility
  (age, Option-B enrollment, optional sex codes). Empty eligibility yields an
  empty frame; callers treat the moment as missing.
  """
  compiled = compile_finding(finding, context_year=context_year)
  if not compiled.compatibility.executable:
    raise CalibrationError(
      f"{finding.finding_id} is not executable for calibration moments"
    )
  eligible = eligible_bene_ids(tables, compiled.eligibility)
  frame = beneficiary_feature_frame(tables, reference_year=context_year)
  return frame.join(eligible, on="bene_id", how="inner")


def _feature_frame_for_target(
  tables: Mapping[str, pl.DataFrame], target: MomentTarget
) -> pl.DataFrame:
  eligible = eligible_bene_ids(tables, target.eligibility)
  frame = beneficiary_feature_frame(tables, reference_year=target.eligibility.reference_year)
  return frame.join(eligible, on="bene_id", how="inner")


def validate_beneficiary_weights(frame: pl.DataFrame, weights: pl.DataFrame) -> None:
  """Require exactly one finite nonnegative weight per beneficiary."""
  if not {"bene_id", "weight"}.issubset(weights.columns):
    raise CalibrationError("weights require bene_id and weight fields")
  if weights.schema["bene_id"] != frame.schema["bene_id"]:
    raise CalibrationError("weight beneficiary key type differs from records")
  if weights["bene_id"].null_count() or weights["bene_id"].n_unique() != weights.height:
    raise CalibrationError("weights contain missing or duplicate beneficiary keys")
  if weights.height != frame.height or weights.join(
    frame.select("bene_id"), on="bene_id", how="anti"
  ).height:
    raise CalibrationError("weights must cover exactly the beneficiary records")
  if not weights.schema["weight"].is_numeric() or weights["weight"].null_count():
    raise CalibrationError("weights must be non-null numeric values")
  if weights.filter(~pl.col("weight").is_finite() | (pl.col("weight") < 0)).height:
    raise CalibrationError("weights must be finite and nonnegative")
  total = float(weights["weight"].sum()) if weights.height else 0.0
  if not math.isfinite(total) or total <= 0:
    raise CalibrationError("weights must have a finite positive total")


def _target_row(
  frame: pl.DataFrame,
  target: MomentTarget,
  partition: PartitionName,
  *,
  tolerance: float | None = None,
) -> DiscrepancyRow:
  denominator = frame.filter(pl.col("diabetes")) if target.feature == "ip_given_diabetes" else frame
  count = denominator.height
  weight_sum = float(denominator["weight"].sum()) if count else 0.0
  estimate = evaluate_moment(frame, target) if count and weight_sum > 0 else None
  residual = None if estimate is None else estimate - target.evidence_estimate
  status = "undefined" if residual is None else (
    "defined" if tolerance is None else
    "matched" if abs(residual) <= tolerance else "outside_tolerance"
  )
  return DiscrepancyRow(
    finding_id=target.finding_id,
    evidence_estimate=target.evidence_estimate,
    synthetic_estimate=None if estimate is None else round(estimate, 12),
    absolute_difference=None if residual is None else round(residual, 12),
    partition=partition,
    status=status,
    reason="empty denominator or zero denominator weight" if residual is None else None,
    denominator_count=count,
    denominator_weight=round(weight_sum, 12),
    tolerance=tolerance,
    compatibility=target.compatibility,
  )


def discrepancy_for_findings(
  tables: Mapping[str, pl.DataFrame],
  findings: Sequence[FindingIR],
  *,
  partition: PartitionName,
  weights: pl.DataFrame | None = None,
  context_year: int = 2021,
) -> DiscrepancyReport:
  """Discrepancy on each finding's **eligible** cohort (Evidence IR aligned).

  Weights (Level B) are joined after eligibility filtering. Beneficiaries
  outside a finding's eligibility do not enter that finding's moment.
  """
  full = beneficiary_feature_frame(tables, reference_year=context_year)
  w_all = weights if weights is not None else _uniform_weights(full)
  validate_beneficiary_weights(full, w_all)
  rows: list[DiscrepancyRow] = []
  for finding in findings:
    try:
      target = moment_target_from_finding(finding, context_year=context_year)
      framed = _feature_frame_for_target(tables, target)
      rows.append(_target_row(framed.join(w_all, on="bene_id", how="inner"), target, partition))
    except CalibrationError as exc:
      rows.append(DiscrepancyRow(
        finding_id=finding.finding_id,
        evidence_estimate=finding.result.estimate,
        synthetic_estimate=None,
        absolute_difference=None,
        partition=partition,
        status="unsupported",
        reason=str(exc),
        compatibility=finding.comparability.grade.value,
      ))
  return DiscrepancyReport.from_rows(rows)


def effective_sample_size(weights: pl.Series) -> float:
  w = weights.cast(pl.Float64)
  s1 = float(w.sum())
  s2 = float((w * w).sum())
  if s2 <= 0.0:
    return 0.0
  return (s1 * s1) / s2


def _rake_binary(
  weights: list[float],
  flag: Sequence[bool],
  target: float,
) -> tuple[list[float], str | None]:
  if not 0.0 <= target <= 1.0:
    return weights, f"target {target} outside [0,1]"
  mass1 = sum(w for w, f in zip(weights, flag, strict=True) if f)
  mass0 = sum(w for w, f in zip(weights, flag, strict=True) if not f)
  total = mass1 + mass0
  if total <= 0.0:
    return weights, "non-positive total weight"
  if mass1 <= 0.0 or mass0 <= 0.0:
    if (mass1 <= 0.0 and target == 0.0) or (mass0 <= 0.0 and target == 1.0):
      return weights, None
    return weights, "empty support for binary rake stratum"
  want1 = target * total
  want0 = (1.0 - target) * total
  out: list[float] = []
  for w, f in zip(weights, flag, strict=True):
    if f:
      out.append(w * (want1 / mass1))
    else:
      out.append(w * (want0 / mass0))
  return out, None


def _rake_conditional(
  weights: list[float],
  cond: Sequence[bool],
  outcome: Sequence[bool],
  target: float,
) -> tuple[list[float], str | None]:
  """Rake outcome prevalence within the conditioning stratum only."""
  if not 0.0 <= target <= 1.0:
    return weights, f"conditional target {target} outside [0,1]"
  idx = [i for i, c in enumerate(cond) if c]
  if not idx:
    return weights, "empty conditioning stratum for conditional rake"
  sub_w = [weights[i] for i in idx]
  sub_o = [outcome[i] for i in idx]
  adjusted, note = _rake_binary(sub_w, sub_o, target)
  if note:
    return weights, note
  out = list(weights)
  for i, w in zip(idx, adjusted, strict=True):
    out[i] = w
  return out, None


def reweight_beneficiaries(
  tables: Mapping[str, pl.DataFrame],
  targets: Sequence[MomentTarget],
  *,
  max_iterations: int = 40,
  tolerance: float = 1e-6,
) -> ReweightResult:
  """Level B: sequential IPF/raking to match calibration moments.

  Prefer ``calibrate_reweight`` so fit targets are corpus calibration-partition
  gated. This lower-level helper does not enforce partition membership.
  """
  if not targets:
    raise CalibrationError("reweight requires at least one moment target")
  if max_iterations < 1 or not math.isfinite(tolerance) or tolerance <= 0:
    raise CalibrationError("reweight requires positive iterations and finite positive tolerance")
  if len({t.finding_id for t in targets}) != len(targets):
    raise CalibrationError("reweight target IDs must be unique")
  years = {target.eligibility.reference_year for target in targets}
  if len(years) != 1:
    raise CalibrationError("targets must use one reference year")
  frame = beneficiary_feature_frame(tables, reference_year=next(iter(years)))
  n = frame.height
  if n == 0:
    raise CalibrationError("empty beneficiary frame")
  weights = [1.0] * n
  diabetes = frame["diabetes"].to_list()
  hf = frame["hf"].to_list()
  ip = frame["ip"].to_list()
  eligible_ids = [
    set(eligible_bene_ids(tables, t.eligibility)["bene_id"].to_list())
    for t in targets
  ]
  ids = frame["bene_id"].to_list()
  notes: list[str] = []
  infeasible = False
  failed_target: tuple[str, str] | None = None

  framed0 = frame.with_columns(pl.lit(1.0).alias("weight"))
  before_rows = [
    _target_row(
      framed0.filter(pl.col("bene_id").is_in(list(eligible))),
      t, PartitionName.CALIBRATION, tolerance=tolerance,
    )
    for t, eligible in zip(targets, eligible_ids, strict=True)
  ]
  before_report = DiscrepancyReport.from_rows(before_rows)

  converged = False
  it = 0
  for it in range(1, max_iterations + 1):
    for t, eligible in zip(targets, eligible_ids, strict=True):
      indexes = [i for i, bene_id in enumerate(ids) if bene_id in eligible]
      sub_weights = [weights[i] for i in indexes]
      if t.feature == "diabetes":
        adjusted, note = _rake_binary(
          sub_weights, [diabetes[i] for i in indexes], t.evidence_estimate
        )
      elif t.feature == "hf":
        adjusted, note = _rake_binary(
          sub_weights, [hf[i] for i in indexes], t.evidence_estimate
        )
      elif t.feature == "ip_given_diabetes":
        adjusted, note = _rake_conditional(
          sub_weights, [diabetes[i] for i in indexes],
          [ip[i] for i in indexes], t.evidence_estimate
        )
      else:
        raise CalibrationError(f"unsupported feature {t.feature}")
      for i, value in zip(indexes, adjusted, strict=True):
        weights[i] = value
      if note:
        infeasible = True
        notes.append(f"{t.finding_id}: {note}")
        failed_target = (t.finding_id, note)
        break
    if infeasible:
      break
    final_frame = frame.with_columns(pl.Series("weight", weights))
    final_rows = [
      _target_row(
        final_frame.filter(pl.col("bene_id").is_in(list(eligible))),
        t, PartitionName.CALIBRATION, tolerance=tolerance,
      )
      for t, eligible in zip(targets, eligible_ids, strict=True)
    ]
    if any(row.status == "undefined" for row in final_rows):
      infeasible = True
      notes.extend(f"{row.finding_id}: {row.reason}" for row in final_rows if row.status == "undefined")
      break
    if all(row.status == "matched" for row in final_rows):
      converged = True
      break

  w_series = pl.Series("weight", weights)
  weight_frame = frame.select("bene_id").with_columns(w_series)
  framed1 = frame.join(weight_frame, on="bene_id", how="inner")
  after_rows = [
    _target_row(
      framed1.filter(pl.col("bene_id").is_in(list(eligible))),
      t, PartitionName.CALIBRATION, tolerance=tolerance,
    )
    for t, eligible in zip(targets, eligible_ids, strict=True)
  ]
  if failed_target is not None:
    after_rows = [
      row.model_copy(update={"status": "infeasible", "reason": failed_target[1]})
      if row.finding_id == failed_target[0] else row
      for row in after_rows
    ]
  after_report = DiscrepancyReport.from_rows(after_rows)

  ess = effective_sample_size(w_series)
  diagnostics = ReweightDiagnostics(
    n_beneficiaries=n,
    ess=round(ess, 12),
    min_weight=round(float(w_series.min()), 12),  # type: ignore[arg-type]
    max_weight=round(float(w_series.max()), 12),  # type: ignore[arg-type]
    sum_weights=round(float(w_series.sum()), 12),
    iterations=it,
    converged=converged and not infeasible,
    infeasible=infeasible,
    infeasibility_notes=tuple(notes),
    solve_status="infeasible" if infeasible else "converged" if converged else "exhausted",
    solver_tolerance=tolerance,
  )
  return ReweightResult(
    weights=weight_frame,
    diagnostics=diagnostics,
    before=before_report,
    after=after_report,
    targets=tuple(targets),
  )


def assert_calibration_partition_only(
  corpus: EvidenceCorpus,
  finding_ids: Sequence[str],
) -> None:
  """Refuse any fit that includes non-calibration findings (esp. holdout)."""
  allowed = set(corpus.finding_ids(PartitionName.CALIBRATION))
  for fid in finding_ids:
    if fid not in allowed:
      raise CalibrationError(
        f"finding {fid!r} is not in the calibration partition; "
        "holdout and diagnostic findings cannot be fit"
      )


def calibration_targets_from_corpus(
  corpus: EvidenceCorpus,
  *,
  finding_ids: Sequence[str] | None = None,
  fixtures_root: Path | None = None,
) -> tuple[MomentTarget, ...]:
  ids = tuple(finding_ids) if finding_ids is not None else corpus.finding_ids(
    PartitionName.CALIBRATION
  )
  assert_calibration_partition_only(corpus, ids)
  findings = [
    load_corpus_finding(corpus, fid, fixtures_root=fixtures_root) for fid in ids
  ]
  return tuple(moment_target_from_finding(f) for f in findings)


def level_a_baseline(
  tables: Mapping[str, pl.DataFrame],
  corpus: EvidenceCorpus,
  *,
  fixtures_root: Path | None = None,
) -> tuple[DiscrepancyReport, DiscrepancyReport]:
  """Baseline discrepancy on calibration and holdout partitions."""
  cal = load_partition_findings(
    corpus, PartitionName.CALIBRATION, fixtures_root=fixtures_root
  )
  hold = load_partition_findings(
    corpus, PartitionName.HOLDOUT, fixtures_root=fixtures_root
  )
  return (
    discrepancy_for_findings(
      tables, cal, partition=PartitionName.CALIBRATION
    ),
    discrepancy_for_findings(tables, hold, partition=PartitionName.HOLDOUT),
  )


def calibrate_reweight(
  tables: Mapping[str, pl.DataFrame],
  corpus: EvidenceCorpus,
  *,
  finding_ids: Sequence[str] | None = None,
  fixtures_root: Path | None = None,
  max_iterations: int = 40,
  tolerance: float = 1e-6,
) -> ReweightResult:
  required = corpus.finding_ids(PartitionName.CALIBRATION)
  if finding_ids is not None and (
    len(finding_ids) != len(required) or set(finding_ids) != set(required)
  ):
    assert_calibration_partition_only(corpus, finding_ids)
    raise CalibrationError("reweight fit requires all approved calibration targets")
  targets = calibration_targets_from_corpus(
    corpus, finding_ids=finding_ids, fixtures_root=fixtures_root
  )
  return reweight_beneficiaries(
    tables, targets, max_iterations=max_iterations, tolerance=tolerance
  )


def _param_grid(
  *,
  diabetes_values: Sequence[float],
  hf_values: Sequence[float],
  ip_diab_values: Sequence[float],
) -> list[tuple[float, float, float]]:
  grid: list[tuple[float, float, float]] = []
  for d in diabetes_values:
    for h in hf_values:
      for p in ip_diab_values:
        grid.append((float(d), float(h), float(p)))
  return grid


def _findings_hash(findings: Sequence[FindingIR]) -> str:
  raw = json.dumps(
    [f.model_dump(mode="json") for f in findings],
    sort_keys=True, separators=(",", ":"),
  )
  return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def calibrate_generator_params(
  baseline_params: ConditionalWorldParams,
  corpus: EvidenceCorpus,
  *,
  fixtures_root: Path | None = None,
  diabetes_values: Sequence[float] | None = None,
  hf_values: Sequence[float] | None = None,
  ip_diab_values: Sequence[float] | None = None,
  p_ip_given_no_diabetes: float | None = None,
) -> ParamCalibrationResult:
  """Freeze a complete calibration-only Level C candidate; do not evaluate holdout."""
  cal_findings = load_partition_findings(
    corpus, PartitionName.CALIBRATION, fixtures_root=fixtures_root
  )
  ids = tuple(f.finding_id for f in cal_findings)
  if not ids or ids != corpus.finding_ids(PartitionName.CALIBRATION) or len(set(ids)) != len(ids):
    raise CalibrationError("calibration findings must cover the complete frozen target set")
  assert_calibration_partition_only(corpus, ids)
  target_hash = _findings_hash(cal_findings)

  d_vals = diabetes_values if diabetes_values is not None else (0.20, 0.25, 0.277, 0.30, 0.35)
  h_vals = hf_values if hf_values is not None else (0.05, 0.10, 0.12, 0.15)
  p_vals = ip_diab_values if ip_diab_values is not None else (0.08, 0.10, 0.13, 0.16, 0.20)
  if not d_vals or not h_vals or not p_vals:
    raise CalibrationError("parameter search grid must not be empty")
  p_no = (
    baseline_params.p_ip_given_no_diabetes
    if p_ip_given_no_diabetes is None
    else p_ip_given_no_diabetes
  )
  if any(not math.isfinite(v) or not 0.0 <= v <= 1.0 for v in (*d_vals, *h_vals, *p_vals, p_no)):
    raise CalibrationError("parameter search values must be finite probabilities in [0, 1]")

  baseline_world = generate_diabetes_ip_world(baseline_params)
  baseline_cal = discrepancy_for_findings(
    baseline_world.tables(), cal_findings, partition=PartitionName.CALIBRATION
  )
  best_mae = baseline_cal.mean_absolute_error
  best_params: ConditionalWorldParams | None = baseline_params if best_mae is not None else None
  best_cal: DiscrepancyReport | None = baseline_cal if best_mae is not None else None
  trace: list[ParamSearchPoint] = []

  for d, h, p in _param_grid(
    diabetes_values=d_vals, hf_values=h_vals, ip_diab_values=p_vals
  ):
    params = baseline_params.model_copy(
      update={
        "diabetes_prevalence": d,
        "hf_prevalence": h,
        "p_ip_given_diabetes": p,
        "p_ip_given_no_diabetes": p_no,
      }
    )
    world = generate_diabetes_ip_world(params)
    cal = discrepancy_for_findings(
      world.tables(), cal_findings, partition=PartitionName.CALIBRATION
    )
    mae = cal.mean_absolute_error
    trace.append(
      ParamSearchPoint(
        diabetes_prevalence=d,
        hf_prevalence=h,
        p_ip_given_diabetes=p,
        calibration_mae=mae,
        eligible=mae is not None,
        n_missing=cal.n_missing,
        reason="required target undefined or unsupported" if mae is None else None,
        targets=cal.rows,
      )
    )
    if mae is not None and (best_mae is None or mae < best_mae - 1e-15):
      best_mae = mae
      best_params = params
      best_cal = cal

  if best_params is None or best_cal is None or best_mae is None:
    raise CalibrationError("no candidate has complete calibration target coverage")
  return ParamCalibrationResult(
    baseline_params=baseline_params,
    fitted_params=best_params,
    baseline=baseline_cal,
    fitted=best_cal,
    corpus_id=corpus.corpus_id,
    calibration_finding_ids=ids,
    calibration_findings_sha256=target_hash,
    search_trace=tuple(trace),
    improved_calibration=(
      baseline_cal.mean_absolute_error is not None
      and best_mae < baseline_cal.mean_absolute_error
    ),
  )


def evaluate_frozen_params(
  result: ParamCalibrationResult,
  corpus: EvidenceCorpus,
  *,
  fixtures_root: Path | None = None,
) -> ParamEvaluation:
  """Evaluate holdout only after a complete calibration candidate is frozen."""
  if corpus.corpus_id != result.corpus_id:
    raise CalibrationError("evaluation corpus differs from frozen fit corpus")
  cal_findings = load_partition_findings(
    corpus, PartitionName.CALIBRATION, fixtures_root=fixtures_root
  )
  if (
    tuple(f.finding_id for f in cal_findings) != result.calibration_finding_ids
    or _findings_hash(cal_findings) != result.calibration_findings_sha256
  ):
    raise CalibrationError("evaluation calibration targets differ from frozen fit")
  hold_findings = load_partition_findings(
    corpus, PartitionName.HOLDOUT, fixtures_root=fixtures_root
  )
  return ParamEvaluation(
    holdout_baseline=discrepancy_for_findings(
      generate_diabetes_ip_world(result.baseline_params).tables(),
      hold_findings, partition=PartitionName.HOLDOUT,
    ),
    holdout_fitted=discrepancy_for_findings(
      generate_diabetes_ip_world(result.fitted_params).tables(),
      hold_findings, partition=PartitionName.HOLDOUT,
    ),
  )


def structural_valid(world: ConditionalWorld) -> bool:
  tables = world.tables()
  report = RelationalValidator().validate_slice(
    tables["beneficiary_summary"],
    inpatient_df=tables["inpatient_claims"],
    mbsf_cc_df=tables["mbsf_chronic_conditions"],
    mbsf_base_df=tables["mbsf_base_enrollment"],
  )
  return bool(report.is_valid)


def build_run_manifest(
  *,
  run_id: str,
  level: CalibrationLevel,
  corpus: EvidenceCorpus,
  corpus_path: Path,
  seed: int,
  method_hyperparameters: Mapping[str, Any],
  diagnostics: Mapping[str, Any],
  calibration_mae_before: float | None,
  calibration_mae_after: float | None,
  holdout_mae_before: float | None = None,
  holdout_mae_after: float | None = None,
  structural_valid_flag: bool | None = None,
  notes: Sequence[str] = (),
  calibration_finding_ids: Sequence[str] | None = None,
) -> CalibrationRunManifest:
  """Build a run manifest.

  ``calibration_finding_ids`` should list the moments actually used in the fit
  when a subset was requested; defaults to the full calibration partition.
  """
  cal_ids = (
    tuple(calibration_finding_ids)
    if calibration_finding_ids is not None
    else corpus.finding_ids(PartitionName.CALIBRATION)
  )
  if calibration_finding_ids is not None:
    assert_calibration_partition_only(corpus, cal_ids)
  return CalibrationRunManifest(
    run_id=run_id,
    level=level,
    context_id=corpus.context_id,
    corpus_id=corpus.corpus_id,
    corpus_sha256=sha256_file(Path(corpus_path)),
    calibration_finding_ids=cal_ids,
    holdout_finding_ids=corpus.finding_ids(PartitionName.HOLDOUT),
    seed=seed,
    method_hyperparameters=dict(method_hyperparameters),
    diagnostics=dict(diagnostics),
    calibration_mae_before=calibration_mae_before,
    calibration_mae_after=calibration_mae_after,
    holdout_mae_before=holdout_mae_before,
    holdout_mae_after=holdout_mae_after,
    structural_valid=structural_valid_flag,
    notes=tuple(notes),
  )


def agent_role_contract(role: AgentRole) -> AgentRoleContract:
  for contract in AGENT_ROLE_CONTRACTS:
    if contract.role == role:
      return contract
  raise CalibrationError(f"unknown agent role {role}")


def load_default_corpus() -> tuple[EvidenceCorpus, Path]:
  path = default_mvp_corpus_path()
  return load_corpus(path), path
