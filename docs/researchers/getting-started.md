---
title: "Getting started for researchers"
description: "Honest access paths into Medicare-Synth: reading without install, analyst export handoff, or full developer setup."
permalink: /researchers/getting-started/
---

# Getting started for researchers

Pick the path that matches how you work. Researcher-friendly public downloads of
calibrated MVP datasets are **not** shipped as a website product today; do not
expect a one-click calibrated CSV from these pages.

## Path A — Reading and exploration (no install)

1. Read [what you can do](../what-you-can-do/) and the
   [diabetes–hospitalization example](../diabetes-hospitalization-example/).
2. Skim [understanding the data](../understanding-the-data/) for person vs claim
   grain.
3. Read [interpreting results](../interpreting-results/) and
   [limitations](../limitations/) before using any numbers in a proposal or talk.

You can learn whether the tool is relevant without writing Python.

## Path B — Analyst handoff (tables in R, Stata, Python, …)

1. Ask a colleague or collaborator who can run the package to export a **valid
   scenario fixture** (structural teaching data) via the
   [export and release](../../developers/export-and-release/) workflow.
2. Import the resulting CSV or Parquet files into your analysis environment.
3. Treat the files as artificial structure for code practice. They are not a
   calibrated research MVP unless your collaborator also runs the separate
   Phase 5 worlds workflow and clearly labels that output.

If a separately packaged sample dataset is later approved, this page will list
the verified artifact path, supported use, and checksums. That path is **not**
documented as existing functionality today.

## Path C — Developer setup

Install locally and use the CLI/API:

- [Installation](../../developers/installation/)
- [First useful run](../../developers/first-run/)
- [Calibrated worlds](../../developers/calibrated-worlds/)

## Responsible use

Synthetic cohorts—even when adjusted toward selected published statistics—cannot
support defensible real-Medicare prevalence, effect, or policy claims. See the
[FAQ](../faq/) for common boundaries.
