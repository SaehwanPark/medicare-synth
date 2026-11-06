# Phase 2 — Evidence IR schema v0.1

**Status:** Implemented (`medicare_synth.evidence_ir`, `SCHEMA_VERSION = "0.1"`)
**Date:** 2026-11-06

## Purpose

A typed, reviewed object for a Medicare-only finding: what was measured, on
whom, when, how, with what uncertainty, and whether it may execute on supported
synthetic tables. Numeric agreement with synthetic data is a **comparison**, not
a Medicare result.

## Top-level fields

| Field | Required content |
| --- | --- |
| `schema_version` | `"0.1"` |
| `finding_id` | Stable id |
| `inventory_id` | Optional Phase 0 inventory link (e.g. `LIT-03`) |
| `source` | Type, identifier, title, URL, location anchor, citation |
| `population` | Program, years, age, geography, FFS rule, enrollment notes |
| `cohort` | Index/observation window, death policy, inclusion/exclusion notes |
| `estimand` | Type (`prevalence` \| `binary_risk` \| `rate`), numerator concept/algorithm, optional conditioning, scale, time unit for rates |
| `analysis` | Stratification, adjustment set, estimator label |
| `result` | Point estimate, optional SE/CI/N, unit |
| `role` | `pending_review` \| `calibration` \| `holdout` \| `diagnostic` \| `excluded` |
| `comparability` | Grade A/B/C/X/unassessed, assumptions, gaps, transport flag |
| `governance` | Review status, reviewer, timestamp, rationale, conflicts |
| `context_id` | Default `mvp-2021-om-ffs-diabetes-ip` |

## Vocabulary (v0.1)

**Concepts:** `diabetes`, `heart_failure`, `all_cause_inpatient`,
`eligible_beneficiaries`.

**Algorithms:** `mbsf_sp_diabetes_v1`, `mbsf_sp_chf_v1`, `ip_claim_presence_v1`,
`claims_diabetes_andes_mmwr_v1` (approximated), `unsupported`.

**FFS rules:** Option A/B/C plus `source_custom` (recorded then approximated).

## Compiler outputs

1. **Eligibility plan** — age floor, reference year, Option-B-like filters.
2. **Derivation plan** — concept/algorithm map onto tables.
3. **Estimator plan** — crude proportion, conditional proportion, or rate.
4. **Compatibility report** — `executable` flag; `error` / `warning` / `info`
   issues (year transport, age floor, algorithm approximation, unsupported
   planned-admission exclusions, adjusted models, etc.).

Under-specified rates (missing `time_unit`) and binary risks (missing
`conditioning`) fail at parse time. Unsupported semantics fail at compile time
with explicit errors—never silent guesses.

## Execution rules

- `governance.review_status` must be `accepted` unless `allow_unreviewed=True`.
- `role=excluded` never executes.
- Missing required tables → explicit error.
- Draft extraction helper (`draft_finding_from_fields`) always emits
  `review_status=draft`.

## Fixtures

| File | Role |
| --- | --- |
| `lit03_mmwr_diabetes_prevalence_2015.json` | Reviewed executable prevalence finding |
| `lit02_drye_admission_rate_unsupported.json` | Reviewed negative control (planned-admission rate refused) |

Packaged under `medicare_synth/fixtures/evidence_ir/`; mirrored in
`docs/phase2/fixtures/` and persisted outside git under
`~/data/medicare-synth/phase2/`.
