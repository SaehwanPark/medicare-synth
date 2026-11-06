# Phase 3 — MVP evidence corpus freeze

**Status:** Complete (2026-11-06)
**Corpus ID:** `mvp-2021-om-ffs-diabetes-ip-corpus-v1`
**Runtime:** `medicare_synth.evidence_corpus`
**Artifact:** [`fixtures/mvp_2021_om_ffs_diabetes_ip_corpus_v1.json`](fixtures/mvp_2021_om_ffs_diabetes_ip_corpus_v1.json)
**Report:** [`reports/phase3/corpus_partition_report.json`](../../reports/phase3/corpus_partition_report.json)

## Freeze decision

Partitions are **frozen** before Phase 4 calibration. The holdout finding must
not be used for fitting. Excluded and diagnostic items are retained with
rationales (not deleted).

| Partition | Count | Finding IDs |
| --- | --- | --- |
| Calibration | 3 | `cms-agg03-diabetes-prev-ffs-2018`, `cms-agg04-hf-prev-ffs-2022`, `lit07-avalere-ffs-diabetes-ip-risk` |
| Holdout | 1 | `lit03-mmwr-diabetes-prev-2015-women` |
| Diagnostic | 2 | `lit03-mmwr-diabetes-prevalence-2015`, `cms-agg05-hf-algorithm-shift-2017` |
| Excluded | 2 | `lit02-drye-diabetes-unplanned-admission-rate-2012`, `excluded-mmd-diabetes-condition-hosp` |

## Targets (anchored)

| ID | Estimate | Grade | Executability |
| --- | --- | --- | --- |
| CMS-AGG-03 diabetes prev 2018 | 0.277 | B | approximated (year transport) |
| CMS-AGG-04 HF prev 2022 | 0.12 | B | approximated (year/preliminary) |
| LIT-07 Avalere P(IP\|diabetes) | 0.13 | B | executable (weak industry prior) |
| LIT-03 women 2015 (holdout) | 0.296 | B | approximated (year/age/sex/algorithm) |

## Integrity

- Each registry entry stores `relative_path` + SHA-256 of the finding JSON.
- `verify_corpus_checksums` / `ensure_corpus_checksums` fail on tamper.
- `freeze_corpus` / `replace_entry` refuse mutation when `frozen=true`.
- Active partitions (calibration + holdout) must be executable or transparently
  approximated (`assert_active_partition_support`).

## Non-claims

Synthetic agreement with these targets is **not** a Medicare finding and does
not authorize publishing calibrated synthetic estimates as empirical results.
