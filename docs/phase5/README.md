# Phase 5 — MVP calibrated worlds

**Status:** Complete (2026-11-07)
**Packages:** `medicare_synth.worlds`, `medicare_synth.evaluation`
**Corpus:** frozen `mvp-2021-om-ffs-diabetes-ip-corpus-v1`
**Family:** `mvp-2021-om-ffs-diabetes-ip-worlds-v1`
**Evaluation freeze:** `mvp-2021-om-ffs-diabetes-ip-eval-freeze-v1`

## Docs

| Doc | Role |
| --- | --- |
| [world-family.md](world-family.md) | Shared targets, weak assumptions, emit API |
| [evaluation-freeze.md](evaluation-freeze.md) | Hard gates, graded metrics, holdout isolation |
| [capability-report.md](capability-report.md) | Exit criteria and verified results |

## Artifacts

- [`reports/phase5/world_family_summary.json`](../../reports/phase5/world_family_summary.json)
- [`reports/phase5/evaluation_freeze.json`](../../reports/phase5/evaluation_freeze.json)
- [`configs/worlds/mvp_2021_om_ffs_diabetes_ip_worlds_v1.json`](../../configs/worlds/mvp_2021_om_ffs_diabetes_ip_worlds_v1.json)
- Emit script: `uv run python scripts/phase5_emit_worlds.py`

## Non-claims

Synthetic agreement with published moments is **not** a Medicare finding.
Phase 6 owns independent holdout/generalization claims; this phase packages
worlds without retuning against holdout.
