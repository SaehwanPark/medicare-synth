"""Vertical and horizontal dataset expansion framework for Medicare-Synth.

Provides TabDatSynthAdapter for vertical feature synthesis and HorizontalExpander
for connected-subgraph scaling with deterministic re-keying.
"""

from typing import Dict, List, Optional
import polars as pl

from medicare_synth.models import ProvenanceStatus


class TabDatSynthAdapter:
  """Adapter for integrating tabular data synthesis engines (e.g., tabdat-synth).

  Provides evidence-graded vertical expansion for within-table attributes while
  preserving relational keys and temporal invariants.
  """

  provenance_status: ProvenanceStatus = ProvenanceStatus.SYNTHESIZED

  def __init__(self, provider_name: str = "tabdat-synth-builtin"):
    """Initialize adapter with specified provider name.

    Args:
      provider_name: Identifier for the underlying synthesis engine.
    """
    self.provider_name = provider_name

  def synthesize_table(
    self,
    df: pl.DataFrame,
    target_columns: Optional[List[str]] = None,
    seed: int = 42,
  ) -> pl.DataFrame:
    """Synthesize or enhance within-table feature columns deterministically.

    Args:
      df: Source Polars DataFrame.
      target_columns: Optional list of new column names to synthesize.
      seed: Seed for deterministic feature generation.

    Returns:
      Polars DataFrame with added/modified synthetic feature columns.
    """
    cols_to_add = target_columns or ["SYN_RISK_SCORE"]
    result_df = df

    for idx, col_name in enumerate(cols_to_add):
      if col_name not in result_df.columns:
        # Deterministic generation using row index and seed
        col_expr = (
          (pl.arange(0, pl.len(), dtype=pl.Int64) * (seed + idx + 1) % 100) / 10.0
        ).alias(col_name)
        result_df = result_df.with_columns(col_expr)

    return result_df


class VerticalExpander:
  """Applies evidence-graded vertical expansion across dataset tables."""

  def __init__(self, adapter: Optional[TabDatSynthAdapter] = None):
    """Initialize VerticalExpander with a synthesis adapter.

    Args:
      adapter: TabDatSynthAdapter instance; defaults to built-in adapter.
    """
    self.adapter = adapter or TabDatSynthAdapter()

  def expand_slice(
    self,
    tables: Dict[str, pl.DataFrame],
    bene_features: Optional[List[str]] = None,
    seed: int = 42,
  ) -> Dict[str, pl.DataFrame]:
    """Perform vertical feature expansion on beneficiary and claim tables.

    Args:
      tables: Dictionary mapping table name to Polars DataFrame.
      bene_features: Optional list of feature names to synthesize on beneficiary summary.
      seed: Seed for deterministic feature generation.

    Returns:
      Updated dictionary of Polars DataFrames with vertical synthetic features.
    """
    expanded_tables: Dict[str, pl.DataFrame] = {}
    features = bene_features or ["SYN_RISK_SCORE", "SYN_CHRONIC_INDEX"]

    for tbl_name, df in tables.items():
      if tbl_name == "beneficiary_summary":
        expanded_tables[tbl_name] = self.adapter.synthesize_table(
          df, target_columns=features, seed=seed
        )
      else:
        expanded_tables[tbl_name] = df.clone()

    return expanded_tables


class HorizontalExpander:
  """Applies connected-subgraph horizontal expansion with deterministic re-keying."""

  provenance_status: ProvenanceStatus = ProvenanceStatus.REKEYED

  def __init__(self, seed: int = 42):
    """Initialize HorizontalExpander.

    Args:
      seed: Random seed for deterministic re-keying.
    """
    self.seed = seed

  def expand_subgraph(
    self,
    tables: Dict[str, pl.DataFrame],
    scale_factor: int = 2,
  ) -> Dict[str, pl.DataFrame]:
    """Replicate connected beneficiary subgraphs with deterministic re-keying.

    Args:
      tables: Dictionary mapping table names ("beneficiary_summary", "carrier_claims",
        "outpatient_claims") to Polars DataFrames.
      scale_factor: Number of subgraph copies to generate (e.g. 2 for 2x size).

    Returns:
      Scaled dictionary of Polars DataFrames with valid re-keyed foreign key relationships.
    """
    if scale_factor < 1:
      raise ValueError("scale_factor must be >= 1")

    if scale_factor == 1:
      return {tbl: df.clone() for tbl, df in tables.items()}

    scaled_tables: Dict[str, List[pl.DataFrame]] = {tbl: [df.clone()] for tbl, df in tables.items()}

    for copy_idx in range(1, scale_factor):
      suffix = f"_H{copy_idx}"

      for tbl_name, df in tables.items():
        rekeyed_df = df.clone()
        for col_name in ("BENE_ID", "bene_id"):
          if col_name in rekeyed_df.columns:
            rekeyed_df = rekeyed_df.with_columns(
              (pl.col(col_name) + suffix).alias(col_name)
            )
        for col_name in ("CLM_ID", "clm_id"):
          if col_name in rekeyed_df.columns:
            rekeyed_df = rekeyed_df.with_columns(
              (pl.col(col_name) + suffix).alias(col_name)
            )
        for col_name in ("PDE_ID", "pde_id"):
          if col_name in rekeyed_df.columns:
            rekeyed_df = rekeyed_df.with_columns(
              (pl.col(col_name) + suffix).alias(col_name)
            )
        scaled_tables[tbl_name].append(rekeyed_df)


    return {
      tbl: pl.concat(dfs, rechunk=True)
      for tbl, dfs in scaled_tables.items()
    }
