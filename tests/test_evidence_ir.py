"""Behavioral tests for Evidence IR v0.1 parse/validate/compile/execute."""

from __future__ import annotations

import json

import pytest

from medicare_synth.evidence_ir import (
  SCHEMA_VERSION,
  AgeSpec,
  AlgorithmId,
  ComparabilityGrade,
  ComparabilityNotes,
  ConceptId,
  EvidenceIRError,
  EvidenceRole,
  EstimateResult,
  EstimandSpec,
  EstimandType,
  FfsRule,
  FindingIR,
  PopulationSpec,
  Program,
  ReviewStatus,
  SourceRef,
  SourceType,
  VariableRef,
  compile_finding,
  draft_finding_from_fields,
  execute_finding,
  load_finding,
  package_fixtures_dir,
  parse_finding,
  validate_finding,
)
from medicare_synth.synthesis import (
  ConditionalWorldParams,
  generate_diabetes_ip_world,
)

FIXTURES = package_fixtures_dir()
LIT03 = FIXTURES / "lit03_mmwr_diabetes_prevalence_2015.json"
LIT02 = FIXTURES / "lit02_drye_admission_rate_unsupported.json"


def test_package_fixtures_exist() -> None:
  assert LIT03.is_file()
  assert LIT02.is_file()


def test_load_lit03_schema_version() -> None:
  finding = load_finding(LIT03)
  assert finding.schema_version == SCHEMA_VERSION
  assert finding.finding_id == "lit03-mmwr-diabetes-prevalence-2015"
  assert finding.inventory_id == "LIT-03"
  assert finding.result.estimate == pytest.approx(0.316)
  assert finding.governance.review_status == ReviewStatus.ACCEPTED
  assert finding.role == EvidenceRole.DIAGNOSTIC
  assert finding.source.url.startswith("https://www.cdc.gov/mmwr/")


def test_validate_accepted_requires_reviewer() -> None:
  finding = load_finding(LIT03)
  bad = finding.model_copy(
    update={
      "governance": finding.governance.model_copy(
        update={"reviewer": None, "reviewed_at": None}
      )
    }
  )
  errors = validate_finding(bad)
  assert any("reviewer" in e for e in errors)


def test_parse_rejects_rate_without_time_unit() -> None:
  raw = json.loads(LIT03.read_text(encoding="utf-8"))
  raw["estimand"] = {
    "type": "rate",
    "numerator": {
      "concept": "all_cause_inpatient",
      "algorithm": "ip_claim_presence_v1",
    },
    "scale": 100.0,
  }
  with pytest.raises(EvidenceIRError):
    parse_finding(raw)


def test_parse_rejects_wrong_schema_version() -> None:
  raw = json.loads(LIT03.read_text(encoding="utf-8"))
  raw["schema_version"] = "9.9"
  with pytest.raises(EvidenceIRError):
    parse_finding(raw)


def test_compile_lit03_compatibility_gaps() -> None:
  finding = load_finding(LIT03)
  compiled = compile_finding(finding, context_year=2021)
  codes = {i.code for i in compiled.compatibility.issues}
  assert "YEAR-TRANSPORT" in codes
  assert "AGE-FLOOR" in codes
  assert "ALG-APPROX" in codes
  assert "FFS-CUSTOM" in codes
  assert compiled.compatibility.executable is True
  assert AlgorithmId.MBSF_SP_DIABETES_V1.value in str(
    compiled.compatibility.approximating_algorithms
  )
  assert compiled.eligibility.age_minimum == 68
  assert "mbsf_chronic_conditions" in compiled.compatibility.required_tables


def test_compile_lit02_refuses_planned_admission() -> None:
  finding = load_finding(LIT02)
  compiled = compile_finding(finding, context_year=2021)
  assert compiled.compatibility.executable is False
  assert any(i.code == "PLANNED-ADMISSION" for i in compiled.compatibility.errors)
  assert finding.estimand.conditioning is not None
  assert finding.estimand.conditioning.concept == ConceptId.DIABETES


def test_unplanned_only_text_does_not_trigger_planned_admission() -> None:
  finding = load_finding(LIT03)
  rate = finding.model_copy(
    update={
      "estimand": EstimandSpec(
        type=EstimandType.RATE,
        numerator=VariableRef(
          concept=ConceptId.ALL_CAUSE_IP,
          algorithm=AlgorithmId.IP_CLAIM_PRESENCE_V1,
        ),
        conditioning=VariableRef(
          concept=ConceptId.DIABETES,
          algorithm=AlgorithmId.MBSF_SP_DIABETES_V1,
        ),
        scale=100.0,
        time_unit="person_years",
        notes="Crude rate of unplanned acute admissions among diabetes.",
      ),
      "cohort": finding.cohort.model_copy(
        update={
          "exclusion_notes": None,
          "inclusion_notes": "Unplanned acute admissions only.",
        }
      ),
      "comparability": ComparabilityNotes(
        grade=ComparabilityGrade.B,
        transport_required=True,
        gaps=("year_transport",),
        assumptions=("Outcome described as unplanned; not an exclusion rule.",),
      ),
      "result": EstimateResult(estimate=40.0, unit="per_100_person_years"),
    }
  )
  compiled = compile_finding(rate, context_year=2021)
  assert not any(
    i.code == "PLANNED-ADMISSION" for i in compiled.compatibility.issues
  )
  assert compiled.compatibility.executable is True


def test_planned_admission_detected_from_exclusion_notes() -> None:
  """PLANNED-ADMISSION must not depend only on estimand.notes."""
  finding = load_finding(LIT03)
  rate = finding.model_copy(
    update={
      "estimand": EstimandSpec(
        type=EstimandType.RATE,
        numerator=VariableRef(
          concept=ConceptId.ALL_CAUSE_IP,
          algorithm=AlgorithmId.IP_CLAIM_PRESENCE_V1,
        ),
        conditioning=VariableRef(
          concept=ConceptId.DIABETES,
          algorithm=AlgorithmId.MBSF_SP_DIABETES_V1,
        ),
        scale=100.0,
        time_unit="person_years",
        notes="Crude all-cause IP rate among diabetes.",
      ),
      "cohort": finding.cohort.model_copy(
        update={
          "exclusion_notes": "Planned admissions excluded in the source study."
        }
      ),
      "result": EstimateResult(estimate=40.0, unit="per_100_person_years"),
    }
  )
  compiled = compile_finding(rate, context_year=2021)
  assert any(i.code == "PLANNED-ADMISSION" for i in compiled.compatibility.errors)


def test_executable_rate_counts_events_in_diabetes_stratum() -> None:
  finding = load_finding(LIT03)
  rate = finding.model_copy(
    update={
      "population": finding.population.model_copy(
        update={
          "years": (2021,),
          "age": AgeSpec(minimum=65),
          "ffs_rule": FfsRule.OPTION_B_FULL_YEAR,
        }
      ),
      "estimand": EstimandSpec(
        type=EstimandType.RATE,
        numerator=VariableRef(
          concept=ConceptId.ALL_CAUSE_IP,
          algorithm=AlgorithmId.IP_CLAIM_PRESENCE_V1,
        ),
        conditioning=VariableRef(
          concept=ConceptId.DIABETES,
          algorithm=AlgorithmId.MBSF_SP_DIABETES_V1,
        ),
        scale=100.0,
        time_unit="person_years",
        notes="All-cause IP claim events per 100 person-years among diabetes.",
      ),
      "cohort": finding.cohort.model_copy(
        update={"exclusion_notes": None, "inclusion_notes": None}
      ),
      "comparability": ComparabilityNotes(
        grade=ComparabilityGrade.B,
        transport_required=False,
        gaps=(),
        assumptions=(),
      ),
      "result": EstimateResult(estimate=20.0, unit="per_100_person_years"),
    }
  )
  params = ConditionalWorldParams(
    n_beneficiaries=2000,
    seed=11,
    diabetes_prevalence=0.40,
    p_ip_given_diabetes=0.25,
    p_ip_given_no_diabetes=0.05,
  )
  world = generate_diabetes_ip_world(params)
  report = execute_finding(rate, world.tables(), context_year=2021)
  assert report.executable is True
  assert report.synthetic_estimate is not None
  assert report.n_numerator is not None
  # ~25 IP events per 100 diabetes person-years under one-claim-per-bene world.
  assert report.synthetic_estimate == pytest.approx(25.0, abs=5.0)
  assert report.n_eligible > 0


def test_execute_lit03_on_synthetic_world_reproducible() -> None:
  finding = load_finding(LIT03)
  world = generate_diabetes_ip_world(
    ConditionalWorldParams(
      n_beneficiaries=5000,
      seed=42,
      diabetes_prevalence=0.316,
      p_ip_given_diabetes=0.20,
      p_ip_given_no_diabetes=0.08,
    )
  )
  tables = world.tables()
  a = execute_finding(finding, tables, context_year=2021)
  b = execute_finding(finding, tables, context_year=2021)
  assert a.executable is True
  assert a.synthetic_estimate is not None
  assert a.n_eligible > 0
  assert a.absolute_difference is not None
  assert a.model_dump() == b.model_dump()
  # Age ≥68 filter still leaves most of a 65–89 world; prevalence near target.
  assert a.synthetic_estimate == pytest.approx(0.316, abs=0.05)
  assert any("transport" in n.lower() or "2015" in n for n in a.notes)


def test_execute_refuses_draft_without_override() -> None:
  draft = draft_finding_from_fields(
    finding_id="draft-demo",
    inventory_id=None,
    source=SourceRef(
      type=SourceType.OTHER,
      identifier="demo",
      title="Demo",
      url="https://example.com",
      location="n/a",
    ),
    population=PopulationSpec(
      program=Program.ORIGINAL_MEDICARE_FFS,
      years=(2021,),
      age=AgeSpec(minimum=65),
      ffs_rule=FfsRule.OPTION_B_FULL_YEAR,
    ),
    estimand=EstimandSpec(
      type=EstimandType.PREVALENCE,
      numerator=VariableRef(
        concept=ConceptId.DIABETES,
        algorithm=AlgorithmId.MBSF_SP_DIABETES_V1,
      ),
    ),
    result=EstimateResult(estimate=0.25),
    comparability=ComparabilityNotes(grade=ComparabilityGrade.UNASSESSED),
  )
  assert draft.governance.review_status == ReviewStatus.DRAFT
  world = generate_diabetes_ip_world(
    ConditionalWorldParams(
      n_beneficiaries=200,
      seed=1,
      diabetes_prevalence=0.25,
      p_ip_given_diabetes=0.1,
      p_ip_given_no_diabetes=0.05,
    )
  )
  refused = execute_finding(draft, world.tables())
  assert refused.executable is False
  assert any("review_status" in e for e in refused.errors)


def test_execute_lit02_errors_explicitly() -> None:
  finding = load_finding(LIT02)
  world = generate_diabetes_ip_world(
    ConditionalWorldParams(
      n_beneficiaries=200,
      seed=2,
      diabetes_prevalence=0.3,
      p_ip_given_diabetes=0.2,
      p_ip_given_no_diabetes=0.1,
    )
  )
  report = execute_finding(finding, world.tables())
  assert report.executable is False
  assert report.synthetic_estimate is None
  assert report.errors
  assert any("Planned-admission" in e or "planned" in e.lower() for e in report.errors)


def test_execute_missing_table_errors() -> None:
  finding = load_finding(LIT03)
  world = generate_diabetes_ip_world(
    ConditionalWorldParams(
      n_beneficiaries=100,
      seed=3,
      diabetes_prevalence=0.3,
      p_ip_given_diabetes=0.2,
      p_ip_given_no_diabetes=0.1,
    )
  )
  tables = {
    k: v
    for k, v in world.tables().items()
    if k != "mbsf_chronic_conditions"
  }
  report = execute_finding(finding, tables)
  assert report.executable is False
  assert any("missing required tables" in e for e in report.errors)


def test_prevalence_recovers_world_diabetes_when_age_matches() -> None:
  """When evidence age floor is 65, estimator tracks world prevalence."""
  finding = load_finding(LIT03)
  finding_65 = finding.model_copy(
    update={
      "population": finding.population.model_copy(
        update={
          "age": AgeSpec(minimum=65),
          "years": (2021,),
          "ffs_rule": FfsRule.OPTION_B_FULL_YEAR,
        }
      ),
      "comparability": finding.comparability.model_copy(
        update={"transport_required": False, "gaps": ()}
      ),
    }
  )
  params = ConditionalWorldParams(
    n_beneficiaries=4000,
    seed=7,
    diabetes_prevalence=0.28,
    p_ip_given_diabetes=0.15,
    p_ip_given_no_diabetes=0.07,
  )
  world = generate_diabetes_ip_world(params)
  report = execute_finding(finding_65, world.tables(), context_year=2021)
  assert report.executable is True
  assert report.synthetic_estimate == pytest.approx(
    params.diabetes_prevalence, abs=0.03
  )


def test_finding_roundtrip_dict() -> None:
  finding = load_finding(LIT03)
  again = FindingIR.model_validate(finding.model_dump(mode="json"))
  assert again == finding
