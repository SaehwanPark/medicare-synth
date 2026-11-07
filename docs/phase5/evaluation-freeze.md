# Phase 5 — Evaluation freeze

**Freeze ID:** `mvp-2021-om-ffs-diabetes-ip-eval-freeze-v1`
**API:** `medicare_synth.evaluation.load_evaluation_freeze`
**Pinned before:** further iterative packaging / fitting on this family

## Roles

| Partition | Role |
| --- | --- |
| Calibration | Fit-allowed |
| Holdout | Evaluate-only (never fit) |
| Diagnostic | Evaluate-only (never fit) |
| Excluded | Not used |

## Gates

| Gate | Kind |
| --- | --- |
| `structural_validity` | Hard |
| `holdout_isolation` | Hard |
| `calibration_mae` | Graded (training diagnostic) |
| `holdout_mae` | Reporting-only (no selection / retuning in Phase 5) |
| `reweight_nondegeneracy` | Graded (ESS / weight collapse warnings) |

`assert_fit_roles_allowed` refuses holdout and diagnostic IDs.
`refuse_unfreeze` blocks silent protocol mutation; a new freeze ID requires
human approval.

## Phase boundary

Phase 5 freezes this protocol and packages worlds. Phase 6 runs independent
evaluation claims against holdout / workflows without indefinite retuning on
the same holdout set.
