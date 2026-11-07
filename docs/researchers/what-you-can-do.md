---
title: "What you can do"
description: "Honest capability matrix for Medicare-Synth research tasks: available, limited prototype, planned, and not a valid use."
permalink: /researchers/what-you-can-do/
---

# What you can do

Status labels are plain English. **Available** means demonstrated today.
**Limited prototype** means a pinned experimental workflow with disclosed
assumptions. **Planned** is roadmap-only. **Not a valid use** is outside project
claims even if someone could run code that looks similar.

| Research task | What works today | Technical assistance needed | Current limitations | Verification reference |
| --- | --- | --- | --- | --- |
| Study Medicare-like file structure, keys, and joins | **Available** via deterministic fixture workflows | Install/CLI help, or a colleague who can export tables | Teaching fixtures, not a full CMS extract | [Scenarios & validation](../../developers/scenarios-and-validation/); catalog CLI |
| Run basic code and cohort-definition exercises | **Available** with local setup | Python/`uv` or exported tables for R/Stata | Fixtures are small and structural | [Getting started](../getting-started/); [first run](../../developers/first-run/) |
| Export ordinary fixture-based CSV/Parquet bundles | **Available** through developer tooling | Someone to run export and share files | Not a calibrated research MVP download | [Export and release](../../developers/export-and-release/) |
| Generate a 2021 FFS diabetes–any-inpatient MVP world | **Limited prototype** (Python API / Phase 5 scripts) | Developer familiar with the synthesis/worlds APIs | Selected moments only; independent evaluation still Phase 6 | [Worked example](../diabetes-hospitalization-example/); [calibrated worlds](../../developers/calibrated-worlds/); `reports/phase5/` |
| Compare multiple worlds under alternative assumptions | **Limited prototype** | Same as above | Same targets can yield different free-structure outcomes | Phase 5 family summary (e.g. 404 vs 572 inpatient claims at n=6,000) |
| Choose any disease, year, and outcome | **Not supported** as a calibrated product | — | MVP is pinned to one context | [ROADMAP](https://github.com/SaehwanPark/medicare-synth/blob/main/ROADMAP.md) |
| Download calibrated datasets in one click from the website | **Not supported** | — | No hosted calibrated CSV product | This matrix; plan non-goals |
| Make population, causal, clinical, or policy claims | **Not a valid use** | — | Synthetic outputs are not Medicare findings | [Limitations](../limitations/); [interpreting results](../interpreting-results/) |

## How to read “adjusted toward published statistics”

For the MVP, three selected public quantities are used as calibration targets
(with mismatched source years and uneven evidence strength). Matching those
moments improves contextual plausibility for methods work. It does **not** mean
the synthetic joint distribution equals Medicare, that subgroups are validated,
or that Phase 6 research-utility evaluation is complete.

## Related pages

- [Diabetes–hospitalization example](../diabetes-hospitalization-example/)
- [FAQ](../faq/)
- [Developer hub](../../developers/)
