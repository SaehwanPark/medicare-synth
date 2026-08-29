---
title: "Documentation portal"
description: "Start here to install Medicare-Synth, run a deterministic fixture, and understand its evidence and validation boundaries."
permalink: /
---

<section class="hero">
  <div class="eyebrow">Open-source Medicare data infrastructure</div>
  <h1>Build against Medicare-shaped data before restricted access.</h1>
  <p class="lede">Medicare-Synth compiles provenance-backed synthetic datasets and deterministic research fixtures for schema work, pipeline development, methods testing, and teaching.</p>
  <div class="hero-actions">
    <a class="button" href="{{ '/getting-started/installation/' | relative_url }}">Install and run it</a>
    <a class="button secondary" href="{{ '/getting-started/first-run/' | relative_url }}">See the first useful run</a>
  </div>
</section>

<div class="callout callout-note">
  <div class="callout-title">What this project promises</div>
  The fixtures are deterministic, relationally checked, and explicit about their source lineage. They are for software and research workflow development—not estimates of the Medicare population.
</div>

## ⚡ First value in five minutes

You do not need CMS files, a database, cloud credentials, or a service account to
try the built-in scenarios:

1. Install Python 3.13+ and [`uv`](https://docs.astral.sh/uv/).
2. Clone the repository and run `uv sync`.
3. Validate the known-good baseline fixture:

   ```shell
   uv run medicare-synth validate --scenario valid_baseline_cohort
   ```

4. Run the same validator against an intentional orphaned-claim fixture and
   inspect the one expected finding:

   ```shell
   uv run medicare-synth validate --scenario invalid_orphaned_claim
   ```

You should see `Valid: True` for the first command and `Valid: False` with one
`REL-001` finding for the second. The [first-run guide](getting-started/first-run/)
explains what those results mean.

## Choose a path

<div class="card-grid">
  <div class="card">
    <h3>🚀 New to the repository?</h3>
    <p>Install the package, run a fixture, and learn the source-to-validation flow.</p>
    <p><a href="{{ '/getting-started/installation/' | relative_url }}">Start with installation →</a></p>
  </div>
  <div class="card">
    <h3>⌨️ Building a pipeline?</h3>
    <p>Use the CLI, Python API, scenario catalog, and focused validation checks.</p>
    <p><a href="{{ '/guides/cli/' | relative_url }}">Open the CLI reference →</a></p>
  </div>
  <div class="card">
    <h3>📦 Need shareable artifacts?</h3>
    <p>Export checksummed CSV, Parquet, manifests, reports, and SQL reference DDL.</p>
    <p><a href="{{ '/guides/release-workflow/' | relative_url }}">Package a release →</a></p>
  </div>
  <div class="card">
    <h3>🔍 Reviewing fidelity?</h3>
    <p>Trace fields to evidence and separate structural validity from population claims.</p>
    <p><a href="{{ '/concepts/provenance-and-validation/' | relative_url }}">Read the boundary →</a></p>
  </div>
</div>

## At a glance

<div class="stats-grid">
  <div class="stat"><span class="stat-number">19</span><p>implemented domain tables</p></div>
  <div class="stat"><span class="stat-number">21</span><p>deterministic catalog scenarios</p></div>
  <div class="stat"><span class="stat-number">2</span><p>supported release formats: CSV and Parquet</p></div>
  <div class="stat"><span class="stat-number">0</span><p>population estimates claimed</p></div>
</div>

| Boundary | Current contract |
| --- | --- |
| Default baseline | CMS 2021 Synthetic Claims (`CMS-2021-SYN-CLAIMS`) |
| Additional source path | Bounded 2022 CMS Synthetic Medicare Claims PUF beneficiary/carrier slice |
| Core stack | Python 3.13+, Pydantic v2, Polars, PyArrow |
| License | Apache-2.0 for code; CMS synthetic source is acquired by checksummed manifest |
| Primary outputs | Validated scenario slices, versioned release bundles, provenance and limitation profiles |

## What the package does

### Preserve a documented baseline

The repository records source manifests and pinned ResDAC Knowledge Base (RKB)
evidence snapshots. Raw CMS files are acquired into ignored `data/` directories;
the tracked manifests preserve URLs, versions, grains, row counts, and checksums.

### Validate relationships before expansion

Pydantic models handle record-level contracts. Polars and PyArrow support table
validation, foreign-key checks, temporal rules, code formats, accounting bounds,
and release I/O. A validator finding is reported rather than silently repaired.

### Generate reproducible fixtures

Named scenarios cover valid workflows and intentional anomalies. Vertical
expansion adds evidence-graded fields; horizontal expansion re-keys connected
beneficiary subgraphs. Seeds, manifests, and explicit provenance keep results
reproducible.

## Documentation map

- **Getting started:** [installation](getting-started/installation/) and the
  [first useful run](getting-started/first-run/).
- **Using the package:** [CLI reference](guides/cli/),
  [scenarios and validation](guides/scenarios-and-validation/), and the
  [release workflow](guides/release-workflow/).
- **Understanding the data:** [data model and grains](concepts/data-model/),
  [provenance and validation](concepts/provenance-and-validation/), and
  [limitations](reference/limitations/).
- **Contributing:** [contributor guide](contributing/) and the
  [canonical project documents](reference/project-documents/).

## Scope notice

Medicare-Synth supports development, testing, education, and feasibility work.
Structural and relational validity does not establish clinical validity,
distributional fidelity, formal privacy guarantees, or national
representativeness. Do not cite synthetic outputs as empirical Medicare
statistics. Read the complete [limitations and scope statement](reference/limitations/)
before using a release.
