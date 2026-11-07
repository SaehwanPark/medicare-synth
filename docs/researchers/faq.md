---
title: "Researcher FAQ"
description: "Short answers about real patients, permissions, coding requirements, disease coverage, publication, realism, and where technical docs live."
permalink: /researchers/faq/
---

# Researcher FAQ

## Are these real Medicare patients?

No. Records are artificial and Medicare-like. The project does not reconstruct
real beneficiaries.

## Do I need CMS permission or files to try the demos?

Not for the built-in structural fixtures. Those run from the open-source package
without bundling restricted Medicare claims. If you later acquire official CMS
synthetic source files for other workflows, check that product’s acquisition and
redistribution terms separately. Code is Apache-2.0.

## Can I use it without coding?

You can **read** the researcher pages, worked example, and interpretation guides
without coding. Producing tables still needs a developer path or a collaborator
who exports files. There is no browser-based generator or one-click calibrated
download on the website today.

## Does it support my disease or year?

The calibrated MVP is pinned to a **2021 Original Medicare FFS-like, age 65+,
diabetes and any-inpatient** context (with heart failure as an indicator).
Arbitrary disease/year/outcome calibration is **not** a current product.

## Can I publish analyses of these data?

You can publish methods, software, and clearly labeled synthetic demonstrations.
Do **not** present synthetic associations or calibrated rates as empirical
Medicare findings. Cite limitations and evidence anchors.

## How realistic are admissions and diagnoses?

Structural relationships are checked. Selected summary rates can be targeted in
the MVP. Realistic longitudinal patterns, diagnosis-specific admissions, rich
comorbidity dependence, and validated subgroup behavior are **not** claimed.
Phase 6 evaluation remains active.

## Can I use synthetic results to justify a clinical conclusion?

No. That is **not a valid use**.

## Where do I find setup and technical details?

Start at the [developer hub](../../developers/), especially
[installation](../../developers/installation/),
[CLI](../../developers/cli/), and
[calibrated worlds](../../developers/calibrated-worlds/).
Canonical status lives in
[`ROADMAP.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/ROADMAP.md)
and [`SPEC.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/SPEC.md).
