"""Phase 5 multi-world packaging for the MVP diabetes→IP context.

Emits a small family of worlds that share frozen calibration targets and differ
in documented weak / underidentified assumptions. Holdout stays evaluate-only.
Engines run without the agent harness. Synthetic agreement is not a Medicare
finding.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

import polars as pl
from pydantic import BaseModel, ConfigDict, Field

from medicare_synth.calibration import (
  CalibrationLevel,
  CalibrationRunManifest,
  DiscrepancyReport,
  assert_calibration_partition_only,
  build_run_manifest,
  calibrate_generator_params,
  calibrate_reweight,
  discrepancy_for_findings,
  level_a_baseline,
  load_default_corpus,
  structural_valid,
)
from medicare_synth.evaluation import (
  EvaluationFreeze,
  assert_fit_roles_allowed,
  load_evaluation_freeze,
)
from medicare_synth.evidence_corpus import (
  EvidenceCorpus,
  PartitionName,
  load_partition_findings,
  sha256_file,
)
from medicare_synth.evidence_ir import EvidenceIRError
from medicare_synth.synthesis import (
  ConditionalWorld,
  ConditionalWorldParams,
  generate_diabetes_ip_world,
)

WORLDS_SCHEMA_VERSION = "0.1"
MVP_WORLD_FAMILY_ID = "mvp-2021-om-ffs-diabetes-ip-worlds-v1"


class WorldsError(EvidenceIRError):
  """Recoverable multi-world configuration or emit failure."""


class WorldMethod(str, Enum):
  REWEIGHT = "reweight"
  GENERATOR_PARAMS = "generator_params"


class WeakAssumption(BaseModel):
  """One underidentified or weakly identified modeling choice."""

  model_config = ConfigDict(frozen=True)

  assumption_id: str
  statement: str
  constrained_by_calibration: bool = False


class WorldPreset(BaseModel):
  """Versioned world recipe: shared targets, distinct weak assumptions."""

  model_config = ConfigDict(frozen=True)

  world_id: str
  label: str
  method: WorldMethod
  calibration_level: CalibrationLevel
  p_ip_given_no_diabetes: float = Field(..., ge=0.0, le=1.0)
  weak_assumptions: tuple[WeakAssumption, ...]
  notes: tuple[str, ...] = ()


class NondegeneracyReport(BaseModel):
  model_config = ConfigDict(frozen=True)

  n_beneficiaries: int
  n_with_diabetes: int
  n_with_hf: int
  n_inpatient_claims: int
  diabetes_prevalence: float
  hf_prevalence: float
  ess: float | None = None
  min_weight: float | None = None
  max_weight: float | None = None
  weight_collapsed: bool | None = None
  warnings: tuple[str, ...] = ()


class WorldRelease(BaseModel):
  """One emitted calibrated (or baseline-packaged) world with provenance."""

  model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

  schema_version: str = WORLDS_SCHEMA_VERSION
  family_id: str
  world_id: str
  label: str
  context_id: str
  corpus_id: str
  corpus_sha256: str
  evaluation_freeze_id: str
  calibration_finding_ids: tuple[str, ...]
  holdout_finding_ids: tuple[str, ...]
  method: WorldMethod
  calibration_level: CalibrationLevel
  weak_assumptions: tuple[WeakAssumption, ...]
  params: ConditionalWorldParams
  world: ConditionalWorld
  weights: pl.DataFrame | None = None
  calibration_baseline: DiscrepancyReport
  calibration_fitted: DiscrepancyReport
  holdout_report: DiscrepancyReport
  nondegeneracy: NondegeneracyReport
  structural_valid: bool
  run_manifest: CalibrationRunManifest
  limitations: tuple[str, ...]
  improved_calibration: bool

  def tables(self) -> dict[str, pl.DataFrame]:
    return self.world.tables()

  def sha256(self) -> str:
    payload = {
      "family_id": self.family_id,
      "world_id": self.world_id,
      "corpus_sha256": self.corpus_sha256,
      "evaluation_freeze_id": self.evaluation_freeze_id,
      "calibration_finding_ids": list(self.calibration_finding_ids),
      "method": self.method.value,
      "params": self.params.model_dump(mode="json"),
      "calibration_mae_before": self.calibration_baseline.mean_absolute_error,
      "calibration_mae_after": self.calibration_fitted.mean_absolute_error,
      "holdout_mae": self.holdout_report.mean_absolute_error,
      "structural_valid": self.structural_valid,
      "run_manifest_sha256": self.run_manifest.sha256(),
      "weak_assumptions": [a.model_dump(mode="json") for a in self.weak_assumptions],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class WorldFamilyRelease(BaseModel):
  """Shared-target multi-world package."""

  model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

  schema_version: str = WORLDS_SCHEMA_VERSION
  family_id: str = MVP_WORLD_FAMILY_ID
  context_id: str
  corpus_id: str
  corpus_sha256: str
  evaluation_freeze_id: str
  shared_calibration_finding_ids: tuple[str, ...]
  worlds: tuple[WorldRelease, ...]
  limitations: tuple[str, ...]

  def sha256(self) -> str:
    payload = {
      "family_id": self.family_id,
      "corpus_sha256": self.corpus_sha256,
      "evaluation_freeze_id": self.evaluation_freeze_id,
      "shared_calibration_finding_ids": list(self.shared_calibration_finding_ids),
      "world_sha256s": [w.sha256() for w in self.worlds],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _shared_weak_assumptions(
  *,
  p_ip_given_no_diabetes: float,
  method: WorldMethod,
) -> tuple[WeakAssumption, ...]:
  return (
    WeakAssumption(
      assumption_id="p_ip_given_no_diabetes_free",
      statement=(
        f"P(IP|no diabetes)={p_ip_given_no_diabetes} is not a frozen "
        "calibration target; treated as a free scenario knob."
      ),
      constrained_by_calibration=False,
    ),
    WeakAssumption(
      assumption_id="diabetes_hf_independent_bernoulli",
      statement=(
        "Generator draws diabetes and HF as independent Bernoullis; "
        "joint comorbidity structure is underidentified by the moment set."
      ),
      constrained_by_calibration=False,
    ),
    WeakAssumption(
      assumption_id="year_transport_aggregates",
      statement=(
        "CMS-AGG diabetes (2018) and HF (2022) moments are transported into "
        "the 2021 FFS context with explicit approximation grades."
      ),
      constrained_by_calibration=True,
    ),
    WeakAssumption(
      assumption_id="lit07_industry_prior",
      statement=(
        "LIT-07 P(IP|diabetes)=0.13 is a weak industry prior inside the "
        "frozen corpus, not a peer-reviewed prevalence estimand."
      ),
      constrained_by_calibration=True,
    ),
    WeakAssumption(
      assumption_id="calibration_method",
      statement=(
        f"Method={method.value}: Level B reweights existing support; "
        "Level C regenerates via discrete param search. Same targets, "
        "different underidentified residual structure."
      ),
      constrained_by_calibration=False,
    ),
  )


def mvp_world_presets() -> tuple[WorldPreset, ...]:
  """Prespecified Phase 5 family: shared targets, distinct free assumptions."""
  return (
    WorldPreset(
      world_id="mvp-w1-reweight-v1",
      label="reference_reweight",
      method=WorldMethod.REWEIGHT,
      calibration_level=CalibrationLevel.B_REWEIGHT,
      p_ip_given_no_diabetes=0.04,
      weak_assumptions=_shared_weak_assumptions(
        p_ip_given_no_diabetes=0.04, method=WorldMethod.REWEIGHT
      ),
      notes=(
        "Records unchanged; beneficiary weights absorb calibration moments.",
      ),
    ),
    WorldPreset(
      world_id="mvp-w2-generator-v1",
      label="reference_generator",
      method=WorldMethod.GENERATOR_PARAMS,
      calibration_level=CalibrationLevel.C_GENERATOR_PARAMS,
      p_ip_given_no_diabetes=0.04,
      weak_assumptions=_shared_weak_assumptions(
        p_ip_given_no_diabetes=0.04, method=WorldMethod.GENERATOR_PARAMS
      ),
      notes=("Discrete search over diabetes / HF / P(IP|diabetes).",),
    ),
    WorldPreset(
      world_id="mvp-w3-generator-high-bg-ip-v1",
      label="alt_background_ip",
      method=WorldMethod.GENERATOR_PARAMS,
      calibration_level=CalibrationLevel.C_GENERATOR_PARAMS,
      p_ip_given_no_diabetes=0.08,
      weak_assumptions=_shared_weak_assumptions(
        p_ip_given_no_diabetes=0.08, method=WorldMethod.GENERATOR_PARAMS
      ),
      notes=(
        "Same calibration targets as W2; alternate free background IP rate.",
      ),
    ),
  )


def list_mvp_world_presets() -> tuple[WorldPreset, ...]:
  return mvp_world_presets()


def get_world_preset(world_id: str) -> WorldPreset:
  for preset in mvp_world_presets():
    if preset.world_id == world_id:
      return preset
  raise WorldsError(f"unknown world_id {world_id!r}")


def default_baseline_params(
  *,
  n_beneficiaries: int = 4000,
  seed: int = 42,
  p_ip_given_no_diabetes: float = 0.04,
) -> ConditionalWorldParams:
  """Miscalibrated start used for Phase 4/5 known-truth packaging demos."""
  return ConditionalWorldParams(
    n_beneficiaries=n_beneficiaries,
    seed=seed,
    diabetes_prevalence=0.18,
    p_ip_given_diabetes=0.05,
    p_ip_given_no_diabetes=p_ip_given_no_diabetes,
    hf_prevalence=0.04,
    reference_year=2021,
  )


def _nondegeneracy(
  world: ConditionalWorld,
  *,
  weights: pl.DataFrame | None = None,
  ess: float | None = None,
  min_weight: float | None = None,
  max_weight: float | None = None,
) -> NondegeneracyReport:
  tables = world.tables()
  n = tables["beneficiary_summary"].height
  cc = tables["mbsf_chronic_conditions"]
  n_diab = int(cc.filter(pl.col("sp_diabetes").is_in(["1", "2"])).height)
  n_hf = int(cc.filter(pl.col("sp_chf").is_in(["1", "2"])).height)
  n_ip = tables["inpatient_claims"].height
  warnings: list[str] = []
  collapsed: bool | None = None
  if weights is not None and ess is not None and n > 0:
    collapsed = ess < 0.2 * float(n)
    if collapsed:
      warnings.append(
        f"ESS {ess:.1f} is below 20% of n={n}; weight concentration risk"
      )
  if n_diab == 0:
    warnings.append("zero diabetes support")
  if n_ip == 0:
    warnings.append("zero inpatient claims")
  return NondegeneracyReport(
    n_beneficiaries=n,
    n_with_diabetes=n_diab,
    n_with_hf=n_hf,
    n_inpatient_claims=n_ip,
    diabetes_prevalence=round(n_diab / n, 12) if n else 0.0,
    hf_prevalence=round(n_hf / n, 12) if n else 0.0,
    ess=None if ess is None else round(ess, 12),
    min_weight=min_weight,
    max_weight=max_weight,
    weight_collapsed=collapsed,
    warnings=tuple(warnings),
  )


_DEFAULT_LIMITATIONS: tuple[str, ...] = (
  "These are synthetic Medicare-like records for research development and "
  "stress testing—not reconstructed beneficiaries.",
  "Literature/CMS aggregate agreement provides contextual plausibility for "
  "selected moments only; do not publish synthetic estimates as Medicare "
  "findings.",
  "Multiple worlds fit the same calibration moments by design; residual "
  "structure remains underidentified.",
  "Holdout was not used for fitting; Phase 6 owns independent evaluation claims.",
)


def analyze_world_moments(
  tables: Mapping[str, pl.DataFrame],
  corpus: EvidenceCorpus,
  *,
  weights: pl.DataFrame | None = None,
  fixtures_root: Path | None = None,
) -> tuple[DiscrepancyReport, DiscrepancyReport]:
  """Identical downstream analysis across worlds: calibration + holdout MAE."""
  cal_findings = load_partition_findings(
    corpus, PartitionName.CALIBRATION, fixtures_root=fixtures_root
  )
  hold_findings = load_partition_findings(
    corpus, PartitionName.HOLDOUT, fixtures_root=fixtures_root
  )
  return (
    discrepancy_for_findings(
      tables,
      cal_findings,
      partition=PartitionName.CALIBRATION,
      weights=weights,
    ),
    discrepancy_for_findings(
      tables,
      hold_findings,
      partition=PartitionName.HOLDOUT,
      weights=weights,
    ),
  )


def emit_world(
  preset: WorldPreset,
  *,
  corpus: EvidenceCorpus | None = None,
  corpus_path: Path | None = None,
  freeze: EvaluationFreeze | None = None,
  baseline_params: ConditionalWorldParams | None = None,
  n_beneficiaries: int = 4000,
  seed: int = 42,
  diabetes_values: Sequence[float] | None = None,
  hf_values: Sequence[float] | None = None,
  ip_diab_values: Sequence[float] | None = None,
) -> WorldRelease:
  """Emit one world from a preset against the frozen corpus + evaluation freeze."""
  if corpus is None or corpus_path is None:
    corpus, corpus_path = load_default_corpus()
  freeze = freeze or load_evaluation_freeze(corpus=corpus)
  cal_ids = corpus.finding_ids(PartitionName.CALIBRATION)
  assert_calibration_partition_only(corpus, cal_ids)
  assert_fit_roles_allowed(freeze, cal_ids)
  if freeze.calibration_finding_ids != cal_ids:
    raise WorldsError(
      "evaluation freeze calibration IDs disagree with corpus partition"
    )

  base = baseline_params or default_baseline_params(
    n_beneficiaries=n_beneficiaries,
    seed=seed,
    p_ip_given_no_diabetes=preset.p_ip_given_no_diabetes,
  )
  # Ensure the free assumption from the preset is applied.
  base = base.model_copy(
    update={"p_ip_given_no_diabetes": preset.p_ip_given_no_diabetes, "seed": seed}
  )

  if preset.method == WorldMethod.REWEIGHT:
    world = generate_diabetes_ip_world(base)
    before_cal, before_hold = level_a_baseline(world.tables(), corpus)
    result = calibrate_reweight(world.tables(), corpus)
    if result.diagnostics.infeasible:
      raise WorldsError(
        f"{preset.world_id}: reweight infeasible: "
        f"{result.diagnostics.infeasibility_notes}"
      )
    _after_cal_check, after_hold = analyze_world_moments(
      world.tables(), corpus, weights=result.weights
    )
    after_cal = result.after
    if (
      _after_cal_check.mean_absolute_error is not None
      and after_cal.mean_absolute_error is not None
      and abs(_after_cal_check.mean_absolute_error - after_cal.mean_absolute_error)
      > 1e-9
    ):
      raise WorldsError(
        f"{preset.world_id}: analyze_world_moments calibration MAE disagree "
        "with reweight after-report"
      )
    nondeg = _nondegeneracy(
      world,
      weights=result.weights,
      ess=result.diagnostics.ess,
      min_weight=result.diagnostics.min_weight,
      max_weight=result.diagnostics.max_weight,
    )
    improved = (
      after_cal.mean_absolute_error is not None
      and before_cal.mean_absolute_error is not None
      and after_cal.mean_absolute_error < before_cal.mean_absolute_error
    )
    manifest = build_run_manifest(
      run_id=f"phase5-{preset.world_id}",
      level=CalibrationLevel.B_REWEIGHT,
      corpus=corpus,
      corpus_path=corpus_path,
      seed=seed,
      method_hyperparameters={
        "world_id": preset.world_id,
        "p_ip_given_no_diabetes": preset.p_ip_given_no_diabetes,
        "n_beneficiaries": base.n_beneficiaries,
      },
      diagnostics=result.diagnostics.model_dump(mode="json"),
      calibration_mae_before=before_cal.mean_absolute_error,
      calibration_mae_after=after_cal.mean_absolute_error,
      holdout_mae_before=before_hold.mean_absolute_error,
      holdout_mae_after=after_hold.mean_absolute_error,
      structural_valid_flag=structural_valid(world),
      notes=preset.notes
      + (
        "Holdout MAE reported only; not used in reweight objective.",
        f"evaluation_freeze_id={freeze.freeze_id}",
      ),
      calibration_finding_ids=cal_ids,
    )
    return WorldRelease(
      family_id=MVP_WORLD_FAMILY_ID,
      world_id=preset.world_id,
      label=preset.label,
      context_id=corpus.context_id,
      corpus_id=corpus.corpus_id,
      corpus_sha256=sha256_file(Path(corpus_path)),
      evaluation_freeze_id=freeze.freeze_id,
      calibration_finding_ids=cal_ids,
      holdout_finding_ids=corpus.finding_ids(PartitionName.HOLDOUT),
      method=preset.method,
      calibration_level=preset.calibration_level,
      weak_assumptions=preset.weak_assumptions,
      params=base,
      world=world,
      weights=result.weights,
      calibration_baseline=before_cal,
      calibration_fitted=after_cal,
      holdout_report=after_hold,
      nondegeneracy=nondeg,
      structural_valid=structural_valid(world),
      run_manifest=manifest,
      limitations=_DEFAULT_LIMITATIONS + preset.notes,
      improved_calibration=improved,
    )

  if preset.method == WorldMethod.GENERATOR_PARAMS:
    d_vals = diabetes_values or (0.18, 0.25, 0.277, 0.32)
    h_vals = hf_values or (0.04, 0.10, 0.12, 0.15)
    p_vals = ip_diab_values or (0.05, 0.10, 0.13, 0.16)
    result = calibrate_generator_params(
      base,
      corpus,
      diabetes_values=d_vals,
      hf_values=h_vals,
      ip_diab_values=p_vals,
      p_ip_given_no_diabetes=preset.p_ip_given_no_diabetes,
    )
    fitted_world = generate_diabetes_ip_world(result.fitted_params)
    after_cal, after_hold = analyze_world_moments(fitted_world.tables(), corpus)
    nondeg = _nondegeneracy(fitted_world)
    improved = result.improved_calibration
    manifest = build_run_manifest(
      run_id=f"phase5-{preset.world_id}",
      level=CalibrationLevel.C_GENERATOR_PARAMS,
      corpus=corpus,
      corpus_path=corpus_path,
      seed=seed,
      method_hyperparameters={
        "world_id": preset.world_id,
        "p_ip_given_no_diabetes": preset.p_ip_given_no_diabetes,
        "diabetes_values": list(d_vals),
        "hf_values": list(h_vals),
        "ip_diab_values": list(p_vals),
        "n_beneficiaries": base.n_beneficiaries,
      },
      diagnostics={
        "n_search_points": len(result.search_trace),
        "fitted_params": result.fitted_params.model_dump(mode="json"),
      },
      calibration_mae_before=result.baseline.mean_absolute_error,
      calibration_mae_after=result.fitted.mean_absolute_error,
      holdout_mae_before=result.holdout_baseline.mean_absolute_error,
      holdout_mae_after=result.holdout_fitted.mean_absolute_error,
      structural_valid_flag=structural_valid(fitted_world),
      notes=preset.notes
      + (
        "Holdout MAE reported only; not used in search objective.",
        f"evaluation_freeze_id={freeze.freeze_id}",
      ),
      calibration_finding_ids=cal_ids,
    )
    return WorldRelease(
      family_id=MVP_WORLD_FAMILY_ID,
      world_id=preset.world_id,
      label=preset.label,
      context_id=corpus.context_id,
      corpus_id=corpus.corpus_id,
      corpus_sha256=sha256_file(Path(corpus_path)),
      evaluation_freeze_id=freeze.freeze_id,
      calibration_finding_ids=cal_ids,
      holdout_finding_ids=corpus.finding_ids(PartitionName.HOLDOUT),
      method=preset.method,
      calibration_level=preset.calibration_level,
      weak_assumptions=preset.weak_assumptions,
      params=result.fitted_params,
      world=fitted_world,
      weights=None,
      calibration_baseline=result.baseline,
      calibration_fitted=result.fitted,
      holdout_report=after_hold,
      nondegeneracy=nondeg,
      structural_valid=structural_valid(fitted_world),
      run_manifest=manifest,
      limitations=_DEFAULT_LIMITATIONS + preset.notes,
      improved_calibration=improved,
    )

  raise WorldsError(f"unsupported method {preset.method}")


def emit_world_family(
  *,
  corpus: EvidenceCorpus | None = None,
  corpus_path: Path | None = None,
  freeze: EvaluationFreeze | None = None,
  n_beneficiaries: int = 4000,
  seed: int = 42,
  diabetes_values: Sequence[float] | None = None,
  hf_values: Sequence[float] | None = None,
  ip_diab_values: Sequence[float] | None = None,
  world_ids: Sequence[str] | None = None,
) -> WorldFamilyRelease:
  """Emit the MVP multi-world family with shared calibration targets."""
  if corpus is None or corpus_path is None:
    corpus, corpus_path = load_default_corpus()
  freeze = freeze or load_evaluation_freeze(corpus=corpus)
  presets = list_mvp_world_presets()
  if world_ids is not None:
    wanted = set(world_ids)
    presets = tuple(p for p in presets if p.world_id in wanted)
    if len(presets) != len(wanted):
      raise WorldsError(f"unknown world_ids in {sorted(wanted)}")

  releases: list[WorldRelease] = []
  shared_ids: tuple[str, ...] | None = None
  for preset in presets:
    release = emit_world(
      preset,
      corpus=corpus,
      corpus_path=corpus_path,
      freeze=freeze,
      n_beneficiaries=n_beneficiaries,
      seed=seed,
      diabetes_values=diabetes_values,
      hf_values=hf_values,
      ip_diab_values=ip_diab_values,
    )
    if not release.structural_valid:
      raise WorldsError(f"{release.world_id} failed structural validity gate")
    if shared_ids is None:
      shared_ids = release.calibration_finding_ids
    elif release.calibration_finding_ids != shared_ids:
      raise WorldsError("world family must share identical calibration finding IDs")
    releases.append(release)

  assert shared_ids is not None
  return WorldFamilyRelease(
    family_id=MVP_WORLD_FAMILY_ID,
    context_id=corpus.context_id,
    corpus_id=corpus.corpus_id,
    corpus_sha256=sha256_file(Path(corpus_path)),
    evaluation_freeze_id=freeze.freeze_id,
    shared_calibration_finding_ids=shared_ids,
    worlds=tuple(releases),
    limitations=_DEFAULT_LIMITATIONS
    + (
      "Worlds differ on calibration method and/or free P(IP|no diabetes); "
      "run the same analyze_world_moments API in each.",
    ),
  )


def family_summary(family: WorldFamilyRelease) -> dict[str, Any]:
  """JSON-serializable summary for reports (no large tables)."""
  return {
    "family_id": family.family_id,
    "family_sha256": family.sha256(),
    "context_id": family.context_id,
    "corpus_id": family.corpus_id,
    "corpus_sha256": family.corpus_sha256,
    "evaluation_freeze_id": family.evaluation_freeze_id,
    "shared_calibration_finding_ids": list(family.shared_calibration_finding_ids),
    "limitations": list(family.limitations),
    "worlds": [
      {
        "world_id": w.world_id,
        "label": w.label,
        "method": w.method.value,
        "calibration_level": w.calibration_level.value,
        "world_sha256": w.sha256(),
        "p_ip_given_no_diabetes": w.params.p_ip_given_no_diabetes,
        "params": w.params.model_dump(mode="json"),
        "calibration_mae_before": w.calibration_baseline.mean_absolute_error,
        "calibration_mae_after": w.calibration_fitted.mean_absolute_error,
        "holdout_mae": w.holdout_report.mean_absolute_error,
        "improved_calibration": w.improved_calibration,
        "structural_valid": w.structural_valid,
        "nondegeneracy": w.nondegeneracy.model_dump(mode="json"),
        "weak_assumptions": [
          a.model_dump(mode="json") for a in w.weak_assumptions
        ],
        "run_manifest_sha256": w.run_manifest.sha256(),
      }
      for w in family.worlds
    ],
  }


__all__ = [
  "MVP_WORLD_FAMILY_ID",
  "WORLDS_SCHEMA_VERSION",
  "NondegeneracyReport",
  "WeakAssumption",
  "WorldFamilyRelease",
  "WorldMethod",
  "WorldPreset",
  "WorldRelease",
  "WorldsError",
  "analyze_world_moments",
  "default_baseline_params",
  "emit_world",
  "emit_world_family",
  "family_summary",
  "get_world_preset",
  "list_mvp_world_presets",
  "mvp_world_presets",
]
