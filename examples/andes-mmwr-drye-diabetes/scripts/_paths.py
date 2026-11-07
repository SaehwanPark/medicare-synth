"""Shared paths for the Andes→Drye example."""

from __future__ import annotations

from pathlib import Path

EXAMPLE_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = EXAMPLE_ROOT / "evidence"
CORPUS_PATH = EVIDENCE_DIR / "corpus.json"
FIXTURES_ROOT = EVIDENCE_DIR
OUTPUT_DIR = EXAMPLE_ROOT / "output"
PARQUET_DIR = OUTPUT_DIR / "parquet"
REPORTS_DIR = OUTPUT_DIR / "reports"

BASELINE_N = 6000
BASELINE_SEED = 42
# Deliberately off Andes 31.6% so Level C has work to do.
BASELINE_DIABETES = 0.20
BASELINE_HF = 0.10
BASELINE_P_IP_DIAB = 0.08
BASELINE_P_IP_NO = 0.04

ANDES_FINDING_ID = "lit03-mmwr-diabetes-prevalence-2015"
DRYE_FINDING_ID = "lit02-drye-diabetes-unplanned-admission-rate-2012"
# Absolute tolerance for declaring in-domain A "aligned" after calibration.
ANDES_ABS_TOL = 0.015
