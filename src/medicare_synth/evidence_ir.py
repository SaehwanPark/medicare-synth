"""Evidence IR v0.1: typed findings, validation, compilation, and execution.

Formalizes reviewed Medicare-only aggregates/studies as executable estimands.
Synthetic comparison results are not Medicare findings. Engines run without
the agent harness.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "0.1"

# --- Vocabulary ----------------------------------------------------------------


class SourceType(str, Enum):
  OFFICIAL_AGGREGATE = "official_aggregate"
  MEDICARE_ONLY_STUDY = "medicare_only_study"
  METHOD_GUIDANCE = "method_guidance"
  OTHER = "other"


class Program(str, Enum):
  ORIGINAL_MEDICARE_FFS = "original_medicare_ffs"
  MEDICARE_ADVANTAGE = "medicare_advantage"
  MIXED = "mixed"
  UNSPECIFIED = "unspecified"


class FfsRule(str, Enum):
  """Aligns with Phase 0 Option A/B/C language."""

  OPTION_A_ANNUAL_TOTALS = "option_a_annual_totals"
  OPTION_B_FULL_YEAR = "option_b_full_year"
  OPTION_C_MONTHLY_HMO = "option_c_monthly_hmo"
  SOURCE_CUSTOM = "source_custom"


class ConceptId(str, Enum):
  DIABETES = "diabetes"
  HEART_FAILURE = "heart_failure"
  ALL_CAUSE_IP = "all_cause_inpatient"
  ELIGIBLE_BENEFICIARIES = "eligible_beneficiaries"


class AlgorithmId(str, Enum):
  """Versioned algorithm references — not free-text guesses."""

  MBSF_SP_DIABETES_V1 = "mbsf_sp_diabetes_v1"
  MBSF_SP_CHF_V1 = "mbsf_sp_chf_v1"
  IP_CLAIM_PRESENCE_V1 = "ip_claim_presence_v1"
  CLAIMS_DIABETES_ANDES_MMWR_V1 = "claims_diabetes_andes_mmwr_v1"
  UNSUPPORTED = "unsupported"


class EstimandType(str, Enum):
  PREVALENCE = "prevalence"
  BINARY_RISK = "binary_risk"
  RATE = "rate"


class EvidenceRole(str, Enum):
  PENDING_REVIEW = "pending_review"
  CALIBRATION = "calibration"
  HOLDOUT = "holdout"
  DIAGNOSTIC = "diagnostic"
  EXCLUDED = "excluded"


class ReviewStatus(str, Enum):
  DRAFT = "draft"
  PENDING_REVIEW = "pending_review"
  ACCEPTED = "accepted"
  REJECTED = "rejected"


class ComparabilityGrade(str, Enum):
  A = "A"
  B = "B"
  C = "C"
  X = "X"
  UNASSESSED = "unassessed"


CONCEPT_VOCABULARY: Mapping[ConceptId, str] = {
  ConceptId.DIABETES: "Diabetes mellitus chronic-condition indicator",
  ConceptId.HEART_FAILURE: "Heart failure / CHF chronic-condition indicator",
  ConceptId.ALL_CAUSE_IP: "All-cause inpatient hospitalization (≥1 claim)",
  ConceptId.ELIGIBLE_BENEFICIARIES: "Denominator: eligibility-filtered beneficiaries",
}

ALGORITHM_VOCABULARY: Mapping[AlgorithmId, str] = {
  AlgorithmId.MBSF_SP_DIABETES_V1: "MBSF CC sp_diabetes in {1,2}",
  AlgorithmId.MBSF_SP_CHF_V1: "MBSF CC sp_chf in {1,2}",
  AlgorithmId.IP_CLAIM_PRESENCE_V1: "≥1 inpatient claim for beneficiary in year",
  AlgorithmId.CLAIMS_DIABETES_ANDES_MMWR_V1: (
    "Andes MMWR claims algorithm (IP/OP ICD lookback); not implemented on "
    "MVP tables — approximate via MBSF_SP_DIABETES_V1 with explicit gap"
  ),
  AlgorithmId.UNSUPPORTED: "No executable mapping on supported schema",
}


# --- Schema --------------------------------------------------------------------


class SourceRef(BaseModel):
  model_config = ConfigDict(frozen=True)

  type: SourceType
  identifier: str
  title: str
  url: str
  location: str = Field(
    ...,
    description="Table/figure/page or section anchor within the source.",
  )
  citation: str | None = None
  retrieval_date: str | None = None


class AgeSpec(BaseModel):
  model_config = ConfigDict(frozen=True)

  minimum: int = Field(..., ge=0, le=130)
  maximum: int | None = Field(default=None, ge=0, le=130)

  @model_validator(mode="after")
  def _check_bounds(self) -> AgeSpec:
    if self.maximum is not None and self.maximum < self.minimum:
      raise ValueError("age.maximum must be >= age.minimum")
    return self


class PopulationSpec(BaseModel):
  model_config = ConfigDict(frozen=True)

  program: Program
  years: tuple[int, ...] = Field(..., min_length=1)
  age: AgeSpec
  geography: str = "national"
  ffs_rule: FfsRule = FfsRule.OPTION_B_FULL_YEAR
  enrollment_notes: str | None = None


class CohortSpec(BaseModel):
  model_config = ConfigDict(frozen=True)

  index_date: str | None = None
  observation_end: str | None = None
  death_policy: str = "include_with_censor_at_death"
  inclusion_notes: str | None = None
  exclusion_notes: str | None = None


class VariableRef(BaseModel):
  model_config = ConfigDict(frozen=True)

  concept: ConceptId
  algorithm: AlgorithmId
  table: str | None = None
  field: str | None = None
  notes: str | None = None


class EstimandSpec(BaseModel):
  model_config = ConfigDict(frozen=True)

  type: EstimandType
  numerator: VariableRef
  denominator: ConceptId = ConceptId.ELIGIBLE_BENEFICIARIES
  conditioning: VariableRef | None = None
  scale: float = Field(
    default=1.0,
    gt=0.0,
    description="Multiplier for rates (e.g. 100 for per-100 person-years).",
  )
  time_unit: str | None = Field(
    default=None,
    description="Required for rate estimands (e.g. person_years).",
  )
  notes: str | None = None

  @model_validator(mode="after")
  def _rate_requires_time_unit(self) -> EstimandSpec:
    if self.type == EstimandType.RATE and not self.time_unit:
      raise ValueError("rate estimands require estimand.time_unit")
    if self.type == EstimandType.BINARY_RISK and self.conditioning is None:
      raise ValueError("binary_risk estimands require estimand.conditioning")
    return self


class AnalysisSpec(BaseModel):
  model_config = ConfigDict(frozen=True)

  stratification: tuple[str, ...] = ()
  adjustment_set: tuple[str, ...] = ()
  estimator: str = "crude_proportion"
  notes: str | None = None


class EstimateResult(BaseModel):
  model_config = ConfigDict(frozen=True)

  estimate: float
  standard_error: float | None = None
  ci_low: float | None = None
  ci_high: float | None = None
  sample_size: int | None = Field(default=None, ge=0)
  unit: str = "proportion"
  notes: str | None = None


class ComparabilityNotes(BaseModel):
  model_config = ConfigDict(frozen=True)

  grade: ComparabilityGrade = ComparabilityGrade.UNASSESSED
  assumptions: tuple[str, ...] = ()
  gaps: tuple[str, ...] = ()
  transport_required: bool = False


class Governance(BaseModel):
  model_config = ConfigDict(frozen=True)

  review_status: ReviewStatus
  reviewer: str | None = None
  reviewed_at: str | None = None
  rationale: str | None = None
  conflicts: tuple[str, ...] = ()


class FindingIR(BaseModel):
  """Versioned Evidence IR finding object."""

  model_config = ConfigDict(frozen=True)

  schema_version: str = SCHEMA_VERSION
  finding_id: str
  inventory_id: str | None = None
  source: SourceRef
  population: PopulationSpec
  cohort: CohortSpec = Field(default_factory=CohortSpec)
  estimand: EstimandSpec
  analysis: AnalysisSpec = Field(default_factory=AnalysisSpec)
  result: EstimateResult
  role: EvidenceRole
  comparability: ComparabilityNotes
  governance: Governance
  context_id: str = "mvp-2021-om-ffs-diabetes-ip"

  @model_validator(mode="after")
  def _schema_version(self) -> FindingIR:
    if self.schema_version != SCHEMA_VERSION:
      raise ValueError(
        f"unsupported schema_version {self.schema_version!r}; "
        f"expected {SCHEMA_VERSION!r}"
      )
    return self


# --- Parse / validate ----------------------------------------------------------


class EvidenceIRError(ValueError):
  """Recoverable Evidence IR parse/validate/compile/execute failure."""


def parse_finding(data: Mapping[str, Any]) -> FindingIR:
  """Parse a mapping into a FindingIR (Pydantic validation)."""
  try:
    return FindingIR.model_validate(dict(data))
  except Exception as exc:  # noqa: BLE001 — surface as EvidenceIRError
    raise EvidenceIRError(f"invalid Evidence IR: {exc}") from exc


def load_finding(path: Path | str) -> FindingIR:
  """Load a FindingIR from a JSON file."""
  p = Path(path)
  try:
    raw = json.loads(p.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as exc:
    raise EvidenceIRError(f"failed to load Evidence IR from {p}: {exc}") from exc
  if not isinstance(raw, dict):
    raise EvidenceIRError(f"Evidence IR root must be an object: {p}")
  return parse_finding(raw)


def validate_finding(finding: FindingIR) -> list[str]:
  """Return semantic validation errors beyond structural schema checks."""
  errors: list[str] = []
  if finding.governance.review_status == ReviewStatus.ACCEPTED:
    if not finding.governance.reviewer:
      errors.append("accepted findings require governance.reviewer")
    if not finding.governance.reviewed_at:
      errors.append("accepted findings require governance.reviewed_at")
  if finding.role == EvidenceRole.CALIBRATION and finding.comparability.grade in {
    ComparabilityGrade.X,
    ComparabilityGrade.UNASSESSED,
  }:
    errors.append(
      "calibration role requires comparability.grade in {A,B,C}, not "
      f"{finding.comparability.grade.value}"
    )
  if finding.estimand.numerator.algorithm == AlgorithmId.UNSUPPORTED:
    errors.append("numerator algorithm is unsupported")
  if (
    finding.estimand.type == EstimandType.RATE
    and finding.estimand.time_unit not in {"person_years", "beneficiaries"}
  ):
    errors.append(
      f"unsupported rate time_unit {finding.estimand.time_unit!r}; "
      "expected person_years or beneficiaries"
    )
  return errors


def ensure_valid(finding: FindingIR) -> FindingIR:
  errors = validate_finding(finding)
  if errors:
    raise EvidenceIRError("; ".join(errors))
  return finding


# --- Compile -------------------------------------------------------------------


class CompatibilityIssue(BaseModel):
  model_config = ConfigDict(frozen=True)

  code: str
  severity: str  # error | warning | info
  message: str


class CompatibilityReport(BaseModel):
  model_config = ConfigDict(frozen=True)

  finding_id: str
  executable: bool
  issues: tuple[CompatibilityIssue, ...]
  required_tables: tuple[str, ...]
  approximating_algorithms: tuple[str, ...] = ()

  @property
  def errors(self) -> tuple[CompatibilityIssue, ...]:
    return tuple(i for i in self.issues if i.severity == "error")


class EligibilityPlan(BaseModel):
  model_config = ConfigDict(frozen=True)

  age_minimum: int
  reference_year: int
  require_full_year_ab: bool
  require_zero_hmo_months: bool
  ffs_rule: FfsRule
  notes: tuple[str, ...] = ()


class DerivationPlan(BaseModel):
  model_config = ConfigDict(frozen=True)

  numerator_concept: ConceptId
  numerator_algorithm: AlgorithmId
  conditioning_concept: ConceptId | None = None
  conditioning_algorithm: AlgorithmId | None = None
  outcome_algorithm: AlgorithmId | None = None
  steps: tuple[str, ...] = ()


class EstimatorPlan(BaseModel):
  model_config = ConfigDict(frozen=True)

  estimand_type: EstimandType
  method: str
  scale: float = 1.0
  time_unit: str | None = None


class CompiledFinding(BaseModel):
  model_config = ConfigDict(frozen=True)

  finding: FindingIR
  eligibility: EligibilityPlan
  derivation: DerivationPlan
  estimator: EstimatorPlan
  compatibility: CompatibilityReport


_ALGORITHM_TABLE_FIELDS: Mapping[AlgorithmId, tuple[str, str]] = {
  AlgorithmId.MBSF_SP_DIABETES_V1: ("mbsf_chronic_conditions", "sp_diabetes"),
  AlgorithmId.MBSF_SP_CHF_V1: ("mbsf_chronic_conditions", "sp_chf"),
  AlgorithmId.IP_CLAIM_PRESENCE_V1: ("inpatient_claims", "bene_id"),
}


def _issue(code: str, severity: str, message: str) -> CompatibilityIssue:
  return CompatibilityIssue(code=code, severity=severity, message=message)


def _resolve_executable_algorithm(
  algorithm: AlgorithmId,
) -> tuple[AlgorithmId, list[CompatibilityIssue]]:
  """Map source algorithms onto MVP-executable ones; record gaps."""
  issues: list[CompatibilityIssue] = []
  if algorithm == AlgorithmId.CLAIMS_DIABETES_ANDES_MMWR_V1:
    issues.append(
      _issue(
        "ALG-APPROX",
        "warning",
        "Source claims-diabetes algorithm approximated by "
        f"{AlgorithmId.MBSF_SP_DIABETES_V1.value} on MBSF CC flags",
      )
    )
    return AlgorithmId.MBSF_SP_DIABETES_V1, issues
  if algorithm == AlgorithmId.UNSUPPORTED:
    issues.append(
      _issue("ALG-UNSUPPORTED", "error", "Algorithm has no MVP mapping")
    )
    return algorithm, issues
  return algorithm, issues


def compile_finding(
  finding: FindingIR,
  *,
  context_year: int = 2021,
) -> CompiledFinding:
  """Compile a finding into eligibility/derivation/estimator + compatibility."""
  ensure_valid(finding)
  issues: list[CompatibilityIssue] = []
  required: set[str] = {
    "beneficiary_summary",
    "mbsf_base_enrollment",
  }
  approximating: list[str] = []

  source_years = finding.population.years
  if context_year not in source_years:
    issues.append(
      _issue(
        "YEAR-TRANSPORT",
        "warning",
        f"Evidence years {source_years} ≠ context year {context_year}; "
        "transport assumption required",
      )
    )
    if not finding.comparability.transport_required:
      issues.append(
        _issue(
          "YEAR-TRANSPORT-FLAG",
          "warning",
          "comparability.transport_required is false but years differ",
        )
      )

  if finding.population.program != Program.ORIGINAL_MEDICARE_FFS:
    issues.append(
      _issue(
        "PROGRAM",
        "error",
        f"program {finding.population.program.value} is not executable on "
        "MVP FFS tables without an explicit transport rule",
      )
    )

  if finding.population.ffs_rule == FfsRule.OPTION_C_MONTHLY_HMO:
    issues.append(
      _issue(
        "FFS-OPTION-C",
        "error",
        "Option C monthly HMO panel is not first-class on MVP worlds",
      )
    )
  elif finding.population.ffs_rule == FfsRule.SOURCE_CUSTOM:
    issues.append(
      _issue(
        "FFS-CUSTOM",
        "warning",
        "Source-custom FFS/enrollment rule approximated by Option B filters",
      )
    )

  if finding.population.age.minimum != 65:
    issues.append(
      _issue(
        "AGE-FLOOR",
        "warning",
        f"Evidence age minimum {finding.population.age.minimum} differs from "
        "MVP default 65; eligibility will use the evidence minimum",
      )
    )

  num_algo, num_issues = _resolve_executable_algorithm(
    finding.estimand.numerator.algorithm
  )
  issues.extend(num_issues)
  if num_algo != finding.estimand.numerator.algorithm:
    approximating.append(
      f"{finding.estimand.numerator.algorithm.value}->{num_algo.value}"
    )

  cond_algo: AlgorithmId | None = None
  if finding.estimand.conditioning is not None:
    cond_algo, cond_issues = _resolve_executable_algorithm(
      finding.estimand.conditioning.algorithm
    )
    issues.extend(cond_issues)
    if cond_algo != finding.estimand.conditioning.algorithm:
      approximating.append(
        f"{finding.estimand.conditioning.algorithm.value}->{cond_algo.value}"
      )

  for algo in (num_algo, cond_algo):
    if algo is None:
      continue
    if algo in _ALGORITHM_TABLE_FIELDS:
      required.add(_ALGORITHM_TABLE_FIELDS[algo][0])
    elif algo == AlgorithmId.UNSUPPORTED:
      pass
    else:
      issues.append(
        _issue(
          "ALG-UNMAPPED",
          "error",
          f"No table mapping for algorithm {algo.value}",
        )
      )

  estimator_method = "crude_proportion"
  time_unit = finding.estimand.time_unit
  if finding.estimand.type == EstimandType.PREVALENCE:
    estimator_method = "crude_proportion"
  elif finding.estimand.type == EstimandType.BINARY_RISK:
    estimator_method = "conditional_proportion"
    required.add("inpatient_claims")
  elif finding.estimand.type == EstimandType.RATE:
    estimator_method = "events_per_time"
    required.add("inpatient_claims")
    if time_unit == "person_years":
      # MVP worlds lack monthly enrollment panels for precise person-time;
      # full-year Option B implies 1.0 year per eligible survivor approximation.
      issues.append(
        _issue(
          "PERSON-TIME-APPROX",
          "warning",
          "person_years approximated as 1.0 per Option-B eligible beneficiary "
          "(no monthly censoring panel)",
        )
      )
    if "planned" in (finding.estimand.notes or "").lower():
      issues.append(
        _issue(
          "PLANNED-ADMISSION",
          "error",
          "Planned-admission exclusion is not supported without IP ICD / "
          "procedure semantics",
        )
      )

  if finding.analysis.adjustment_set:
    issues.append(
      _issue(
        "ADJUSTMENT",
        "error",
        "Adjusted estimands are not supported in Evidence IR v0.1 compiler",
      )
    )

  executable = not any(i.severity == "error" for i in issues)

  eligibility = EligibilityPlan(
    age_minimum=finding.population.age.minimum,
    reference_year=context_year,
    require_full_year_ab=finding.population.ffs_rule
    in {FfsRule.OPTION_B_FULL_YEAR, FfsRule.SOURCE_CUSTOM},
    require_zero_hmo_months=True,
    ffs_rule=finding.population.ffs_rule,
    notes=tuple(
      n
      for n in (
        finding.population.enrollment_notes,
        finding.cohort.inclusion_notes,
      )
      if n
    ),
  )

  derivation = DerivationPlan(
    numerator_concept=finding.estimand.numerator.concept,
    numerator_algorithm=num_algo,
    conditioning_concept=(
      finding.estimand.conditioning.concept
      if finding.estimand.conditioning
      else None
    ),
    conditioning_algorithm=cond_algo,
    outcome_algorithm=(
      num_algo
      if finding.estimand.type == EstimandType.BINARY_RISK
      else None
    ),
    steps=(
      "Filter beneficiaries by age and Option-B enrollment rules",
      "Join chronic-condition / claim indicators per algorithm map",
      "Compute estimand on eligible rows",
    ),
  )

  estimator = EstimatorPlan(
    estimand_type=finding.estimand.type,
    method=estimator_method,
    scale=finding.estimand.scale,
    time_unit=time_unit,
  )

  compatibility = CompatibilityReport(
    finding_id=finding.finding_id,
    executable=executable,
    issues=tuple(issues),
    required_tables=tuple(sorted(required)),
    approximating_algorithms=tuple(approximating),
  )

  return CompiledFinding(
    finding=finding,
    eligibility=eligibility,
    derivation=derivation,
    estimator=estimator,
    compatibility=compatibility,
  )


# --- Execute -------------------------------------------------------------------


class ComparisonReport(BaseModel):
  model_config = ConfigDict(frozen=True)

  finding_id: str
  evidence_estimate: float
  synthetic_estimate: float | None
  absolute_difference: float | None
  relative_difference: float | None
  n_eligible: int
  n_numerator: int | None
  executable: bool
  compatibility: CompatibilityReport
  errors: tuple[str, ...] = ()
  notes: tuple[str, ...] = ()


def _age_years(birth_col: str, year: int) -> pl.Expr:
  """Integer age at end of ``year`` using calendar-year difference (MVP)."""
  return (year - pl.col(birth_col).dt.year()).alias("age_end")


def _flag_from_algorithm(algo: AlgorithmId, tables: Mapping[str, pl.DataFrame]) -> pl.DataFrame:
  """Return DataFrame with bene_id + flag columns."""
  if algo == AlgorithmId.MBSF_SP_DIABETES_V1:
    cc = tables["mbsf_chronic_conditions"]
    return cc.select(
      "bene_id",
      (pl.col("sp_diabetes").is_in(["1", "2"])).alias("flag"),
    )
  if algo == AlgorithmId.MBSF_SP_CHF_V1:
    cc = tables["mbsf_chronic_conditions"]
    return cc.select(
      "bene_id",
      (pl.col("sp_chf").is_in(["1", "2"])).alias("flag"),
    )
  if algo == AlgorithmId.IP_CLAIM_PRESENCE_V1:
    ip = tables["inpatient_claims"]
    if ip.height == 0:
      return pl.DataFrame(
        {"bene_id": pl.Series([], dtype=pl.Utf8), "flag": pl.Series([], dtype=pl.Boolean)}
      )
    return (
      ip.select("bene_id")
      .unique()
      .with_columns(pl.lit(True).alias("flag"))
    )
  raise EvidenceIRError(f"cannot derive flag for algorithm {algo.value}")


def _eligible_bene_ids(
  tables: Mapping[str, pl.DataFrame],
  plan: EligibilityPlan,
) -> pl.DataFrame:
  bene = tables["beneficiary_summary"]
  enr = tables["mbsf_base_enrollment"]
  joined = bene.join(enr, on="bene_id", how="inner")
  age = _age_years("bene_birth_dt", plan.reference_year)
  filtered = joined.with_columns(age).filter(pl.col("age_end") >= plan.age_minimum)
  if plan.require_full_year_ab:
    filtered = filtered.filter(
      (pl.col("bene_hi_cvrage_tot_mons") == 12)
      & (pl.col("bene_smi_cvrage_tot_mons") == 12)
    )
  if plan.require_zero_hmo_months:
    hmo_cols = [
      c
      for c in ("bene_hmo_cvrage_tot_mons", "bene_ma_cvrage_tot_mons")
      if c in filtered.columns
    ]
    for col in hmo_cols:
      filtered = filtered.filter(
        pl.col(col).is_null() | (pl.col(col) == 0)
      )
  return filtered.select("bene_id").unique()


def execute_finding(
  finding: FindingIR,
  tables: Mapping[str, pl.DataFrame],
  *,
  context_year: int = 2021,
  allow_unreviewed: bool = False,
) -> ComparisonReport:
  """Execute a finding against synthetic tables; return a comparison report."""
  notes: list[str] = []
  errors: list[str] = []

  if finding.governance.review_status != ReviewStatus.ACCEPTED:
    if not allow_unreviewed:
      compiled = compile_finding(finding, context_year=context_year)
      return ComparisonReport(
        finding_id=finding.finding_id,
        evidence_estimate=finding.result.estimate,
        synthetic_estimate=None,
        absolute_difference=None,
        relative_difference=None,
        n_eligible=0,
        n_numerator=None,
        executable=False,
        compatibility=compiled.compatibility,
        errors=(
          "finding governance.review_status is "
          f"{finding.governance.review_status.value}; "
          "refusing execution (pass allow_unreviewed=True to override)",
        ),
        notes=("Unreviewed findings must not be treated as approved evidence",),
      )
    notes.append("Executed with allow_unreviewed=True; not an approved comparison")

  if finding.role == EvidenceRole.EXCLUDED:
    compiled = compile_finding(finding, context_year=context_year)
    return ComparisonReport(
      finding_id=finding.finding_id,
      evidence_estimate=finding.result.estimate,
      synthetic_estimate=None,
      absolute_difference=None,
      relative_difference=None,
      n_eligible=0,
      n_numerator=None,
      executable=False,
      compatibility=compiled.compatibility,
      errors=("finding role is excluded",),
    )

  compiled = compile_finding(finding, context_year=context_year)
  if not compiled.compatibility.executable:
    return ComparisonReport(
      finding_id=finding.finding_id,
      evidence_estimate=finding.result.estimate,
      synthetic_estimate=None,
      absolute_difference=None,
      relative_difference=None,
      n_eligible=0,
      n_numerator=None,
      executable=False,
      compatibility=compiled.compatibility,
      errors=tuple(i.message for i in compiled.compatibility.errors),
      notes=tuple(i.message for i in compiled.compatibility.issues if i.severity != "error"),
    )

  missing = [t for t in compiled.compatibility.required_tables if t not in tables]
  if missing:
    return ComparisonReport(
      finding_id=finding.finding_id,
      evidence_estimate=finding.result.estimate,
      synthetic_estimate=None,
      absolute_difference=None,
      relative_difference=None,
      n_eligible=0,
      n_numerator=None,
      executable=False,
      compatibility=compiled.compatibility,
      errors=(f"missing required tables: {', '.join(missing)}",),
    )

  eligible = _eligible_bene_ids(tables, compiled.eligibility)
  n_eligible = eligible.height
  if n_eligible == 0:
    return ComparisonReport(
      finding_id=finding.finding_id,
      evidence_estimate=finding.result.estimate,
      synthetic_estimate=None,
      absolute_difference=None,
      relative_difference=None,
      n_eligible=0,
      n_numerator=None,
      executable=False,
      compatibility=compiled.compatibility,
      errors=("eligible cohort is empty",),
      notes=tuple(notes),
    )

  try:
    if compiled.estimator.estimand_type == EstimandType.PREVALENCE:
      flags = _flag_from_algorithm(
        compiled.derivation.numerator_algorithm, tables
      )
      joined = eligible.join(flags, on="bene_id", how="left").with_columns(
        pl.col("flag").fill_null(False)
      )
      n_num = int(joined.filter(pl.col("flag")).height)
      est = n_num / float(n_eligible)
    elif compiled.estimator.estimand_type == EstimandType.BINARY_RISK:
      assert compiled.derivation.conditioning_algorithm is not None
      cond = _flag_from_algorithm(
        compiled.derivation.conditioning_algorithm, tables
      )
      out = _flag_from_algorithm(
        compiled.derivation.numerator_algorithm, tables
      )
      joined = (
        eligible.join(cond.rename({"flag": "cond"}), on="bene_id", how="left")
        .join(out.rename({"flag": "out"}), on="bene_id", how="left")
        .with_columns(
          pl.col("cond").fill_null(False),
          pl.col("out").fill_null(False),
        )
        .filter(pl.col("cond"))
      )
      n_num = int(joined.filter(pl.col("out")).height)
      denom = joined.height
      if denom == 0:
        raise EvidenceIRError("conditioning stratum is empty")
      n_eligible = denom
      est = n_num / float(denom)
    elif compiled.estimator.estimand_type == EstimandType.RATE:
      out = _flag_from_algorithm(
        compiled.derivation.numerator_algorithm, tables
      )
      # Count IP claims (events) among eligible; person-time ≈ n_eligible years.
      ip = tables["inpatient_claims"]
      events = eligible.join(ip, on="bene_id", how="inner").height
      person_time = float(n_eligible)  # 1.0 year approx under Option B
      est = compiled.estimator.scale * (events / person_time)
      n_num = events
    else:
      raise EvidenceIRError(
        f"unsupported estimand type {compiled.estimator.estimand_type}"
      )
  except EvidenceIRError as exc:
    return ComparisonReport(
      finding_id=finding.finding_id,
      evidence_estimate=finding.result.estimate,
      synthetic_estimate=None,
      absolute_difference=None,
      relative_difference=None,
      n_eligible=n_eligible,
      n_numerator=None,
      executable=False,
      compatibility=compiled.compatibility,
      errors=(str(exc),),
      notes=tuple(notes),
    )

  abs_diff = est - finding.result.estimate
  rel_diff = (
    abs_diff / finding.result.estimate
    if finding.result.estimate != 0.0
    else None
  )
  # Stable rounding for deterministic reports
  est_r = round(est, 12)
  abs_r = round(abs_diff, 12)
  rel_r = None if rel_diff is None else round(rel_diff, 12)

  for issue in compiled.compatibility.issues:
    if issue.severity != "error":
      notes.append(issue.message)

  return ComparisonReport(
    finding_id=finding.finding_id,
    evidence_estimate=finding.result.estimate,
    synthetic_estimate=est_r,
    absolute_difference=abs_r,
    relative_difference=rel_r,
    n_eligible=n_eligible,
    n_numerator=n_num,
    executable=True,
    compatibility=compiled.compatibility,
    errors=tuple(errors),
    notes=tuple(notes),
  )


# --- Optional draft extraction -------------------------------------------------


def draft_finding_from_fields(
  *,
  finding_id: str,
  inventory_id: str | None,
  source: SourceRef,
  population: PopulationSpec,
  estimand: EstimandSpec,
  result: EstimateResult,
  comparability: ComparabilityNotes,
  role: EvidenceRole = EvidenceRole.PENDING_REVIEW,
  rationale: str | None = None,
) -> FindingIR:
  """Build a draft FindingIR from structured fields (AI-assist path).

  Always returns ``review_status=draft``. Humans must accept before treating
  the finding as reviewed evidence.
  """
  return FindingIR(
    finding_id=finding_id,
    inventory_id=inventory_id,
    source=source,
    population=population,
    estimand=estimand,
    result=result,
    role=role,
    comparability=comparability,
    governance=Governance(
      review_status=ReviewStatus.DRAFT,
      rationale=rationale
      or "AI-assisted or mechanical draft; human review required",
    ),
  )


def comparison_to_dict(report: ComparisonReport) -> dict[str, Any]:
  """JSON-serializable comparison report."""
  return report.model_dump(mode="json")


def package_fixtures_dir() -> Path:
  """Return the packaged fixtures directory."""
  return Path(__file__).resolve().parent / "fixtures" / "evidence_ir"
