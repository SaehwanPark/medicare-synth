"""Typed importer for the bounded CMS Synthetic Medicare Claims PUF slice."""

from dataclasses import dataclass
from pathlib import Path

import polars as pl

from medicare_synth.evidence import RKBEvidenceSnapshot
from medicare_synth.manifest import SourceManifest
from medicare_synth.models import ProvenanceStatus


class PufImportError(ValueError):
    """Raised when source evidence and a local PUF file disagree."""


@dataclass(frozen=True)
class PufSlice:
    """Normalized beneficiary and carrier records with their evidence identity."""

    beneficiary_df: pl.DataFrame
    carrier_df: pl.DataFrame
    source_manifest: SourceManifest
    evidence_snapshot: RKBEvidenceSnapshot
    provenance: dict[str, ProvenanceStatus]


def _source_column(frame: pl.DataFrame, name: str) -> str:
    candidates = {column.upper(): column for column in frame.columns}
    if name.upper() not in candidates:
        raise PufImportError(f"required source column is missing: {name}")
    return candidates[name.upper()]


def _date_format(evidence: RKBEvidenceSnapshot, source: str) -> str:
    variable = evidence.get_variable(source)
    if variable is None or variable.format is None:
        raise PufImportError(f"date format is not defined by evidence: {source}")
    formats = {"YYYYMMDD": "%Y%m%d", "YYYY-MM-DD": "%Y-%m-%d"}
    if variable.format not in formats:
        raise PufImportError(f"unsupported documented date format: {variable.format}")
    return formats[variable.format]


def _project(
    frame: pl.DataFrame,
    mapping: dict[str, str],
    evidence: RKBEvidenceSnapshot,
) -> pl.DataFrame:
    expressions: list[pl.Expr] = []
    for target, source in mapping.items():
        actual = _source_column(frame, source)
        expression = pl.col(actual).alias(target)
        if target.endswith("_dt"):
            expression = (
                pl.when(pl.col(actual).is_null() | (pl.col(actual) == ""))
                .then(None)
                .otherwise(pl.col(actual))
                .str.strptime(pl.Date, format=_date_format(evidence, source), strict=True)
                .alias(target)
            )
        expressions.append(expression)
    return frame.select(expressions)


class PufImporter:
    """Load only the two files declared by a verified source manifest."""

    def load(
        self,
        source_dir: Path,
        manifest_path: Path,
        evidence_path: Path,
        service_year: int = 2022,
    ) -> PufSlice:
        manifest = SourceManifest.from_file(manifest_path)
        evidence = RKBEvidenceSnapshot.from_file(evidence_path)
        required = {"beneficiary_2022", "carrier"}
        declared = {item.file_id for item in manifest.files}
        if not required.issubset(declared):
            raise PufImportError("manifest must declare beneficiary_2022 and carrier")
        errors = manifest.verify_directory(source_dir)
        if errors:
            raise PufImportError("; ".join(errors))

        def read(file_id: str) -> pl.DataFrame:
            item = manifest.get_file_manifest(file_id)
            if item is None:
                raise PufImportError(f"manifest entry not found: {file_id}")
            return pl.read_csv(
                source_dir / item.filename,
                separator=item.delimiter,
                infer_schema=False,
                null_values=["", "NA", "NULL"],
            )

        beneficiary = _project(
            read("beneficiary_2022"),
            {
                "bene_id": "BENE_ID",
                "bene_birth_dt": "BENE_BIRTH_DT",
                "bene_death_dt": "BENE_DEATH_DT",
                "bene_sex_ident_cd": "BENE_SEX_IDENT_CD",
                "bene_race_cd": "BENE_RACE_CD",
            },
            evidence,
        ).sort("bene_id")
        carrier = _project(
            read("carrier"),
            {
                "clm_id": "CLM_ID",
                "line_num": "LINE_NUM",
                "bene_id": "BENE_ID",
                "clm_from_dt": "CLM_FROM_DT",
                "clm_thru_dt": "CLM_THRU_DT",
                "prvdr_npi": "PRVDR_NPI",
                "icd_dgns_cd1": "ICD_DGNS_CD1",
            },
            evidence,
        ).with_columns(pl.col("line_num").cast(pl.Int64, strict=True)).sort(
            ["clm_id", "line_num"]
        )
        if carrier.select(pl.col("clm_from_dt").dt.year().min()).item() is not None:
            carrier = carrier.filter(pl.col("clm_from_dt").dt.year() == service_year)
        return PufSlice(
            beneficiary_df=beneficiary,
            carrier_df=carrier,
            source_manifest=manifest,
            evidence_snapshot=evidence,
            provenance={
                "beneficiary": ProvenanceStatus.NORMALIZED,
                "carrier": ProvenanceStatus.NORMALIZED,
            },
        )
