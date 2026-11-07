# Phase 5 — Capability report

**Date:** 2026-11-07
**Verdict:** Phase 5 exit criteria **met**.

## Multi-world emit (n=6000, seed=42)

| World | Calibration MAE before → after | Structural | Improved |
| --- | --- | --- | --- |
| `mvp-w1-reweight-v1` | 0.0858 → 0.0007 | pass | yes |
| `mvp-w2-generator-v1` | 0.0858 → 0.0025 | pass | yes |
| `mvp-w3-generator-high-bg-ip-v1` | 0.0858 → 0.0025 | pass | yes |

W2 and W3 share calibration-target search results while differing on free
`P(IP|no diabetes)` (0.04 vs 0.08). Holdout MAE is reported in manifests and
was **not** used in fit objectives.

Artifact: [`reports/phase5/world_family_summary.json`](../../reports/phase5/world_family_summary.json).

## Exit criteria

| Criterion | Status |
| --- | --- |
| Reference + controlled alternative worlds with shared targets | **Met** (3 worlds) |
| Documented weak-assumption variation | **Met** (method B vs C; free background IP) |
| Hard structural gates pass; no known degenerate fit failures | **Met** |
| Meaningful improvement on predeclared calibration metrics | **Met** (all three) |
| Underidentified dimensions documented | **Met** (weak assumptions + limitations) |
| Evaluation freeze before iterative fitting; holdout untouched | **Met** |
| Engines run without agents | **Met** (`worlds` / `evaluation` APIs) |

## Limitations

1. Level C remains a coarse discrete grid (Phase 4 engine).
2. Holdout improvement is observed / reported only—Phase 6 owns claims.
3. LIT-07 remains a weak industry prior inside corpus v1.
4. Public “calibrated release” still requires human approval.

## Next (Phase 6)

Independent held-out / research-utility evaluation protocol and go/no-go
decision without retuning against the same holdout set.
