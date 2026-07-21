"""Limitations and dataset boundaries profiling module.

Generates explicit structured profiles describing structural, relational, temporal,
accounting, distributional, and inferential limitations for Medicare synthetic releases.
"""

from enum import Enum
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field


class LimitationsCategory(str, Enum):
  """Categories of synthetic data boundaries and limitations."""

  STRUCTURAL = "STRUCTURAL"
  RELATIONAL = "RELATIONAL"
  TEMPORAL = "TEMPORAL"
  ACCOUNTING = "ACCOUNTING"
  DISTRIBUTIONAL = "DISTRIBUTIONAL"
  INFERENTIAL = "INFERENTIAL"


class LimitationStatement(BaseModel):
  """Single limitation disclosure statement."""

  category: LimitationsCategory
  title: str
  description: str
  mitigation: str


class LimitationsProfile(BaseModel):
  """Structured disclosure profile capturing dataset limitations."""

  package_version: str = Field(default="0.1.0", description="Medicare-Synth software version.")
  target_schema_year: int = Field(default=2021, description="CMS CCW target schema year.")
  statements: List[LimitationStatement]

  def to_json(self) -> str:
    """Serializes profile to pretty JSON string."""
    return self.model_dump_json(indent=2)

  def save_file(self, output_path: Path) -> Path:
    """Saves profile to JSON file path."""
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(self.to_json(), encoding="utf-8")
    return out_p


class LimitationsProfiler:
  """Profiler for generating default and custom dataset limitation disclosures."""

  @classmethod
  def default_profile(cls) -> LimitationsProfile:
    """Returns the canonical limitations profile for Medicare-Synth synthetic releases."""
    statements = [
      LimitationStatement(
        category=LimitationsCategory.STRUCTURAL,
        title="Beneficiary-Year and Claim Line/Header Scope Boundary",
        description="Release baseline supports Beneficiary Summary, Carrier, Outpatient, Inpatient, PDE, SNF, HHA, DME, Hospice, and 10 MBSF segment files for 2021 schema.",
        mitigation="Verify specific file table inclusions and record counts using release manifests and fidelity profiles.",
      ),
      LimitationStatement(
        category=LimitationsCategory.RELATIONAL,
        title="Foreign Key and Co-Occurrence Integrity",
        description="Foreign key relationships (CLM_ID -> BENE_ID) are strictly preserved, but cross-provider referral graphs are uncalibrated.",
        mitigation="Use relational validation checks (REL-001) before conducting network analysis.",
      ),
      LimitationStatement(
        category=LimitationsCategory.TEMPORAL,
        title="Claim Date Sequence and Death Boundaries",
        description="CLM_FROM_DT <= CLM_THRU_DT <= BENE_DEATH_DT invariants are strictly enforced for valid scenarios.",
        mitigation="Rely on temporal validator rules (TEMP-001/002) for event ordering.",
      ),
      LimitationStatement(
        category=LimitationsCategory.ACCOUNTING,
        title="Payment & Line Item Accounting Bounds",
        description="Line-item provider payments aggregate deterministically to header amounts, but reimbursement rates reflect synthetic baseline approximations.",
        mitigation="Do not rely on synthesized financial figures for formal CMS actuarial auditing.",
      ),
      LimitationStatement(
        category=LimitationsCategory.DISTRIBUTIONAL,
        title="Synthetic Trajectory and Frequency Distribution Bounds",
        description="Synthetic features preserve marginal field values but do not guarantee multidimensional joint statistical distributions.",
        mitigation="Calibrate specific sub-populations using empirical CMS public data before econometric modeling.",
      ),
      LimitationStatement(
        category=LimitationsCategory.INFERENTIAL,
        title="Non-Causal & Non-Clinical Inferential Bounds",
        description="Synthetic data is intended for software integration, ETL testing, and determinism verification, not clinical causal inference.",
        mitigation="Explicitly label synthetic datasets as non-clinical when using in downstream evaluations.",
      ),
    ]

    return LimitationsProfile(statements=statements)
