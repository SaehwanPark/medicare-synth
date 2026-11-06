# Phase 4 — Calibration engine

**Status:** Complete (2026-11-06)
**Package:** `medicare_synth.calibration`
**Corpus:** frozen `mvp-2021-om-ffs-diabetes-ip-corpus-v1` (Phase 3)

## Levels

| Level | API | Behavior |
| --- | --- | --- |
| A | `level_a_baseline` | Discrepancy on calibration + holdout; no fit |
| B | `calibrate_reweight` | Sequential IPF/raking weights; records unchanged |
| C | `calibrate_generator_params` | Discrete search over diabetes/HF/`P(IP\|diabetes)` |

Holdout finding IDs are rejected by `assert_calibration_partition_only` if
passed into a fit path.

## Diagnostics

Reweighting reports ESS, min/max weight, sum of weights, iterations,
convergence, and infeasibility notes. Manifests record corpus SHA-256, seeds,
hyperparameters, pre/post MAE, and structural validity.

## Dependence assumptions

Calibration targets may share overlapping CCW/FFS source populations. Treat
moment discrepancies as **dependent**; do not interpret joint MAE as an
independent likelihood.

## Non-claims

Improving synthetic MAE toward published magnitudes is a controllability /
engineering demonstration—not Medicare representativeness.
