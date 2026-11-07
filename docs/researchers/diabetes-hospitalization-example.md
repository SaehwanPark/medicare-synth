---
title: "Diabetes–hospitalization example"
description: "End-to-end narrative of the 2021 Original Medicare FFS-like diabetes and any-inpatient MVP, including calibration anchors and what you may not infer."
permalink: /researchers/diabetes-hospitalization-example/
lang: en
lang_alternate: /ko/researchers/diabetes-hospitalization-example/
---

# Diabetes–hospitalization example

## Question

Before analyzing restricted Medicare files, how could we test code that compares
hospitalization occurrence among people with and without diabetes—without
claiming the synthetic answer is the Medicare answer?

## Cohort (artificial)

- **Setting:** 2021 Original Medicare fee-for-service–like population
- **Age:** 65+
- **Enrollment:** full-year Parts A/B under the project’s simplified enrollment rule
- **Context ID:** `mvp-2021-om-ffs-diabetes-ip`

These are synthetic records for methods development. They are not reconstructed
beneficiaries.

## Core tables and fields

Typical analyst-facing pieces in this MVP:

| Piece | Role in the example |
| --- | --- |
| Beneficiary demographics | Who is in the artificial cohort |
| Enrollment | Simplified full-year A/B membership |
| Chronic-condition indicators | Diabetes (`sp_diabetes`) and heart failure (`sp_chf`) flags |
| Inpatient claims | Presence of at least one inpatient claim (all-cause) |

Important definition: the outcome is **any inpatient admission**, not a
diabetes-principal diagnosis and not a diabetes-specific admission reason.
Heart failure is available as a stratifier/indicator, not a fully modeled
comorbidity system.

## Public anchors (selected, approximate)

The Phase 5 worlds share three frozen calibration targets:

| Target | Approximate value | Source framing |
| --- | --- | --- |
| Diabetes prevalence | 27.7% | 2018 CMS aggregate (transported into 2021 context) |
| Heart failure prevalence | 12% | 2022 CMS aggregate (transported) |
| Inpatient risk among people with diabetes | ~13% | Weaker industry prior (not a clean peer-reviewed Medicare estimand) |

Transport across years and populations is an explicit approximation. Matching
these moments is not a comprehensive 2021 Medicare benchmark.

## Illustration from stored Phase 5 worlds

All example worlds below use **6,000** simulated beneficiaries and the same
selected calibration targets. Free assumptions still differ.

| World (stored example) | Method highlight | Free background IP assumption | Inpatient claim records (stored) |
| --- | --- | --- | --- |
| Reference generator | Adjust generator parameters toward targets | P(IP \| no diabetes) = 0.04 | **404** |
| Alternate background risk | Same calibration targets | P(IP \| no diabetes) = 0.08 | **572** |

These counts come from the checked-in Phase 5 family summary
(`reports/phase5/world_family_summary.json`). They are illustrative stored
outcomes, not universal expected counts for every run configuration.

## What you can practice

- Grouping and merging beneficiary and claims-style tables
- Defining exposure (diabetes indicator) and outcome (any inpatient claim)
- Checking analytic units (person vs claim)
- Running simplistic associations as **code tests**
- Sensitivity checks when free assumptions change but calibration targets match

## What you cannot infer

- A real Medicare diabetes effect on hospitalization
- Validated predictive or risk-adjustment performance
- Diagnosis-specific admission patterns
- Causal effects, policy conclusions, or population-representative rates
- That Phase 6 independent evaluation is finished (it remains active)

## Reproduction (developer path)

There is no no-code calibrated download on the website. To reproduce the Phase 5
summary programmatically:

```shell
uv run python scripts/phase5_emit_worlds.py
```

For a literature-paired walkthrough (Andes MMWR prevalence in-domain vs Drye
admission rates out-of-domain), see the checked-in example:

```shell
uv run python examples/andes-mmwr-drye-diabetes/scripts/run_example.py
```

Details: [Calibrated worlds (developers)](../../developers/calibrated-worlds/) ·
phase docs under [`docs/phase5/`](https://github.com/SaehwanPark/medicare-synth/tree/main/docs/phase5) ·
[`examples/andes-mmwr-drye-diabetes/`](https://github.com/SaehwanPark/medicare-synth/tree/main/examples/andes-mmwr-drye-diabetes).

## Next

- [Interpreting results](../interpreting-results/)
- [Limitations](../limitations/)
- [Getting started](../getting-started/)
