# Phase 3 — MVP evidence corpus freeze

**Status:** Complete (2026-11-06)

## Outputs

| Artifact | Path |
| --- | --- |
| Freeze record | [corpus-freeze.md](corpus-freeze.md) |
| Capability / exit report | [capability-report.md](capability-report.md) |
| Corpus + finding fixtures | [fixtures/](fixtures/) |
| Partition report | [`reports/phase3/corpus_partition_report.json`](../../reports/phase3/corpus_partition_report.json) |

## Runtime

- `medicare_synth.evidence_corpus` — load, verify checksums, freeze gate,
  partition execute
- Default corpus: `mvp-2021-om-ffs-diabetes-ip-corpus-v1`
- Sex-stratum holdout via `PopulationSpec.sex_codes` in Evidence IR
