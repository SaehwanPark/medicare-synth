# Phase 1 — Generator capability report

**Date:** 2026-11-06
**Verdict:** Phase 1 exit criteria **met** for the MVP conditional synthesizer.

## 1. What was verified

| Capability | Result | Evidence |
| --- | --- | --- |
| Deterministic reproduction | Pass | `test_generate_world_is_deterministic` |
| Structural validity | Pass | `test_generated_world_passes_structural_validation` |
| Controllable diabetes prevalence | Pass | recovery tests at n=4000 |
| Controllable `P(O1\|diabetes)` | Pass | recovery tests |
| Held-out `P(O1\|no diabetes)` recovery | Pass | `test_held_out_relationship_recovers_within_tolerance` |
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

1. **Binary, independent Bernoullis** per beneficiary — no comorbidity
   dependence, no temporal disease onset, no clustering, no provider effects.
2. **At most one IP claim** per hospitalized beneficiary in v0.
3. **No IP principal diagnosis** — O1 is all-cause claim presence only.
4. **No monthly MA panel** — Option B annual totals only.
5. **Synthetic known-truth only** — recovering declared params is not evidence
   agreement with CMS aggregates or literature.
6. **Tolerance 0.03** is an engineering gate for n≥4000, not a clinical
   precision claim.

## 4. Exit criteria checklist

| Criterion | Status |
| --- | --- |
| Pinned inputs/seeds reproduce outputs; structural checks pass | **Met** |
| Held-out synthetic ground-truth relationships recover within declared tolerances | **Met** (R3 on holdout partition) |
| Generated data show genuine statistical support (not clone-only variation) | **Met** |

## 5. Next (Phase 2)

Formalize one human-reviewed external finding as Evidence IR and execute it
against compatible synthetic tables—without treating Phase 1 known-truth
magnitudes as Medicare findings.
