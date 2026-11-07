---
title: "Documentation portal"
description: "Explore Medicare-like synthetic data for research preparation: what works today, the diabetes–hospitalization example, and clear limits on inference."
permalink: /
---

<section class="hero">
  <div class="eyebrow">Research preparation with Medicare-like synthetic data</div>
  <h1>Explore ideas before restricted Medicare access.</h1>
  <p class="lede">Medicare-Synth helps researchers work with artificial, Medicare-shaped datasets for structure checks and methods testing. For one limited study setting, it can adjust synthetic populations toward selected published statistics. It is not a source of Medicare population estimates.</p>
  <div class="hero-actions">
    <a class="button" href="{{ '/researchers/' | relative_url }}">Explore as a researcher</a>
    <a class="button secondary" href="{{ '/researchers/diabetes-hospitalization-example/' | relative_url }}">See the worked example</a>
  </div>
</section>

<div class="callout callout-warning">
  <div class="callout-title">Not Medicare findings</div>
  Structural validity and agreement with selected published rates do not authorize citing synthetic results as empirical Medicare statistics, clinical conclusions, or policy evidence.
</div>

## What you can do today

| Status | Meaning |
| --- | --- |
| **Works today** | Study file structure and joins; run fixture-based code exercises; export ordinary teaching CSV/Parquet with developer help |
| **Limited prototype** | Generate and compare 2021 FFS-like diabetes / any-inpatient worlds adjusted toward three selected public targets |
| **Not intended** | One-click calibrated website downloads; any disease/year as a calibrated product; population, causal, or clinical claims |

Full matrix: [What you can do](researchers/what-you-can-do/).

## Three researcher tasks

<div class="card-grid">
  <div class="card">
    <h3>Explore available data</h3>
    <p>Learn how person, enrollment, condition, and claims-style records connect—and why patient count is not claim count.</p>
    <p><a href="{{ '/researchers/understanding-the-data/' | relative_url }}">Understanding the data →</a></p>
  </div>
  <div class="card">
    <h3>Plan an analysis</h3>
    <p>Walk the supported diabetes and any-inpatient example before you invest in restricted extracts.</p>
    <p><a href="{{ '/researchers/diabetes-hospitalization-example/' | relative_url }}">Worked example →</a></p>
  </div>
  <div class="card">
    <h3>Compare assumptions</h3>
    <p>Same selected calibration targets can still produce different outcomes when free assumptions change.</p>
    <p><a href="{{ '/researchers/interpreting-results/' | relative_url }}">Interpreting results →</a></p>
  </div>
</div>

## Flagship example (stored Phase 5 illustration)

Artificial **2021 Original Medicare FFS-like** adults aged 65+, with diabetes and
heart-failure indicators and **any** inpatient admission (not
diagnosis-specific). Selected anchors include approximate diabetes prevalence
27.7% (2018 source), heart failure 12% (2022 source), and ~13% inpatient risk
among people with diabetes (weaker industry prior).

In the checked-in Phase 5 family at 6,000 simulated beneficiaries, two worlds
that share those calibration targets show **404** versus **572** inpatient claim
records under different free background-risk assumptions. Use that contrast to
practice sensitivity—not to bound Medicare truth.

→ [Diabetes–hospitalization example](researchers/diabetes-hospitalization-example/)

## How to begin

- **Reading path:** no install—start with [For researchers](researchers/) and the
  [FAQ](researchers/faq/).
- **Analyst path:** ask a collaborator to export fixture tables; import CSV/Parquet
  into R, Stata, or Python ([getting started](researchers/getting-started/)).
- **Developer path:** [install locally](developers/installation/) and use the CLI/API.

## Building or extending the toolkit?

<div class="callout callout-note">
  <div class="callout-title">Developer documentation</div>
  Installation, CLI, scenarios, data model, calibrated-world reproduction, and contribution guides live under <a href="{{ '/developers/' | relative_url }}">For developers</a>. Canonical technical state remains in the repository root (<code>SPEC.md</code>, <code>ARCHITECTURE.md</code>, <code>ROADMAP.md</code>).
</div>

## Scope notice

Phases 0–5 are complete for the pinned MVP; Phase 6 independent evaluation is
**active**. Read [limitations](researchers/limitations/) before using any release
or synthetic summary in a manuscript or proposal.
