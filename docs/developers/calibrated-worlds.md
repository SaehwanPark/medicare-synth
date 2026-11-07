---
title: "Calibrated worlds"
description: "Reproduce the Phase 5 MVP multi-world family, distinguish fixture exports from world emission, and access tables without treating reports as CSV releases."
permalink: /developers/calibrated-worlds/
---

# Calibrated worlds

This guide closes the discoverability gap for the pinned MVP
`mvp-2021-om-ffs-diabetes-ip` across Phases 1–5. It is a **programmatic**
workflow. It is not a browser download and not a substitute for restricted
Medicare analysis.

## Fixture export vs research MVP emission

| Workflow | What it produces | Primary entry |
| --- | --- | --- |
| Scenario fixtures | Deterministic teaching/valid/invalid slices; CSV/Parquet via CLI export | `medicare-synth export` · [export guide](../export-and-release/) |
| Phase 5 world family | Calibrated multi-world package + reports/manifests under `reports/phase5/` | `scripts/phase5_emit_worlds.py` · `medicare_synth.worlds` |

Do not equate a fixture release bundle with a calibrated MVP world. The Phase 5
script primarily writes **JSON reports and manifests**, not a documented
one-click calibrated CSV product.

## APIs

- Generation primitives: `medicare_synth.synthesis` (conditional known-truth
  worlds for the pinned context)
- Multi-world packaging: `medicare_synth.worlds.emit_world_family`,
  `emit_world`, `analyze_world_moments`
- Access tables from an emitted world: `WorldRelease.tables()` (Polars frames);
  Level B worlds may also carry `weights`
- Identical analysis across worlds: `analyze_world_moments(tables, corpus,
  weights=...)`

## Reproduce the Phase 5 summary

```shell
uv run python scripts/phase5_emit_worlds.py
```

Expected artifacts (among others):

- `reports/phase5/world_family_summary.json`
- `reports/phase5/evaluation_freeze.json`
- per-world calibration manifests

Shared calibration targets (frozen corpus / evaluation freeze):

| Finding | Moment |
| --- | --- |
| CMS-AGG-03 | diabetes prevalence 0.277 (2018 source framing) |
| CMS-AGG-04 | HF prevalence 0.12 (2022 source framing) |
| LIT-07 | P(IP \| diabetes) 0.13 (weak industry prior) |

Holdout findings are evaluate-only and must not enter fitting.

## Example: inspect one world in Python

```python
from medicare_synth.calibration import load_default_corpus
from medicare_synth.evaluation import load_evaluation_freeze
from medicare_synth.worlds import emit_world_family, analyze_world_moments

corpus, path = load_default_corpus()
freeze = load_evaluation_freeze(corpus=corpus)
family = emit_world_family(
  corpus=corpus,
  corpus_path=path,
  freeze=freeze,
  n_beneficiaries=6000,
  seed=42,
)
world = family.worlds[1]  # e.g. reference generator world
tables = world.tables()
cal_report, hold_report = analyze_world_moments(
  tables, corpus, weights=world.weights
)
print(
  world.world_id,
  world.structural_valid,
  cal_report.mean_absolute_error,
  hold_report.mean_absolute_error,
)
```

If you need CSV/Parquet for downstream tools, export from the in-memory tables
with your own explicit step after generation. Confirm any shared release path
against current tests before documenting it as a supported product workflow.

## Simplifying assumptions (disclosed)

- Diabetes and HF drawn as limited/independent Bernoulli structure in the MVP
  generator
- Year transport on CMS aggregate targets into the 2021 FFS-like context
- LIT-07 treated as a weak prior inside the frozen corpus
- Free `P(IP|no diabetes)` differs across worlds by design
- At most one inpatient claim per hospitalized simulated beneficiary in the MVP
  generator; all-cause admission, not diagnosis-specific

## Evaluation boundary

Structural validity is a hard gate. Calibration MAE is graded on the training
partition. Holdout isolation is enforced. **Phase 6** owns independent
research-utility and held-out evaluation claims; do not advertise Phase 5
calibration success as general clinical realism.

Source records:

- [`docs/phase5/`](https://github.com/SaehwanPark/medicare-synth/tree/main/docs/phase5)
- [`reports/phase5/`](https://github.com/SaehwanPark/medicare-synth/tree/main/reports/phase5)
- Earlier phases: `docs/phase0` … `docs/phase4` (repository source; not Jekyll
  published)

Researcher narrative:
[diabetes–hospitalization example](../../researchers/diabetes-hospitalization-example/).
