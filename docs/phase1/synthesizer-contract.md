# Phase 1 — Synthesizer contract

**Status:** Complete (2026-11-06)
**Context:** `mvp-2021-om-ffs-diabetes-ip`
**Module:** `medicare_synth.synthesis`

## Purpose

Provide an independently testable conditional generation interface that emits
coherent beneficiary subgraphs with **declared** diabetes prevalence and
inpatient hospitalization probabilities. This is synthetic known-truth for
engine verification—not Medicare calibration.

## Public API

| Symbol | Role |
| --- | --- |
| `ConditionalWorldParams` | Frozen Pydantic params (`n`, `seed`, prevalences, tolerance) |
| `generate_diabetes_ip_world(params)` | Deterministic world draw |
| `ConditionalWorld` | Tables + params + provenance |
| `estimate_world_relationships` | Recover R1–R4 from tables |
| `split_bene_ids` | Deterministic estimation / holdout partition |
| `relationships_within_tolerance` | Contract check helper |
| `unique_support_ratio` | Distinct `bene_id` / n |

## Tables emitted

`beneficiary_summary`, `mbsf_base_enrollment`, `mbsf_chronic_conditions`,
`inpatient_claims`.

Enrollment defaults match Phase 0 **Option B** (full-year A+B, HMO months 0).
Age ≥ 65 via DOB. Diabetes present coded as `sp_diabetes="1"` (collapse).

## Controllable known truth

| Parameter | Estimand |
| --- | --- |
| `diabetes_prevalence` | R1 `P(diabetes)` |
| `p_ip_given_diabetes` | R2 `P(O1\|diabetes)` |
| `p_ip_given_no_diabetes` | R3 `P(O1\|no diabetes)` (held-out recovery target) |

O1 = ≥1 inpatient claim with admission in `reference_year`.

## Determinism

Draws use `sha256(seed:stream:index)` unit uniforms. Same params → identical
Polars frames. No wall-clock or global RNG.

## Hard gates

Generated MVP tables must pass `RelationalValidator.validate_slice` for the
provided frames. Provenance status is `SYNTHESIZED`.

## Tolerances

Default absolute recovery tolerance: **0.03** at `n_beneficiaries ≥ 4000`
(overridable via `recovery_tolerance`).

## Explicit non-claims

- Does not replace CMS Syn Claims baseline fixtures.
- Does not implement Evidence IR or literature calibration.
- Does not add IP ICD, monthly HMO panels, or geography.
- `TabDatSynthAdapter` / `HorizontalExpander` remain structural tools and are
  **not** this contract.
