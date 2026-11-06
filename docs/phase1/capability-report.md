# Phase 1 — Generator capability report

**Date:** 2026-11-06
**Verdict:** Phase 1 exit criteria **met** for the MVP conditional synthesizer.

## 1. What was verified

| Capability | Result | Evidence |
| --- | --- | --- |
| Deterministic reproduction | Pass | `test_generate_world_is_deterministic` |
| Structural validity | Pass | `test_generated_world_passes_structural_validation` (see limits §3) |
| Controllable diabetes prevalence | Pass | multi-seed recovery at n=8000 |
| Controllable `P(O1\|diabetes)` | Pass | multi-seed recovery |
| Controllable HF prevalence | Pass | `test_hf_prevalence_controllable` (independent of diabetes) |
| Held-out `P(O1\|no diabetes)` recovery | Pass | partition LLN on known truth (`test_held_out_…`) |
| Genuine support (not clone-only) | Pass | clone locked to seed prevalence; conditional hits new target |
| Option B enrollment / age ≥65 | Pass | `test_option_b_enrollment_and_age_floor` |

## 2. Characterization of prior expansion paths

| Path | Behavior | Statistical support for MVP conditionals |
| --- | --- | --- |
| `TabDatSynthAdapter` | Index/seed numeric features | **No** — independent of diabetes/IP |
| `VerticalExpander` | Adds SYN_* on beneficiary only | **No** conditional association |
| `HorizontalExpander` | Re-keys subgraph clones | **No** — prevalence locked to seed; cannot retarget |

These remain useful for structural load / fixture scaling. They are not the
Phase 1 synthesizer.

## 3. Limitations (honest)

1. **Binary, independent Bernoullis** per beneficiary — HF is independently
   drawable but not jointly dependent on diabetes; no temporal onset,
   clustering, or provider effects.
2. **At most one IP claim** per hospitalized beneficiary in v0.
3. **No IP principal diagnosis** — O1 is all-cause claim presence only.
4. **No monthly MA panel** — Option B annual totals only.
5. **Synthetic known-truth only** — recovering declared params is not evidence
   agreement with CMS aggregates or literature.
6. **Tolerance** uses `max(0.03, 3.5·SE)` and multi-seed checks at n≥8000 — an
   engineering gate, not clinical precision.
7. **`validate_slice` on MVP frames** does not exercise DOB/death checks that
   require `clm_from_dt`/`srvc_dt`; admission≤discharge is checked.
8. **Holdout recovery** is a deterministic partition LLN check on the same
   generative process—not a fitted-model generalization test.

## 4. Exit criteria checklist

| Criterion | Status |
| --- | --- |
| Pinned inputs/seeds reproduce outputs; structural checks pass | **Met** |
| Held-out synthetic ground-truth relationships recover within declared tolerances | **Met** (R3 on holdout; SE-aware gate; multi-seed) |
| Generated data show genuine statistical support (not clone-only variation) | **Met** |

## 5. Next (Phase 2)

Formalize one human-reviewed external finding as Evidence IR and execute it
against compatible synthetic tables—without treating Phase 1 known-truth
magnitudes as Medicare findings.
