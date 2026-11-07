"""Generate baseline + Andes-calibrated worlds; write Parquet and manifests.

Calibrates Level C generator params to paper A (Andes MMWR diabetes
prevalence 31.6%) using the example-local corpus. Holdout (women stratum) is
evaluate-only. Synthetic agreement is not a Medicare finding.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

# Allow `uv run python scripts/01_...` from this directory or repo root.
_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src") not in sys.path:
  sys.path.insert(0, str(_REPO / "src"))

from medicare_synth.calibration import (  # noqa: E402
  CalibrationLevel,
  build_run_manifest,
  calibrate_generator_params,
  discrepancy_for_findings,
  level_a_baseline,
  structural_valid,
)
from medicare_synth.evidence_corpus import (  # noqa: E402
  PartitionName,
  load_corpus,
  load_partition_findings,
)
from medicare_synth.synthesis import ConditionalWorldParams, generate_diabetes_ip_world  # noqa: E402

from _paths import (  # noqa: E402
  BASELINE_DIABETES,
  BASELINE_HF,
  BASELINE_N,
  BASELINE_P_IP_DIAB,
  BASELINE_P_IP_NO,
  BASELINE_SEED,
  CORPUS_PATH,
  FIXTURES_ROOT,
  OUTPUT_DIR,
  PARQUET_DIR,
  REPORTS_DIR,
)


def _write_parquet(tables: dict[str, pl.DataFrame], dest: Path) -> list[str]:
  dest.mkdir(parents=True, exist_ok=True)
  written: list[str] = []
  for name, frame in tables.items():
    path = dest / f"{name}.parquet"
    frame.write_parquet(path)
    written.append(str(path.relative_to(OUTPUT_DIR)))
  return written


def _report_to_dict(report) -> dict:
  return {
    "mean_absolute_error": report.mean_absolute_error,
    "n_missing": report.n_missing,
    "rows": [r.model_dump(mode="json") for r in report.rows],
  }


def main() -> int:
  OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
  REPORTS_DIR.mkdir(parents=True, exist_ok=True)
  corpus = load_corpus(CORPUS_PATH)

  baseline_params = ConditionalWorldParams(
    n_beneficiaries=BASELINE_N,
    seed=BASELINE_SEED,
    diabetes_prevalence=BASELINE_DIABETES,
    p_ip_given_diabetes=BASELINE_P_IP_DIAB,
    p_ip_given_no_diabetes=BASELINE_P_IP_NO,
    hf_prevalence=BASELINE_HF,
  )
  baseline_world = generate_diabetes_ip_world(baseline_params)
  baseline_tables = baseline_world.tables()
  baseline_parquet = _write_parquet(baseline_tables, PARQUET_DIR / "baseline")

  cal_before, hold_before = level_a_baseline(
    baseline_tables, corpus, fixtures_root=FIXTURES_ROOT
  )

  # Grid includes Andes 0.316; HF/IP free params stay near baseline (A is prevalence).
  result = calibrate_generator_params(
    baseline_params,
    corpus,
    fixtures_root=FIXTURES_ROOT,
    diabetes_values=(0.20, 0.25, 0.277, 0.30, 0.316, 0.35),
    hf_values=(0.10,),
    ip_diab_values=(0.08, 0.13),
  )
  fitted_world = generate_diabetes_ip_world(result.fitted_params)
  fitted_tables = fitted_world.tables()
  calibrated_parquet = _write_parquet(fitted_tables, PARQUET_DIR / "calibrated_to_a")

  cal_findings = load_partition_findings(
    corpus, PartitionName.CALIBRATION, fixtures_root=FIXTURES_ROOT
  )
  hold_findings = load_partition_findings(
    corpus, PartitionName.HOLDOUT, fixtures_root=FIXTURES_ROOT
  )
  cal_after = discrepancy_for_findings(
    fitted_tables, cal_findings, partition=PartitionName.CALIBRATION
  )
  hold_after = discrepancy_for_findings(
    fitted_tables, hold_findings, partition=PartitionName.HOLDOUT
  )

  ok_struct = structural_valid(fitted_world)
  manifest = build_run_manifest(
    run_id="example-andes-mmwr-level-c",
    level=CalibrationLevel.C_GENERATOR_PARAMS,
    corpus=corpus,
    corpus_path=CORPUS_PATH,
    seed=BASELINE_SEED,
    method_hyperparameters={
      "diabetes_values": [0.20, 0.25, 0.277, 0.30, 0.316, 0.35],
      "hf_values": [0.10],
      "ip_diab_values": [0.08, 0.13],
      "n_beneficiaries": BASELINE_N,
    },
    diagnostics={
      "improved_calibration": result.improved_calibration,
      "fitted_params": result.fitted_params.model_dump(mode="json"),
      "baseline_params": baseline_params.model_dump(mode="json"),
      "n_search_points": len(result.search_trace),
      "structural_valid": ok_struct,
    },
    calibration_mae_before=cal_before.mean_absolute_error,
    calibration_mae_after=cal_after.mean_absolute_error,
    holdout_mae_before=hold_before.mean_absolute_error,
    holdout_mae_after=hold_after.mean_absolute_error,
    structural_valid_flag=ok_struct,
    notes=(
      "Example-local corpus; paper A (Andes) is the sole calibration moment.",
      "Holdout women stratum is evaluate-only.",
      "Synthetic agreement is not a Medicare finding.",
    ),
  )

  payload = {
    "corpus_id": corpus.corpus_id,
    "baseline_parquet": baseline_parquet,
    "calibrated_parquet": calibrated_parquet,
    "structural_valid": ok_struct,
    "improved_calibration": result.improved_calibration,
    "fitted_params": result.fitted_params.model_dump(mode="json"),
    "calibration_before": _report_to_dict(cal_before),
    "calibration_after": _report_to_dict(cal_after),
    "holdout_before": _report_to_dict(hold_before),
    "holdout_after": _report_to_dict(hold_after),
    "manifest_sha256": manifest.sha256(),
    "manifest": json.loads(manifest.to_json()),
  }
  out = REPORTS_DIR / "build_and_calibrate.json"
  out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
  print(f"wrote {out}")
  print(
    "calibration MAE",
    cal_before.mean_absolute_error,
    "->",
    cal_after.mean_absolute_error,
    "| structural_valid",
    ok_struct,
  )
  return 0 if ok_struct else 1


if __name__ == "__main__":
  raise SystemExit(main())
