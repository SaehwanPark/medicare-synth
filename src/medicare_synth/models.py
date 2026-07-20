"""Canonical entity and record models for contemporary Medicare synthetic data.

Provides typed Pydantic models for Beneficiary Summary, Carrier Claim Line, and Outpatient Claim Header records.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BeneficiaryRecord(BaseModel):
  """Domain record representation for a Beneficiary Summary record."""

  model_config = ConfigDict(frozen=True)

  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  bene_birth_dt: date = Field(..., description="Beneficiary Date of Birth")
  bene_death_dt: Optional[date] = Field(default=None, description="Beneficiary Date of Death")
  bene_sex_ident_cd: str = Field(..., max_length=1, description="Beneficiary Sex Identification Code")
  bene_race_cd: str = Field(..., max_length=1, description="Beneficiary Race Code")


class CarrierClaimLineRecord(BaseModel):
  """Domain record representation for a Carrier Claim line item."""

  model_config = ConfigDict(frozen=True)

  clm_id: str = Field(..., max_length=15, description="Claim Control Number")
  line_num: int = Field(..., ge=1, description="Claim Line Number")
  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  clm_from_dt: date = Field(..., description="Service Start Date")
  clm_thru_dt: date = Field(..., description="Service End Date")
  prvdr_npi: Optional[str] = Field(default=None, max_length=10, description="National Provider Identifier")
  icd_dgns_cd1: Optional[str] = Field(default=None, max_length=7, description="Primary ICD-10 Diagnosis Code")


class OutpatientClaimHeaderRecord(BaseModel):
  """Domain record representation for an Outpatient Claim header."""

  model_config = ConfigDict(frozen=True)

  clm_id: str = Field(..., max_length=15, description="Claim Control Number")
  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  clm_from_dt: date = Field(..., description="Claim Start Date")
  clm_thru_dt: date = Field(..., description="Claim Through Date")
  prvdr_npi: Optional[str] = Field(default=None, max_length=10, description="National Provider Identifier")
  icd_dgns_cd1: Optional[str] = Field(default=None, max_length=7, description="Primary ICD-10 Diagnosis Code")
