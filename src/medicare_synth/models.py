"""Canonical entity and record models for contemporary Medicare synthetic data.

Provides typed Pydantic models for Beneficiary Summary, Carrier Claim Line, and Outpatient Claim Header records.
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProvenanceStatus(str, Enum):
  """Provenance status taxonomy for tracking field and table lineage."""

  PRESERVED = "PRESERVED"
  NORMALIZED = "NORMALIZED"
  REKEYED = "REKEYED"
  DERIVED = "DERIVED"
  IMPUTED = "IMPUTED"
  SYNTHESIZED = "SYNTHESIZED"
  EXTERNALLY_CALIBRATED = "EXTERNALLY_CALIBRATED"
  SCENARIO_GENERATED = "SCENARIO_GENERATED"



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


class InpatientClaimHeaderRecord(BaseModel):
  """Domain record representation for an Inpatient Claim header."""

  model_config = ConfigDict(frozen=True)

  clm_id: str = Field(..., max_length=15, description="Claim Control Number")
  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  clm_admsn_dt: date = Field(..., description="Claim Admission Date")
  nch_bene_dschrg_dt: date = Field(..., description="Beneficiary Discharge Date")
  clm_pmt_amt: float = Field(default=0.0, ge=0.0, description="Claim Payment Amount")
  clm_utlztn_day_cnt: int = Field(default=1, ge=0, description="Utilization Day Count")
  clm_drg_cd: Optional[str] = Field(default=None, max_length=3, description="Diagnosis Related Group Code")
