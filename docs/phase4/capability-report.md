# Phase 4 — Capability report

**Date:** 2026-11-06
**Verdict:** Phase 4 exit criteria **met**.

## Known-truth experiment

Miscalibrated start (`diabetes=0.18`, `hf=0.04`, `P(IP|diab)=0.05`, n=6000,
seed=42) vs frozen calibration targets (0.277 / 0.12 / 0.13):

| Level | Calibration MAE | Notes |
| --- | --- | --- |
| A | ≈ 0.086 | Baseline |
| B | ≈ 0.0007 | ESS ≈ 4606; converged; records unchanged |
| C | ≈ 0.0025 | Fitted params → 0.277 / 0.12 / 0.13 |

Holdout MAE is reported under C but **not** used in the search objective.
Structural validators pass on baseline and fitted worlds.

Artifact: [`reports/phase4/known_truth_experiment.json`](../../reports/phase4/known_truth_experiment.json).

## Exit criteria

| Criterion | Status |
| --- | --- |
| Controlled simulations improve predeclared targets without invalidating records | **Met** (B weights-only; C regenerates valid worlds) |
| Pipeline runs fully without agents | **Met** (`calibration.py` APIs) |
| Dependence/uncertainty assumptions visible | **Met** (diagnostics + manifest assumptions) |
| Agent role contracts + review gates | **Met** (`AGENT_ROLE_CONTRACTS`; [agent-roles.md](agent-roles.md)) |
| Deterministic run manifests | **Met** (`CalibrationRunManifest.sha256`) |

## Limitations

1. Level B cannot create unsupported combinations (support failure reported).
2. Level C uses a coarse discrete grid, not continuous MLE / hierarchical Bayes.
3. LIT-07 remains a weak industry prior inside the frozen corpus.
4. Phase 5 still needed for multi-world release packaging.

## Next (Phase 5)

Emit reference + alternative worlds with shared calibration targets and
documented weak-assumption variation; package manifests/limitations.
