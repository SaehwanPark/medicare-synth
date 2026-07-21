"""Canonical entity and record models for contemporary Medicare synthetic data.

Provides typed Pydantic models for Beneficiary Summary, Carrier, Outpatient, Inpatient, PDE,
SNF, HHA, DME, Hospice, and MBSF (Base, CC, CU, Part D, OC, NDI, RA, Part C, FFS) records.
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


class PrescriptionDrugEventRecord(BaseModel):
  """Domain record representation for a Part D Prescription Drug Event (PDE)."""

  model_config = ConfigDict(frozen=True)

  pde_id: str = Field(..., max_length=15, description="Prescription Drug Event ID")
  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  srvc_dt: date = Field(..., description="Prescription Fill Date")
  prod_srvc_id: Optional[str] = Field(default=None, max_length=11, description="National Drug Code (NDC)")
  qty_dspnsd_num: float = Field(default=30.0, ge=0.0, description="Quantity Dispensed")
  days_suply_num: int = Field(default=30, ge=0, description="Days Supply")
  ptnt_pay_amt: float = Field(default=0.0, ge=0.0, description="Patient Paid Amount")
  tot_rx_cst_amt: float = Field(default=0.0, ge=0.0, description="Total Prescription Cost Amount")


class SkilledNursingFacilityClaimRecord(BaseModel):
  """Domain record representation for a Skilled Nursing Facility (SNF) Claim header."""

  model_config = ConfigDict(frozen=True)

  clm_id: str = Field(..., max_length=15, description="Claim Control Number")
  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  clm_admsn_dt: date = Field(..., description="Claim Admission Date")
  nch_bene_dschrg_dt: date = Field(..., description="Beneficiary Discharge Date")
  clm_pmt_amt: float = Field(default=0.0, ge=0.0, description="Claim Payment Amount")
  clm_utlztn_day_cnt: int = Field(default=1, ge=0, description="Utilization Day Count")
  ncvd_days_cnt: int = Field(default=0, ge=0, description="Non-Covered Days Count")


class HomeHealthAgencyClaimRecord(BaseModel):
  """Domain record representation for a Home Health Agency (HHA) Claim header."""

  model_config = ConfigDict(frozen=True)

  clm_id: str = Field(..., max_length=15, description="Claim Control Number")
  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  clm_admsn_dt: date = Field(..., description="Claim Admission Date")
  nch_bene_dschrg_dt: date = Field(..., description="Beneficiary Discharge Date")
  clm_pmt_amt: float = Field(default=0.0, ge=0.0, description="Claim Payment Amount")
  clm_utlztn_day_cnt: int = Field(default=1, ge=0, description="Utilization Day Count")
  clm_hha_lupa_ind: Optional[str] = Field(default="0", max_length=1, description="HHA Low Utilization Payment Adjustment Indicator")


class DurableMedicalEquipmentClaimRecord(BaseModel):
  """Domain record representation for a Durable Medical Equipment (DME) Claim line."""

  model_config = ConfigDict(frozen=True)

  clm_id: str = Field(..., max_length=15, description="Claim Control Number")
  line_num: int = Field(..., ge=1, description="Claim Line Number")
  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  clm_from_dt: date = Field(..., description="Claim From Date")
  clm_thru_dt: date = Field(..., description="Claim Through Date")
  clm_pmt_amt: float = Field(default=0.0, ge=0.0, description="Claim Payment Amount")
  dme_line_item_count: int = Field(default=1, ge=1, description="DME Line Item Count")
  line_cms_type_srvc_cd: Optional[str] = Field(default="P", max_length=1, description="CMS Type of Service Code")


class HospiceClaimHeaderRecord(BaseModel):
  """Domain record representation for a Hospice Claim header."""

  model_config = ConfigDict(frozen=True)

  clm_id: str = Field(..., max_length=15, description="Claim Control Number")
  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  clm_admsn_dt: date = Field(..., description="Hospice Care Admission Date")
  nch_bene_dschrg_dt: date = Field(..., description="Beneficiary Discharge Date")
  clm_pmt_amt: float = Field(default=0.0, ge=0.0, description="Claim Payment Amount")
  clm_utlztn_day_cnt: int = Field(default=1, ge=0, description="Hospice Care Days Count")
  hospice_terminal_diag_cd: Optional[str] = Field(default=None, max_length=7, description="Terminal Diagnosis ICD-10 Code")


class MBSFChronicConditionsRecord(BaseModel):
  """Domain record representation for Master Beneficiary Summary File Chronic Conditions Segment."""

  model_config = ConfigDict(frozen=True)

  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  rfrnc_yr: int = Field(default=2021, ge=2000, le=2099, description="Reference Year")
  sp_alzhmd: str = Field(default="0", max_length=1, description="Alzheimer's Disease or Related Disorders Indicator")
  sp_chf: str = Field(default="0", max_length=1, description="Heart Failure Indicator")
  sp_chrnkidn: str = Field(default="0", max_length=1, description="Chronic Kidney Disease Indicator")
  sp_cncr: str = Field(default="0", max_length=1, description="Cancer Indicator")
  sp_diabetes: str = Field(default="0", max_length=1, description="Diabetes Indicator")
  sp_ischdmt: str = Field(default="0", max_length=1, description="Ischemic Heart Disease Indicator")
  sp_strketia: str = Field(default="0", max_length=1, description="Stroke/TIA Indicator")
  val_mbsf_01: float = Field(default=0.0, ge=0.0, description="MBSF Chronic Conditions Validation Metric")


class MBSFCostAndUseRecord(BaseModel):
  """Domain record representation for Master Beneficiary Summary File Cost & Use Segment."""

  model_config = ConfigDict(frozen=True)

  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  rfrnc_yr: int = Field(default=2021, ge=2000, le=2099, description="Reference Year")
  bene_mdcr_pay_amt: float = Field(default=0.0, ge=0.0, description="Beneficiary Annual Medicare Payment Total Amount")
  bene_tot_pay_amt: float = Field(default=0.0, ge=0.0, description="Beneficiary Annual Total Payment Amount")
  bene_ip_ddctbl_amt: float = Field(default=0.0, ge=0.0, description="Beneficiary Inpatient Deductible Paid Amount")
  bene_cvrd_dys_cnt: int = Field(default=0, ge=0, description="Beneficiary Total Covered Inpatient/SNF Days Count")


class MBSFPartDRecord(BaseModel):
  """Domain record representation for Master Beneficiary Summary File Part D Characteristics Segment."""

  model_config = ConfigDict(frozen=True)

  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  rfrnc_yr: int = Field(default=2021, ge=2000, le=2099, description="Reference Year")
  ptd_cntrct_id_01: Optional[str] = Field(default="S0001", max_length=5, description="Monthly Part D Contract ID Month 01")
  ptd_pbp_id_01: Optional[str] = Field(default="001", max_length=3, description="Monthly Part D Plan Benefit Package ID Month 01")
  ptd_sgnt_cd_01: Optional[str] = Field(default="000", max_length=3, description="Monthly Part D Segment Code Month 01")
  rds_ind_01: Optional[str] = Field(default="N", max_length=1, description="Monthly Retiree Drug Subsidy Indicator Month 01")
  li_cost_shrh_grp_cd_01: Optional[str] = Field(default="00", max_length=2, description="Monthly Low Income Cost Sharing Group Code Month 01")
  bene_ptd_trcc_amt: float = Field(default=0.0, ge=0.0, description="Beneficiary Part D Total Gross Covered Drug Cost Amount")
  bene_ptd_moop_amt: float = Field(default=0.0, ge=0.0, description="Beneficiary Part D True Out-of-Pocket Cost Amount")


class MBSFBaseEnrollmentRecord(BaseModel):
  """Domain record representation for Master Beneficiary Summary File Base / Enrollment Segment."""

  model_config = ConfigDict(frozen=True)

  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  rfrnc_yr: int = Field(default=2021, ge=2000, le=2099, description="Reference Year")
  bene_hi_cvrage_tot_mons: int = Field(default=12, ge=0, le=12, description="Beneficiary Part A Total Coverage Months")
  bene_smi_cvrage_tot_mons: int = Field(default=12, ge=0, le=12, description="Beneficiary Part B Total Coverage Months")
  bene_hmo_cvrage_tot_mons: int = Field(default=0, ge=0, le=12, description="Beneficiary HMO Total Coverage Months")
  bene_ptd_cvrage_tot_mons: int = Field(default=12, ge=0, le=12, description="Beneficiary Part D Total Coverage Months")
  mdcr_entlmt_buyin_ind_01: Optional[str] = Field(default="C", max_length=1, description="Medicare Entitlement / Buy-in Indicator Month 01")
  dual_stus_cd_01: Optional[str] = Field(default="00", max_length=2, description="Dual Eligibility Status Code Month 01")
  val_mbsf_base_01: float = Field(default=0.0, ge=0.0, description="MBSF Base Enrollment Validation Metric")


class MBSFOtherChronicConditionsRecord(BaseModel):
  """Domain record representation for Master Beneficiary Summary File Other Chronic Conditions Segment."""

  model_config = ConfigDict(frozen=True)

  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  rfrnc_yr: int = Field(default=2021, ge=2000, le=2099, description="Reference Year")
  sp_arthglau: str = Field(default="0", max_length=1, description="Arthritis / Glaucoma Indicator")
  sp_asthma: str = Field(default="0", max_length=1, description="Asthma Indicator")
  sp_atrialf: str = Field(default="0", max_length=1, description="Atrial Fibrillation Indicator")
  sp_hyperl: str = Field(default="0", max_length=1, description="Hyperlipidemia Indicator")
  sp_hypert: str = Field(default="0", max_length=1, description="Hypertension Indicator")
  sp_hypot: str = Field(default="0", max_length=1, description="Hypothyroidism Indicator")
  sp_osteop: str = Field(default="0", max_length=1, description="Osteoporosis Indicator")
  val_mbsf_oc_01: float = Field(default=0.0, ge=0.0, description="MBSF Other Chronic Conditions Validation Metric")


class MBSFNDIRecord(BaseModel):
  """Domain record representation for Master Beneficiary Summary File National Death Index (NDI) Segment."""

  model_config = ConfigDict(frozen=True)

  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  rfrnc_yr: int = Field(default=2021, ge=2000, le=2099, description="Reference Year")
  ndi_match_ind: str = Field(default="0", max_length=1, description="National Death Index Match Indicator")
  ndi_diuse_cd: Optional[str] = Field(default=None, max_length=7, description="Underlying Cause of Death ICD Code")
  val_mbsf_ndi_01: float = Field(default=0.0, ge=0.0, description="MBSF NDI Validation Metric")


class MBSFRiskAdjustmentRecord(BaseModel):
  """Domain record representation for Master Beneficiary Summary File Risk Adjustment Segment."""

  model_config = ConfigDict(frozen=True)

  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  rfrnc_yr: int = Field(default=2021, ge=2000, le=2099, description="Reference Year")
  cms_hcc_risk_score: float = Field(default=1.000, ge=0.0, description="CMS-HCC Risk Score")
  rxhcc_risk_score: float = Field(default=1.000, ge=0.0, description="RxHCC Risk Score")
  payment_count: int = Field(default=12, ge=0, le=12, description="Model Payment Month Count")
  val_mbsf_ra_01: float = Field(default=0.0, ge=0.0, description="MBSF Risk Adjustment Validation Metric")


class MBSFPartCRecord(BaseModel):
  """Domain record representation for Master Beneficiary Summary File Part C / Medicare Advantage Segment."""

  model_config = ConfigDict(frozen=True)

  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  rfrnc_yr: int = Field(default=2021, ge=2000, le=2099, description="Reference Year")
  ptc_cntrct_id_01: Optional[str] = Field(default="H0001", max_length=5, description="Monthly Part C Contract ID Month 01")
  ptc_pbp_id_01: Optional[str] = Field(default="001", max_length=3, description="Monthly Part C Plan Benefit Package ID Month 01")
  ptc_plan_type_cd_01: Optional[str] = Field(default="01", max_length=2, description="Monthly Part C Plan Type Code Month 01")
  bene_ma_cvrage_tot_mons: int = Field(default=12, ge=0, le=12, description="Beneficiary Medicare Advantage Total Coverage Months")
  val_mbsf_c_01: float = Field(default=0.0, ge=0.0, description="MBSF Part C Validation Metric")


class MBSFFFSUtilizationRecord(BaseModel):
  """Domain record representation for Master Beneficiary Summary File Fee-For-Service (FFS) Utilization Segment."""

  model_config = ConfigDict(frozen=True)

  bene_id: str = Field(..., max_length=15, description="Encrypted CCW Beneficiary ID")
  rfrnc_yr: int = Field(default=2021, ge=2000, le=2099, description="Reference Year")
  ip_adm_cnt: int = Field(default=0, ge=0, description="Inpatient Admission Count")
  op_vist_cnt: int = Field(default=0, ge=0, description="Outpatient Service Visit Count")
  snf_stay_cnt: int = Field(default=0, ge=0, description="Skilled Nursing Facility Stay Count")
  car_srvc_cnt: int = Field(default=0, ge=0, description="Carrier Service Count")
  hha_vist_cnt: int = Field(default=0, ge=0, description="Home Health Agency Visit Count")
  hosp_stay_cnt: int = Field(default=0, ge=0, description="Hospice Stay Count")
  dme_srvc_cnt: int = Field(default=0, ge=0, description="Durable Medical Equipment Service Count")
  val_mbsf_ffs_01: float = Field(default=0.0, ge=0.0, description="MBSF FFS Utilization Validation Metric")
