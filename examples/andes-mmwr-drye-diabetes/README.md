# Andes → Drye diabetes example

End-to-end researcher workflow for Medicare-Synth:

1. **Paper A (in-domain):** Andes et al., *MMWR* 2019 — Medicare FFS diabetes
   prevalence 31.6% (2015, age ≥68). Inventory **LIT-03**.
2. **Paper B (out-domain):** Drye et al., *Medical Care* — acute unplanned
   admission rates among Medicare FFS with diabetes (2012; 41.4 / 100 PY).
   Inventory **LIT-02** (excluded on MVP schema).

The example **calibrates** a synthetic 2021 OM FFS–like diabetes→IP world to
**A**, exports Parquet, replicates **A** via Evidence IR, and documents why
**B**’s exact estimand is out of domain (with a diagnostic all-cause IP
approximation that is **not** a Drye replication).

> Synthetic agreement is **not** a Medicare finding. Do not publish these
> numbers as empirical results about beneficiaries.

## Quick start

```shell
uv run python examples/andes-mmwr-drye-diabetes/scripts/run_example.py
```

Artifacts land under `output/` (gitignored): Parquet tables plus JSON reports.
`COMPARISON.md` is regenerated in-tree for the write-up.

## Layout

| Path | Role |
| --- | --- |
| `papers.md` | Source anchors and estimand comparison |
| `evidence/` | Example-local corpus (A calibration; B excluded) |
| `scripts/` | Build, calibrate, analyze, compare |
| `COMPARISON.md` | Calibration and A/B comparison write-up |
| `output/` | Generated Parquet + JSON (local only) |

## What this demonstrates

- Generating structurally valid MVP tables and writing **Parquet**
- Level **C** calibration to a literature prevalence finding (paper A)
- Holdout isolation (Andes women stratum is evaluate-only)
- Honest refusal of an unsupported utilization estimand (paper B)
- Eligibility-aligned calibration moments (age ≥68 matches Evidence IR)

## What this does not claim

- Recovery of real Medicare beneficiaries or 2015/2012 population truth
- That Drye’s 41.4/100 PY equals MVP `P(IP|diabetes)`
- Replacement of the frozen Phase 3/5 MVP corpus (`mvp-2021-om-ffs-diabetes-ip-corpus-v1`)
