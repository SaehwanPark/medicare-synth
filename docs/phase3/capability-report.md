# Phase 3 — Evidence corpus capability report

**Date:** 2026-11-06
**Verdict:** Phase 3 exit criteria **met**.

## Exit criteria

| Criterion | Status |
| --- | --- |
| Versioned registry with eligibility/compatibility grades | **Met** (`EvidenceCorpus` + entry grades/executability) |
| Train / held-out / diagnostic partitions + checksums | **Met** (3 / 1 / 2 + excluded 2; SHA-256) |
| Exclusion/conflict rationales retained | **Met** (excluded: LIT-02, MMD condition-hosp; diagnostic conflicts: CMS-AGG-05 HF 27→30) |
| Active findings executable or transparently approximated | **Met** (`assert_active_partition_support`) |
| Partitions frozen and reviewer-approved before calibration | **Met** (`frozen=true`, reviewer `phase3-corpus-freeze`) |

## Limitations

1. LIT-07 utilization prior is an industry white paper (grade B)—replace if a
   cleaner official O1-compatible aggregate is pinned later **without**
   unfreezing holdout casually (requires a new corpus version).
2. Holdout uses MMWR 2015 women stratum—year/age/algorithm transport remains.
3. No county/state geography targets in v1.
4. Corpus freeze is Milestone-C readiness, not calibration success.

## Next (Phase 4)

Reweighting + generator-parameter calibration APIs that read the **calibration**
partition only for fitting and reserve **holdout** for evaluation.
