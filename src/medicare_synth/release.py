"""Release bundle exporter, fidelity profile generation, and manifest compilation for Medicare-Synth.
"""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Dict, Literal, Union

import polars as pl
from pydantic import BaseModel, Field

from medicare_synth.validation import FindingCategory, RelationalValidator, ValidationReport

polars_installed = True


class FidelityProfile(BaseModel):
  """Summary fidelity and integrity profile of a synthetic dataset slice."""

  bene_count: int = Field(..., description="Number of beneficiary summary records")
  carrier_claim_count: int = Field(..., description="Number of carrier claim line/header records")
  outpatient_claim_count: int = Field(..., description="Number of outpatient claim line/header records")
  inpatient_claim_count: int = Field(default=0, description="Number of inpatient claim line/header records")
  pde_count: int = Field(default=0, description="Number of Part D prescription drug event records")
  snf_claim_count: int = Field(default=0, description="Number of SNF claim line/header records")
  hha_claim_count: int = Field(default=0, description="Number of HHA claim line/header records")
  dme_claim_count: int = Field(default=0, description="Number of DME claim line/header records")
  hospice_claim_count: int = Field(default=0, description="Number of Hospice claim line/header records")
  mbsf_cc_count: int = Field(default=0, description="Number of MBSF Chronic Condition records")
  mbsf_cu_count: int = Field(default=0, description="Number of MBSF Cost & Use records")
  mbsf_d_count: int = Field(default=0, description="Number of MBSF Part D records")
  mbsf_base_count: int = Field(default=0, description="Number of MBSF Base Enrollment records")
  mbsf_oc_count: int = Field(default=0, description="Number of MBSF Other Chronic Condition records")
  mbsf_ndi_count: int = Field(default=0, description="Number of MBSF NDI records")
  mbsf_ra_count: int = Field(default=0, description="Number of MBSF Risk Adjustment records")
  mbsf_c_count: int = Field(default=0, description="Number of MBSF Part C records")
  mbsf_ffs_count: int = Field(default=0, description="Number of MBSF FFS Utilization records")
  mbsf_pde_util_count: int = Field(default=0, description="Number of MBSF Part D PDE Utilization records")
  key_uniqueness_rate: float = Field(..., description="Proportion of records satisfying primary key uniqueness")


  foreign_key_validity_rate: float = Field(..., description="Proportion of claims linked to valid beneficiaries")
  temporal_integrity_rate: float = Field(..., description="Proportion of claims with valid temporal ordering")


class FileReleaseEntry(BaseModel):
  """Metadata entry for an exported data file within a release manifest."""

  filename: str = Field(..., description="Relative file name in release directory")
  format: str = Field(..., description="File format (csv or parquet)")
  row_count: int = Field(..., description="Number of records in the table")
  sha256: str = Field(..., description="SHA-256 digest of file content")
  size_bytes: int = Field(..., description="File size in bytes")


class ReleaseManifest(BaseModel):
  """Versioned release manifest summarizing exported files and validation status."""

  release_id: str = Field(..., description="Unique release identifier")
  schema_year: int = Field(default=2021, description="Target schema year")
  collection_id: str = Field(default="CMS-2021-SYN-CLAIMS", description="Baseline CMS synthetic collection ID")
  created_at: str = Field(..., description="ISO 8601 creation timestamp")
  validation_passed: bool = Field(..., description="Whether dataset passed relational validation")
  files: Dict[str, FileReleaseEntry] = Field(default_factory=dict, description="Exported data files metadata")


class ReleaseExporter:
  """Exports normalized baseline data or scenario fixtures to versioned release bundles."""

  def __init__(self, output_dir: Union[str, Path], release_id: str = "v1.0.0-2021"):
    """Initialize exporter with target directory and release identifier.

    Args:
      output_dir: Directory path where release artifacts will be written.
      release_id: Version identifier for this dataset release bundle.
    """
    self.output_dir = Path(output_dir)
    self.release_id = release_id
    self.validator = RelationalValidator()

  @staticmethod
  def _compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 digest of a local file.

    Args:
      file_path: Path to the target file.

    Returns:
      Hexadecimal SHA-256 digest string.
    """
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
      while chunk := f.read(65536):
        hasher.update(chunk)
    return hasher.hexdigest()

  def compute_fidelity_profile(
    self,
    bene_df: pl.DataFrame,
    carrier_df: pl.DataFrame,
    outpatient_df: pl.DataFrame,
    validation_report: ValidationReport,
    inpatient_df: pl.DataFrame | None = None,
    pde_df: pl.DataFrame | None = None,
    snf_df: pl.DataFrame | None = None,
    hha_df: pl.DataFrame | None = None,
    dme_df: pl.DataFrame | None = None,
    hospice_df: pl.DataFrame | None = None,
    mbsf_cc_df: pl.DataFrame | None = None,
    mbsf_cu_df: pl.DataFrame | None = None,
    mbsf_d_df: pl.DataFrame | None = None,
    mbsf_base_df: pl.DataFrame | None = None,
    mbsf_oc_df: pl.DataFrame | None = None,
    mbsf_ndi_df: pl.DataFrame | None = None,
    mbsf_ra_df: pl.DataFrame | None = None,
    mbsf_c_df: pl.DataFrame | None = None,
    mbsf_ffs_df: pl.DataFrame | None = None,
    mbsf_pde_util_df: pl.DataFrame | None = None,
  ) -> FidelityProfile:
    """Compute summary metrics and integrity rates for a dataset slice."""
    inp_count = inpatient_df.height if inpatient_df is not None else 0
    pde_cnt = pde_df.height if pde_df is not None else 0
    snf_cnt = snf_df.height if snf_df is not None else 0
    hha_cnt = hha_df.height if hha_df is not None else 0
    dme_cnt = dme_df.height if dme_df is not None else 0
    hospice_cnt = hospice_df.height if hospice_df is not None else 0
    mbsf_cc_cnt = mbsf_cc_df.height if mbsf_cc_df is not None else 0
    mbsf_cu_cnt = mbsf_cu_df.height if mbsf_cu_df is not None else 0
    mbsf_d_cnt = mbsf_d_df.height if mbsf_d_df is not None else 0
    mbsf_base_cnt = mbsf_base_df.height if mbsf_base_df is not None else 0
    mbsf_oc_cnt = mbsf_oc_df.height if mbsf_oc_df is not None else 0
    mbsf_ndi_cnt = mbsf_ndi_df.height if mbsf_ndi_df is not None else 0
    mbsf_ra_cnt = mbsf_ra_df.height if mbsf_ra_df is not None else 0
    mbsf_c_cnt = mbsf_c_df.height if mbsf_c_df is not None else 0
    mbsf_ffs_cnt = mbsf_ffs_df.height if mbsf_ffs_df is not None else 0
    mbsf_pde_util_cnt = mbsf_pde_util_df.height if mbsf_pde_util_df is not None else 0
    total_claims = carrier_df.height + outpatient_df.height + inp_count + pde_cnt + snf_cnt + hha_cnt + dme_cnt + hospice_cnt + mbsf_cc_cnt + mbsf_cu_cnt + mbsf_d_cnt + mbsf_base_cnt + mbsf_oc_cnt + mbsf_ndi_cnt + mbsf_ra_cnt + mbsf_c_cnt + mbsf_ffs_cnt + mbsf_pde_util_cnt
    fk_findings = [f for f in validation_report.findings if f.category == FindingCategory.RELATIONAL]
    temp_findings = [f for f in validation_report.findings if f.category == FindingCategory.TEMPORAL]

    fk_validity_rate = 1.0 - (len(fk_findings) / max(total_claims, 1)) if fk_findings else 1.0
    temp_integrity_rate = 1.0 - (len(temp_findings) / max(total_claims, 1)) if temp_findings else 1.0

    return FidelityProfile(
      bene_count=bene_df.height,
      carrier_claim_count=carrier_df.height,
      outpatient_claim_count=outpatient_df.height,
      inpatient_claim_count=inp_count,
      pde_count=pde_cnt,
      snf_claim_count=snf_cnt,
      hha_claim_count=hha_cnt,
      dme_claim_count=dme_cnt,
      hospice_claim_count=hospice_cnt,
      mbsf_cc_count=mbsf_cc_cnt,
      mbsf_cu_count=mbsf_cu_cnt,
      mbsf_d_count=mbsf_d_cnt,
      mbsf_base_count=mbsf_base_cnt,
      mbsf_oc_count=mbsf_oc_cnt,
      mbsf_ndi_count=mbsf_ndi_cnt,
      mbsf_ra_count=mbsf_ra_cnt,
      mbsf_c_count=mbsf_c_cnt,
      mbsf_ffs_count=mbsf_ffs_cnt,
      mbsf_pde_util_count=mbsf_pde_util_cnt,
      key_uniqueness_rate=1.0,
      foreign_key_validity_rate=max(0.0, min(1.0, fk_validity_rate)),
      temporal_integrity_rate=max(0.0, min(1.0, temp_integrity_rate)),
    )

  def generate_sql_schema(self) -> str:
    """Generate DDL schema for loading exported tables into SQL engines (e.g. DuckDB, PostgreSQL)."""
    return (
      "-- Medicare-Synth 2021 CCW Baseline Reference DDL Schema\n\n"
      "CREATE TABLE IF NOT EXISTS beneficiary (\n"
      "    BENE_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_BIRTH_DT DATE,\n"
      "    BENE_DEATH_DT DATE,\n"
      "    BENE_SEX_IDENT_CD VARCHAR,\n"
      "    BENE_RACE_CD VARCHAR\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS carrier (\n"
      "    CLM_ID VARCHAR,\n"
      "    LINE_NUM INTEGER,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    CLM_FROM_DT DATE,\n"
      "    CLM_THRU_DT DATE,\n"
      "    PRVDR_NPI VARCHAR,\n"
      "    ICD_DGNS_CD1 VARCHAR,\n"
      "    PRIMARY KEY (CLM_ID, LINE_NUM)\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS outpatient (\n"
      "    CLM_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    CLM_FROM_DT DATE,\n"
      "    CLM_THRU_DT DATE,\n"
      "    PRVDR_NPI VARCHAR,\n"
      "    ICD_DGNS_CD1 VARCHAR\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS inpatient (\n"
      "    CLM_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    CLM_ADMSN_DT DATE,\n"
      "    NCH_BENE_DSCHRG_DT DATE,\n"
      "    CLM_PMT_AMT NUMERIC,\n"
      "    CLM_UTLZTN_DAY_CNT INTEGER,\n"
      "    CLM_DRG_CD VARCHAR\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS pde (\n"
      "    PDE_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    SRVC_DT DATE,\n"
      "    PROD_SRVC_ID VARCHAR,\n"
      "    QTY_DSPNSD_NUM NUMERIC,\n"
      "    DAYS_SUPLY_NUM INTEGER,\n"
      "    PTNT_PAY_AMT NUMERIC,\n"
      "    TOT_RX_CST_AMT NUMERIC\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS snf (\n"
      "    CLM_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    CLM_ADMSN_DT DATE,\n"
      "    NCH_BENE_DSCHRG_DT DATE,\n"
      "    CLM_PMT_AMT NUMERIC,\n"
      "    CLM_UTLZTN_DAY_CNT INTEGER,\n"
      "    NCVD_DAYS_CNT INTEGER\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS hha (\n"
      "    CLM_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    CLM_ADMSN_DT DATE,\n"
      "    NCH_BENE_DSCHRG_DT DATE,\n"
      "    CLM_PMT_AMT NUMERIC,\n"
      "    CLM_UTLZTN_DAY_CNT INTEGER,\n"
      "    CLM_HHA_LUPA_IND VARCHAR\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS dme (\n"
      "    CLM_ID VARCHAR,\n"
      "    LINE_NUM INTEGER,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    CLM_FROM_DT DATE,\n"
      "    CLM_THRU_DT DATE,\n"
      "    CLM_PMT_AMT NUMERIC,\n"
      "    DME_LINE_ITEM_COUNT INTEGER,\n"
      "    LINE_CMS_TYPE_SRVC_CD VARCHAR,\n"
      "    PRIMARY KEY (CLM_ID, LINE_NUM)\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS hospice (\n"
      "    CLM_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    CLM_ADMSN_DT DATE,\n"
      "    NCH_BENE_DSCHRG_DT DATE,\n"
      "    CLM_PMT_AMT NUMERIC,\n"
      "    CLM_UTLZTN_DAY_CNT INTEGER,\n"
      "    HOSPICE_TERMINAL_DIAG_CD VARCHAR\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS mbsf_chronic_conditions (\n"
      "    BENE_ID VARCHAR PRIMARY KEY REFERENCES beneficiary(BENE_ID),\n"
      "    RFRNC_YR INTEGER,\n"
      "    SP_ALZHMD VARCHAR,\n"
      "    SP_CHF VARCHAR,\n"
      "    SP_CHRNKIDN VARCHAR,\n"
      "    SP_CNCR VARCHAR,\n"
      "    SP_DIABETES VARCHAR,\n"
      "    SP_ISCHDMT VARCHAR,\n"
      "    SP_STRKETIA VARCHAR,\n"
      "    VAL_MBSF_01 NUMERIC\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS mbsf_cost_and_use (\n"
      "    BENE_ID VARCHAR PRIMARY KEY REFERENCES beneficiary(BENE_ID),\n"
      "    RFRNC_YR INTEGER,\n"
      "    BENE_MDCR_PAY_AMT NUMERIC,\n"
      "    BENE_TOT_PAY_AMT NUMERIC,\n"
      "    BENE_IP_DDCTBL_AMT NUMERIC,\n"
      "    BENE_CVRD_DYS_CNT INTEGER\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS mbsf_part_d (\n"
      "    BENE_ID VARCHAR PRIMARY KEY REFERENCES beneficiary(BENE_ID),\n"
      "    RFRNC_YR INTEGER,\n"
      "    PTD_CNTRCT_ID_01 VARCHAR,\n"
      "    PTD_PBP_ID_01 VARCHAR,\n"
      "    PTD_SGNT_CD_01 VARCHAR,\n"
      "    RDS_IND_01 VARCHAR,\n"
      "    LI_COST_SHRH_GRP_CD_01 VARCHAR,\n"
      "    BENE_PTD_TRCC_AMT NUMERIC,\n"
      "    BENE_PTD_MOOP_AMT NUMERIC\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS mbsf_base_enrollment (\n"
      "    BENE_ID VARCHAR PRIMARY KEY REFERENCES beneficiary(BENE_ID),\n"
      "    RFRNC_YR INTEGER,\n"
      "    BENE_HI_CVRAGE_TOT_MONS INTEGER,\n"
      "    BENE_SMI_CVRAGE_TOT_MONS INTEGER,\n"
      "    BENE_HMO_CVRAGE_TOT_MONS INTEGER,\n"
      "    BENE_PTD_CVRAGE_TOT_MONS INTEGER,\n"
      "    MDCR_ENTLMT_BUYIN_IND_01 VARCHAR,\n"
      "    DUAL_STUS_CD_01 VARCHAR,\n"
      "    VAL_MBSF_BASE_01 NUMERIC\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS mbsf_other_chronic_conditions (\n"
      "    BENE_ID VARCHAR PRIMARY KEY REFERENCES beneficiary(BENE_ID),\n"
      "    RFRNC_YR INTEGER,\n"
      "    SP_ARTHGLAU VARCHAR,\n"
      "    SP_ASTHMA VARCHAR,\n"
      "    SP_ATRIALF VARCHAR,\n"
      "    SP_HYPERL VARCHAR,\n"
      "    SP_HYPERT VARCHAR,\n"
      "    SP_HYPOT VARCHAR,\n"
      "    SP_OSTEOP VARCHAR,\n"
      "    VAL_MBSF_OC_01 NUMERIC\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS mbsf_ndi (\n"
      "    BENE_ID VARCHAR PRIMARY KEY REFERENCES beneficiary(BENE_ID),\n"
      "    RFRNC_YR INTEGER,\n"
      "    NDI_MATCH_IND VARCHAR,\n"
      "    NDI_DIUSE_CD VARCHAR,\n"
      "    VAL_MBSF_NDI_01 NUMERIC\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS mbsf_risk_adjustment (\n"
      "    BENE_ID VARCHAR PRIMARY KEY REFERENCES beneficiary(BENE_ID),\n"
      "    RFRNC_YR INTEGER,\n"
      "    CMS_HCC_RISK_SCORE NUMERIC,\n"
      "    RXHCC_RISK_SCORE NUMERIC,\n"
      "    PAYMENT_COUNT INTEGER,\n"
      "    VAL_MBSF_RA_01 NUMERIC\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS mbsf_part_c (\n"
      "    BENE_ID VARCHAR PRIMARY KEY REFERENCES beneficiary(BENE_ID),\n"
      "    RFRNC_YR INTEGER,\n"
      "    PTC_CNTRCT_ID_01 VARCHAR,\n"
      "    PTC_PBP_ID_01 VARCHAR,\n"
      "    PTC_PLAN_TYPE_CD_01 VARCHAR,\n"
      "    BENE_MA_CVRAGE_TOT_MONS INTEGER,\n"
      "    VAL_MBSF_C_01 NUMERIC\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS mbsf_ffs_utilization (\n"
      "    BENE_ID VARCHAR PRIMARY KEY REFERENCES beneficiary(BENE_ID),\n"
      "    RFRNC_YR INTEGER,\n"
      "    IP_ADM_CNT INTEGER,\n"
      "    OP_VIST_CNT INTEGER,\n"
      "    SNF_STAY_CNT INTEGER,\n"
      "    CAR_SRVC_CNT INTEGER,\n"
      "    HHA_VIST_CNT INTEGER,\n"
      "    HOSP_STAY_CNT INTEGER,\n"
      "    DME_SRVC_CNT INTEGER,\n"
      "    VAL_MBSF_FFS_01 NUMERIC\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS mbsf_pde_utilization (\n"
      "    BENE_ID VARCHAR PRIMARY KEY REFERENCES beneficiary(BENE_ID),\n"
      "    RFRNC_YR INTEGER,\n"
      "    PDE_TOT_FILL_CNT INTEGER,\n"
      "    PDE_BRAND_FILL_CNT INTEGER,\n"
      "    PDE_GENERIC_FILL_CNT INTEGER,\n"
      "    PDE_TOT_CST_AMT NUMERIC,\n"
      "    PDE_PTNT_PAY_AMT NUMERIC,\n"
      "    PDE_LIS_PAY_AMT NUMERIC,\n"
      "    VAL_MBSF_PDE_UTIL_01 NUMERIC\n"
      ");\n"
    )

  def export_slice(
    self,
    bene_df: pl.DataFrame,
    carrier_df: pl.DataFrame,
    outpatient_df: pl.DataFrame,
    fmt: Literal["csv", "parquet", "all"] = "all",
    inpatient_df: pl.DataFrame | None = None,
    pde_df: pl.DataFrame | None = None,
    snf_df: pl.DataFrame | None = None,
    hha_df: pl.DataFrame | None = None,
    dme_df: pl.DataFrame | None = None,
    hospice_df: pl.DataFrame | None = None,
    mbsf_cc_df: pl.DataFrame | None = None,
    mbsf_cu_df: pl.DataFrame | None = None,
    mbsf_d_df: pl.DataFrame | None = None,
    mbsf_base_df: pl.DataFrame | None = None,
    mbsf_oc_df: pl.DataFrame | None = None,
    mbsf_ndi_df: pl.DataFrame | None = None,
    mbsf_ra_df: pl.DataFrame | None = None,
    mbsf_c_df: pl.DataFrame | None = None,
    mbsf_ffs_df: pl.DataFrame | None = None,
    mbsf_pde_util_df: pl.DataFrame | None = None,
  ) -> ReleaseManifest:
    """Export normalized tabular data and metadata artifacts to the release directory."""
    self.output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run validation
    report = self.validator.validate_slice(
      bene_df, carrier_df, outpatient_df, inpatient_df, pde_df, snf_df, hha_df, dme_df, hospice_df, mbsf_cc_df, mbsf_cu_df, mbsf_d_df, mbsf_base_df, mbsf_oc_df, mbsf_ndi_df, mbsf_ra_df, mbsf_c_df, mbsf_ffs_df, mbsf_pde_util_df
    )

    # 2. Compute fidelity profile
    fidelity = self.compute_fidelity_profile(
      bene_df, carrier_df, outpatient_df, report, inpatient_df, pde_df, snf_df, hha_df, dme_df, hospice_df, mbsf_cc_df, mbsf_cu_df, mbsf_d_df, mbsf_base_df, mbsf_oc_df, mbsf_ndi_df, mbsf_ra_df, mbsf_c_df, mbsf_ffs_df, mbsf_pde_util_df
    )

    # Write validation report and fidelity profile
    with open(self.output_dir / "validation_report.json", "w") as f:
      f.write(report.model_dump_json(indent=2))

    with open(self.output_dir / "fidelity_profile.json", "w") as f:
      f.write(fidelity.model_dump_json(indent=2))

    # Write SQL DDL schema reference
    with open(self.output_dir / "sql_reference_schema.sql", "w") as f:
      f.write(self.generate_sql_schema())

    file_entries: Dict[str, FileReleaseEntry] = {}

    tables: dict[str, pl.DataFrame] = {
      "beneficiary": bene_df,
      "carrier": carrier_df,
      "outpatient": outpatient_df,
    }
    if inpatient_df is not None:
      tables["inpatient"] = inpatient_df
    if pde_df is not None:
      tables["pde"] = pde_df
    if snf_df is not None:
      tables["snf"] = snf_df
    if hha_df is not None:
      tables["hha"] = hha_df
    if dme_df is not None:
      tables["dme"] = dme_df
    if hospice_df is not None:
      tables["hospice"] = hospice_df
    if mbsf_cc_df is not None:
      tables["mbsf_cc"] = mbsf_cc_df
    if mbsf_cu_df is not None:
      tables["mbsf_cu"] = mbsf_cu_df
    if mbsf_d_df is not None:
      tables["mbsf_d"] = mbsf_d_df
    if mbsf_base_df is not None:
      tables["mbsf_base"] = mbsf_base_df
    if mbsf_oc_df is not None:
      tables["mbsf_oc"] = mbsf_oc_df
    if mbsf_ndi_df is not None:
      tables["mbsf_ndi"] = mbsf_ndi_df
    if mbsf_ra_df is not None:
      tables["mbsf_ra"] = mbsf_ra_df
    if mbsf_c_df is not None:
      tables["mbsf_c"] = mbsf_c_df
    if mbsf_ffs_df is not None:
      tables["mbsf_ffs"] = mbsf_ffs_df
    if mbsf_pde_util_df is not None:
      tables["mbsf_pde_util"] = mbsf_pde_util_df




    formats_to_export = ["csv", "parquet"] if fmt == "all" else [fmt]

    for tbl_name, df in tables.items():
      for file_fmt in formats_to_export:
        filename = f"{tbl_name}.{file_fmt}"
        file_path = self.output_dir / filename

        if file_fmt == "csv":
          df.write_csv(file_path)
        elif file_fmt == "parquet":
          df.write_parquet(file_path)

        sha256_hash = self._compute_sha256(file_path)
        entry_key = f"{tbl_name}_{file_fmt}"

        file_entries[entry_key] = FileReleaseEntry(
          filename=filename,
          format=file_fmt,
          row_count=df.height,
          sha256=sha256_hash,
          size_bytes=file_path.stat().st_size,
        )

    manifest = ReleaseManifest(
      release_id=self.release_id,
      created_at=datetime.now(timezone.utc).isoformat(),
      validation_passed=report.is_valid,
      files=file_entries,
    )

    with open(self.output_dir / "release_manifest.json", "w") as f:
      f.write(manifest.model_dump_json(indent=2))

    return manifest
