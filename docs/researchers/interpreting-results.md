---
title: "Interpreting results"
description: "Separate structural validity, match to selected published rates, methods realism, and real-world Medicare inference."
permalink: /researchers/interpreting-results/
lang: en
lang_alternate: /ko/researchers/interpreting-results/
---

# Interpreting results

Synthetic outputs can look like analysis results. Keep four kinds of “validity”
separate:

| Level | Question | Current project basis |
| --- | --- | --- |
| 1. Structure | Do tables link and pass format/relationship checks? | Strong for fixtures and MVP gates |
| 2. Selected moments | Do chosen summary rates land near published anchors? | Bounded Phase 5 calibration (graded, not proof of generality) |
| 3. Workflow realism | Is the data realistic enough for a stated analysis workflow? | Needs Phase 6 independent evaluation (active) |
| 4. Population inference | Can we treat results as Medicare truth? | **Not a project claim** |

## Safe to say / not safe to say

| Safe to say | Not safe to say |
| --- | --- |
| “This fixture failed a foreign-key check, so my join code should handle the error.” | “Medicare has this orphan-claim rate.” |
| “Under these synthetic assumptions, my cohort definition returned N people.” | “Therefore N is the Medicare cohort size.” |
| “Two worlds matched the same calibration targets but differed on free background risk, and my estimate moved.” | “The true Medicare effect lies between those estimates.” |
| “Calibration reduced error on the selected training moments.” | “The model is clinically validated / population-representative.” |
| “I used synthetic data to debug code before DUAs and restricted extracts.” | “Synthetic performance justifies a clinical or policy conclusion.” |

## Simulated parameter truth vs empirical Medicare truth

In known-truth experiments, the generator’s parameters are under the analyst’s
control. Recovering those parameters tests the toolchain. It does **not** mean
the same numbers exist in Medicare.

Public calibration anchors in the MVP deliberately mix source years and evidence
strength. Treat them as contextual targets with disclosed transport assumptions.

## MVP gaps that affect interpretation

- Diabetes and heart failure drawn independently in the MVP (no robust comorbidity dependence)
- No robust multiyear disease trajectories or provider effects
- All-cause inpatient presence, not diagnosis-specific admission
- No claim that subgroup performance or confounding structure is realistic

Details: [limitations](../limitations/) ·
[worked example](../diabetes-hospitalization-example/).
