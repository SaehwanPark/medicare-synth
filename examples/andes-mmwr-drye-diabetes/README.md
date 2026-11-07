# Andes → Drye diabetes example (WIP)

End-to-end researcher workflow for Medicare-Synth:

1. **Paper A (in-domain):** Andes et al., *MMWR* 2019 — Medicare FFS diabetes
   prevalence 31.6% (2015, age ≥68).
2. **Paper B (out-domain):** Drye et al., *Medical Care* — acute unplanned
   admission rates among Medicare FFS with diabetes (2012; 41.4 / 100 PY).

This example **calibrates** a synthetic 2021 OM FFS–like diabetes→IP world to
**A**, exports Parquet, runs analytic replication for **A**, and documents why
**B**’s exact estimand is out of domain on the MVP schema (with a diagnostic
all-cause IP approximation).

> Synthetic agreement is **not** a Medicare finding. Do not publish these
> numbers as empirical results about beneficiaries.

## Status

WIP — scaffolding only. See the open PR for progress.

## Layout

| Path | Role |
| --- | --- |
| `papers.md` | Source anchors and estimand comparison |
| `evidence/` | Example-local corpus (A as calibration; B excluded) |
| `scripts/` | Build, calibrate, analyze, compare |
| `COMPARISON.md` | Calibration and A/B comparison write-up |
| `output/` | Generated Parquet + JSON reports (local; gitignored) |

## Quick start (once scripts land)

```shell
uv run python examples/andes-mmwr-drye-diabetes/scripts/run_example.py
```
