"""Cross-domain synthetic data quality and privacy audit engine for Medicare-Synth.

Provides relational join coverage evaluation, k-anonymity privacy metrics,
and column-level statistical audit metrics across synthetic tables.
"""

import datetime

import polars as pl
from pydantic import BaseModel, Field


def _find_col(df: pl.DataFrame, target: str) -> str | None:
  """Find column name case-insensitively in DataFrame."""
  target_upper = target.upper()
  for col in df.columns:
    if col.upper() == target_upper:
      return col
  return None


class KAnonymityResult(BaseModel):
  """K-anonymity privacy evaluation result for a set of quasi-identifiers."""

  qi_columns: list[str] = Field(..., description="Quasi-identifier column names evaluated.")
  min_k: int = Field(..., description="Minimum equivalence class size observed.")
  class_count: int = Field(..., description="Number of distinct equivalence classes.")
  at_risk_record_count: int = Field(..., description="Count of records in classes with k < 5.")


class ColumnAuditMetric(BaseModel):
  """Column-level audit metric for nullity and uniqueness."""

  column_name: str = Field(..., description="Name of the evaluated column.")
  total_count: int = Field(..., description="Total row count evaluated.")
  null_count: int = Field(..., description="Count of null or missing values.")
  null_ratio: float = Field(..., description="Fraction of null values (0.0 to 1.0).")
  unique_count: int = Field(..., description="Count of unique distinct values.")


class AuditReport(BaseModel):
  """Unified cross-domain synthetic dataset audit report."""

  scenario_name: str = Field(..., description="Name of the audited scenario or dataset.")
  timestamp: str = Field(..., description="ISO 8601 timestamp of audit execution.")
  join_coverage: dict[str, float] = Field(..., description="Relational join coverage ratios.")
  k_anonymity: dict[str, KAnonymityResult] = Field(..., description="K-anonymity metrics by table.")
  column_metrics: dict[str, list[ColumnAuditMetric]] = Field(..., description="Column metrics by table.")


class AuditEngine:
  """Engine for executing data quality and privacy audits over Polars DataFrames."""

  def __init__(self, dataset: dict[str, pl.DataFrame], scenario_name: str = "custom") -> None:
    """Initialize audit engine with named table DataFrames."""
    self.dataset = dataset
    self.scenario_name = scenario_name

  def compute_join_coverage(self) -> dict[str, float]:
    """Compute foreign key join coverage ratios between claims and beneficiary tables."""
    coverage: dict[str, float] = {}

    bene_df = self.dataset.get("beneficiary")
    if bene_df is None or bene_df.is_empty():
      return coverage

    bene_col = _find_col(bene_df, "BENE_ID")
    if not bene_col:
      return coverage

    bene_ids = set(bene_df.get_column(bene_col).to_list())
    total_bene = len(bene_ids)
    if total_bene == 0:
      return coverage

    for table_name in ("carrier", "outpatient", "inpatient", "pde", "snf", "hha", "dme", "hospice", "mbsf_cc", "mbsf_cu", "mbsf_d", "mbsf_base", "mbsf_oc", "mbsf_ndi"):
      claims_df = self.dataset.get(table_name)

      if claims_df is not None and not claims_df.is_empty():
        claim_bene_col = _find_col(claims_df, "BENE_ID")
        if claim_bene_col:
          claim_benes = claims_df.get_column(claim_bene_col).to_list()
          matched = sum(1 for b in claim_benes if b in bene_ids)
          coverage[f"beneficiary_{table_name}_coverage"] = round(matched / len(claim_benes), 4) if claim_benes else 1.0

    return coverage



  def compute_k_anonymity(self, table_name: str, qi_columns: list[str]) -> KAnonymityResult | None:
    """Compute k-anonymity privacy score for specified quasi-identifier columns."""
    df = self.dataset.get(table_name)
    if df is None or df.is_empty():
      return None

    valid_cols: list[str] = []
    for qi in qi_columns:
      matched = _find_col(df, qi)
      if matched:
        valid_cols.append(matched)

    if not valid_cols:
      return None

    # Group by quasi-identifiers to get equivalence class sizes
    grouped = df.group_by(valid_cols).agg(pl.len().alias("k_count"))
    k_counts = grouped.get_column("k_count").to_list()

    min_k = min(k_counts) if k_counts else 0
    class_count = len(k_counts)
    at_risk = sum(count for count in k_counts if count < 5)

    return KAnonymityResult(
      qi_columns=valid_cols,
      min_k=min_k,
      class_count=class_count,
      at_risk_record_count=at_risk,
    )

  def compute_column_metrics(self, table_name: str) -> list[ColumnAuditMetric]:
    """Compute nullity ratios and distinct counts for all columns in a table."""
    df = self.dataset.get(table_name)
    if df is None or df.is_empty():
      return []

    metrics: list[ColumnAuditMetric] = []
    total_count = len(df)

    for col_name in df.columns:
      col = df.get_column(col_name)
      null_count = col.null_count()
      null_ratio = round(null_count / total_count, 4) if total_count > 0 else 0.0
      unique_count = col.n_unique()

      metrics.append(
        ColumnAuditMetric(
          column_name=col_name,
          total_count=total_count,
          null_count=null_count,
          null_ratio=null_ratio,
          unique_count=unique_count,
        )
      )

    return metrics

  def run_audit(self) -> AuditReport:
    """Execute complete audit suite and return structured AuditReport."""
    coverage = self.compute_join_coverage()

    k_anon_map: dict[str, KAnonymityResult] = {}
    if "beneficiary" in self.dataset:
      res = self.compute_k_anonymity("beneficiary", ["BENE_BIRTH_DT"])
      if res is not None:
        k_anon_map["beneficiary"] = res

    if "carrier" in self.dataset:
      res = self.compute_k_anonymity("carrier", ["ICD_DGNS_CD1"])
      if res is not None:
        k_anon_map["carrier"] = res

    if "inpatient" in self.dataset:
      res = self.compute_k_anonymity("inpatient", ["CLM_DRG_CD"])
      if res is not None:
        k_anon_map["inpatient"] = res

    if "pde" in self.dataset:
      res = self.compute_k_anonymity("pde", ["PROD_SRVC_ID"])
      if res is not None:
        k_anon_map["pde"] = res


    col_metrics_map: dict[str, list[ColumnAuditMetric]] = {}
    for table_name in self.dataset:
      col_metrics_map[table_name] = self.compute_column_metrics(table_name)

    return AuditReport(
      scenario_name=self.scenario_name,
      timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      join_coverage=coverage,
      k_anonymity=k_anon_map,
      column_metrics=col_metrics_map,
    )
