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
from typing import Any, Mapping, Sequence

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
  EstimandType,
  EvidenceIRError,
  FindingIR,
  compile_finding,
)
from medicare_synth.synthesis import (
  ConditionalWorld,
  ConditionalWorldParams,
  generate_diabetes_ip_world,
)
from medicare_synth.validation import RelationalValidator

CALIBRATION_SCHEMA_VERSION = "0.1"


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

  finding_id: str
  estimand_type: EstimandType
  evidence_estimate: float
  feature: str  # diabetes | hf | ip_given_diabetes


class DiscrepancyRow(BaseModel):
  model_config = ConfigDict(frozen=True)

  finding_id: str
  evidence_estimate: float
  synthetic_estimate: float | None
  absolute_difference: float | None
  partition: PartitionName


class DiscrepancyReport(BaseModel):
  model_config = ConfigDict(frozen=True)

  rows: tuple[DiscrepancyRow, ...]
  mean_absolute_error: float | None
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
      mean_absolute_error=None if mae is None else round(mae, 12),
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
  calibration_mae: float


class ParamCalibrationResult(BaseModel):
  model_config = ConfigDict(frozen=True)

  baseline_params: ConditionalWorldParams
  fitted_params: ConditionalWorldParams
  baseline: DiscrepancyReport
  fitted: DiscrepancyReport
  holdout_baseline: DiscrepancyReport
  holdout_fitted: DiscrepancyReport
  search_trace: tuple[ParamSearchPoint, ...]
  improved_calibration: bool


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


def _ip_flag(tables: Mapping[str, pl.DataFrame]) -> pl.DataFrame:
  ip = tables["inpatient_claims"]
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


def beneficiary_feature_frame(tables: Mapping[str, pl.DataFrame]) -> pl.DataFrame:
  """One row per beneficiary with diabetes / HF / IP flags."""
  bene = tables["beneficiary_summary"].select("bene_id")
  frame = (
    bene.join(_diabetes_flag(tables), on="bene_id", how="left")
    .join(_hf_flag(tables), on="bene_id", how="left")
    .join(_ip_flag(tables), on="bene_id", how="left")
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


def moment_target_from_finding(finding: FindingIR) -> MomentTarget:
  compiled = compile_finding(finding)
  et = finding.estimand.type
  if et == EstimandType.PREVALENCE:
    concept = finding.estimand.numerator.concept.value
    if concept == "diabetes":
      feature = "diabetes"
    elif concept == "heart_failure":
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
  if not compiled.compatibility.executable:
    raise CalibrationError(
      f"{finding.finding_id} is not executable for calibration moments"
    )
  return MomentTarget(
    finding_id=finding.finding_id,
    estimand_type=et,
    evidence_estimate=finding.result.estimate,
    feature=feature,
  )


def _uniform_weights(frame: pl.DataFrame) -> pl.DataFrame:
  n = frame.height
  if n == 0:
    raise CalibrationError("empty beneficiary frame")
  return frame.select("bene_id").with_columns(pl.lit(1.0).alias("weight"))


def discrepancy_for_findings(
  tables: Mapping[str, pl.DataFrame],
  findings: Sequence[FindingIR],
  *,
  partition: PartitionName,
  weights: pl.DataFrame | None = None,
) -> DiscrepancyReport:
  frame = beneficiary_feature_frame(tables)
  w = weights if weights is not None else _uniform_weights(frame)
  framed = frame.join(w, on="bene_id", how="inner")
  rows: list[DiscrepancyRow] = []
  for finding in findings:
    try:
      target = moment_target_from_finding(finding)
      est = evaluate_moment(framed, target)
    except CalibrationError:
      est = None
    abs_diff = None if est is None else est - finding.result.estimate
    rows.append(
      DiscrepancyRow(
        finding_id=finding.finding_id,
        evidence_estimate=finding.result.estimate,
        synthetic_estimate=None if est is None else round(est, 12),
        absolute_difference=None if abs_diff is None else round(abs_diff, 12),
        partition=partition,
      )
    )
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
  frame = beneficiary_feature_frame(tables)
  n = frame.height
  weights = [1.0] * n
  diabetes = frame["diabetes"].to_list()
  hf = frame["hf"].to_list()
  ip = frame["ip"].to_list()
  notes: list[str] = []
  infeasible = False

  framed0 = frame.with_columns(pl.lit(1.0).alias("weight"))
  before_rows: list[DiscrepancyRow] = []
  for t in targets:
    est = evaluate_moment(framed0, t)
    abs_diff = None if est is None else est - t.evidence_estimate
    before_rows.append(
      DiscrepancyRow(
        finding_id=t.finding_id,
        evidence_estimate=t.evidence_estimate,
        synthetic_estimate=None if est is None else round(est, 12),
        absolute_difference=None if abs_diff is None else round(abs_diff, 12),
        partition=PartitionName.CALIBRATION,
      )
    )
  before_report = DiscrepancyReport.from_rows(before_rows)

  converged = False
  it = 0
  for it in range(1, max_iterations + 1):
    max_err = 0.0
    for t in targets:
      if t.feature == "diabetes":
        weights, note = _rake_binary(weights, diabetes, t.evidence_estimate)
      elif t.feature == "hf":
        weights, note = _rake_binary(weights, hf, t.evidence_estimate)
      elif t.feature == "ip_given_diabetes":
        weights, note = _rake_conditional(
          weights, diabetes, ip, t.evidence_estimate
        )
      else:
        raise CalibrationError(f"unsupported feature {t.feature}")
      if note:
        infeasible = True
        notes.append(f"{t.finding_id}: {note}")
        break
      # track error
      tmp = frame.with_columns(pl.Series("weight", weights))
      est = evaluate_moment(tmp, t)
      if est is None:
        infeasible = True
        notes.append(f"{t.finding_id}: moment undefined after rake")
        break
      max_err = max(max_err, abs(est - t.evidence_estimate))
    if infeasible:
      break
    if max_err < tolerance:
      converged = True
      break

  w_series = pl.Series("weight", weights)
  weight_frame = frame.select("bene_id").with_columns(w_series)
  framed1 = frame.join(weight_frame, on="bene_id", how="inner")
  after_rows: list[DiscrepancyRow] = []
  for t in targets:
    est = evaluate_moment(framed1, t)
    abs_diff = None if est is None else est - t.evidence_estimate
    after_rows.append(
      DiscrepancyRow(
        finding_id=t.finding_id,
        evidence_estimate=t.evidence_estimate,
        synthetic_estimate=None if est is None else round(est, 12),
        absolute_difference=None if abs_diff is None else round(abs_diff, 12),
        partition=PartitionName.CALIBRATION,
      )
    )
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
  holdout = set(corpus.finding_ids(PartitionName.HOLDOUT))
  for fid in finding_ids:
    if fid in holdout:
      raise CalibrationError(
        f"refusing to fit on holdout finding {fid!r}"
      )
    if fid not in allowed:
      raise CalibrationError(
        f"finding {fid!r} is not in the calibration partition"
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
  """Level C: discrete search over generator params; holdout not in objective."""
  cal_findings = load_partition_findings(
    corpus, PartitionName.CALIBRATION, fixtures_root=fixtures_root
  )
  hold_findings = load_partition_findings(
    corpus, PartitionName.HOLDOUT, fixtures_root=fixtures_root
  )
  # Ensure we never pass holdout ids into fit helpers.
  assert_calibration_partition_only(
    corpus, [f.finding_id for f in cal_findings]
  )

  d_vals = diabetes_values or (0.20, 0.25, 0.277, 0.30, 0.35)
  h_vals = hf_values or (0.05, 0.10, 0.12, 0.15)
  p_vals = ip_diab_values or (0.08, 0.10, 0.13, 0.16, 0.20)
  p_no = (
    baseline_params.p_ip_given_no_diabetes
    if p_ip_given_no_diabetes is None
    else p_ip_given_no_diabetes
  )

  baseline_world = generate_diabetes_ip_world(baseline_params)
  baseline_cal = discrepancy_for_findings(
    baseline_world.tables(), cal_findings, partition=PartitionName.CALIBRATION
  )
  baseline_hold = discrepancy_for_findings(
    baseline_world.tables(), hold_findings, partition=PartitionName.HOLDOUT
  )
  if baseline_cal.mean_absolute_error is None:
    raise CalibrationError("baseline calibration MAE undefined")

  best_mae = baseline_cal.mean_absolute_error
  best_params = baseline_params
  best_cal = baseline_cal
  best_hold = baseline_hold
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
    hold = discrepancy_for_findings(
      world.tables(), hold_findings, partition=PartitionName.HOLDOUT
    )
    mae = cal.mean_absolute_error
    if mae is None:
      continue
    trace.append(
      ParamSearchPoint(
        diabetes_prevalence=d,
        hf_prevalence=h,
        p_ip_given_diabetes=p,
        calibration_mae=round(mae, 12),
      )
    )
    if mae < best_mae - 1e-15:
      best_mae = mae
      best_params = params
      best_cal = cal
      best_hold = hold

  return ParamCalibrationResult(
    baseline_params=baseline_params,
    fitted_params=best_params,
    baseline=baseline_cal,
    fitted=best_cal,
    holdout_baseline=baseline_hold,
    holdout_fitted=best_hold,
    search_trace=tuple(trace),
    improved_calibration=best_mae < (baseline_cal.mean_absolute_error or math.inf),
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
