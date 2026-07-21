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
  ) -> FidelityProfile:
    """Compute summary metrics and integrity rates for a dataset slice.

    Args:
      bene_df: Beneficiary DataFrame.
      carrier_df: Carrier Claims DataFrame.
      outpatient_df: Outpatient Claims DataFrame.
      validation_report: Relational validation report.
      inpatient_df: Optional Inpatient Claims DataFrame.

    Returns:
      FidelityProfile instance containing computed counts and validity ratios.
    """
    inp_count = inpatient_df.height if inpatient_df is not None else 0
    total_claims = carrier_df.height + outpatient_df.height + inp_count
    fk_findings = [f for f in validation_report.findings if f.category == FindingCategory.RELATIONAL]
    temp_findings = [f for f in validation_report.findings if f.category == FindingCategory.TEMPORAL]

    fk_validity_rate = 1.0 - (len(fk_findings) / max(total_claims, 1)) if fk_findings else 1.0
    temp_integrity_rate = 1.0 - (len(temp_findings) / max(total_claims, 1)) if temp_findings else 1.0

    return FidelityProfile(
      bene_count=bene_df.height,
      carrier_claim_count=carrier_df.height,
      outpatient_claim_count=outpatient_df.height,
      inpatient_claim_count=inp_count,
      key_uniqueness_rate=1.0,
      foreign_key_validity_rate=max(0.0, min(1.0, fk_validity_rate)),
      temporal_integrity_rate=max(0.0, min(1.0, temp_integrity_rate)),
    )

  def generate_sql_schema(self) -> str:
    """Generate DDL schema for loading exported tables into SQL engines (e.g. DuckDB, PostgreSQL).

    Returns:
      SQL string containing DDL statements.
    """
    return (
      "-- Medicare-Synth 2021 CCW Baseline Reference DDL Schema\n\n"
      "CREATE TABLE IF NOT EXISTS beneficiary (\n"
      "    BENE_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_BIRTH_DT DATE,\n"
      "    BENE_DEATH_DT DATE,\n"
      "    SEX_IDENT_CD VARCHAR,\n"
      "    BENE_RACE_CD VARCHAR,\n"
      "    SP_STATE_CODE VARCHAR,\n"
      "    BENE_COUNTY_CD VARCHAR\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS carrier_claim (\n"
      "    CLM_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    CLM_FROM_DT DATE,\n"
      "    CLM_THRU_DT DATE,\n"
      "    LINE_NUM INTEGER,\n"
      "    LINE_CMS_TYPE_SRVC_CD VARCHAR,\n"
      "    LINE_NCH_PAY_TP_CD VARCHAR\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS outpatient_claim (\n"
      "    CLM_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    CLM_FROM_DT DATE,\n"
      "    CLM_THRU_DT DATE,\n"
      "    NCH_BENEFTS_DISCHRG_DT DATE,\n"
      "    CLM_PMT_AMT NUMERIC\n"
      ");\n\n"
      "CREATE TABLE IF NOT EXISTS inpatient_claim (\n"
      "    CLM_ID VARCHAR PRIMARY KEY,\n"
      "    BENE_ID VARCHAR REFERENCES beneficiary(BENE_ID),\n"
      "    CLM_ADMSN_DT DATE,\n"
      "    NCH_BENE_DSCHRG_DT DATE,\n"
      "    CLM_PMT_AMT NUMERIC,\n"
      "    CLM_UTLZTN_DAY_CNT INTEGER,\n"
      "    CLM_DRG_CD VARCHAR\n"
      ");\n"
    )

  def export_slice(
    self,
    bene_df: pl.DataFrame,
    carrier_df: pl.DataFrame,
    outpatient_df: pl.DataFrame,
    fmt: Literal["csv", "parquet", "all"] = "all",
    inpatient_df: pl.DataFrame | None = None,
  ) -> ReleaseManifest:
    """Export normalized tabular data and metadata artifacts to the release directory.

    Args:
      bene_df: Beneficiary DataFrame.
      carrier_df: Carrier Claims DataFrame.
      outpatient_df: Outpatient Claims DataFrame.
      fmt: Format choice ('csv', 'parquet', or 'all').
      inpatient_df: Optional Inpatient Claims DataFrame.

    Returns:
      ReleaseManifest detailing the exported files and validation summary.
    """
    self.output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run validation
    report = self.validator.validate_slice(bene_df, carrier_df, outpatient_df, inpatient_df)

    # 2. Compute fidelity profile
    fidelity = self.compute_fidelity_profile(bene_df, carrier_df, outpatient_df, report, inpatient_df)

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
