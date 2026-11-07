# Phase 5 — World family

**Family ID:** `mvp-2021-om-ffs-diabetes-ip-worlds-v1`
**API:** `medicare_synth.worlds.emit_world_family` /
`analyze_world_moments`

## Shared calibration targets

All worlds fit the same frozen calibration partition only:

| Finding | Moment |
| --- | --- |
| CMS-AGG-03 | diabetes prevalence 0.277 |
| CMS-AGG-04 | HF prevalence 0.12 |
| LIT-07 | P(IP \| diabetes) 0.13 |

Holdout (LIT-03 women stratum) is evaluate-only.

## Worlds

| World ID | Method | Free assumption highlight |
| --- | --- | --- |
| `mvp-w1-reweight-v1` | Level B IPF reweight | `P(IP\|no diabetes)=0.04`; records unchanged |
| `mvp-w2-generator-v1` | Level C param search | `P(IP\|no diabetes)=0.04`; regenerate toward targets |
| `mvp-w3-generator-high-bg-ip-v1` | Level C param search | `P(IP\|no diabetes)=0.08` (alternate free rate) |

Shared documented weak assumptions also include diabetes ⟂ HF Bernoulli draws,
year transport on CMS aggregates, and LIT-07 as a weak industry prior.

## Downstream analysis

`analyze_world_moments(tables, corpus, weights=...)` is the identical
comparison API for every world (calibration + holdout discrepancy reports).

## Reproduce

```shell
uv run python scripts/phase5_emit_worlds.py
```
