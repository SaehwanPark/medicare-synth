---
title: "Your first useful run"
description: "Learn the Medicare-Synth workflow by compiling, validating, and inspecting deterministic scenario fixtures."
permalink: /getting-started/first-run/
---

# Your first useful run

The fastest way to understand Medicare-Synth is to follow one fixture through
the same boundaries used for source-backed work:

<div class="flow">scenario compiler → typed tables → relational validator → reports / release bundle
       ↑                         provenance and limitations stay explicit ↓</div>

## 1. Validate a known-good cohort

```shell
uv run medicare-synth validate --scenario valid_baseline_cohort
```

This small cohort contains beneficiaries plus carrier, outpatient, inpatient,
prescription, post-acute, hospice, and MBSF-shaped records. A passing result
means the fixture satisfies the checks enabled by `validate` for that scenario;
it does not mean that the data represent real Medicare utilization.

## 2. Inspect the scenario catalog

```shell
uv run medicare-synth catalog
uv run medicare-synth catalog --json
```

The catalog currently contains three valid teaching fixtures and eighteen
intentional anomaly fixtures. Anomaly names make the broken contract explicit,
for example `invalid_orphaned_claim` and `invalid_temporal_inversion`.

## 3. Observe a deliberate failure

```shell
uv run medicare-synth validate --scenario invalid_orphaned_claim
```

The command should report `Valid: False` and one critical `REL-001` finding.
The claim points at a beneficiary that is absent from the parent table. This is
useful test data: a failing fixture confirms that the validator catches a
specific relationship violation rather than that the package is malfunctioning.

## 4. Call the Python API

```python
import medicare_synth as ms

slice_data = ms.ScenarioCompiler.valid_baseline_cohort()
report = ms.RelationalValidator().validate_slice(slice_data)

if not report.is_valid:
    raise ValueError(report.findings)

audit = ms.AuditEngine().audit_dataset(slice_data)
print(audit.overall_privacy_score)
```

Use the Python API when you need typed records, Polars tables, or a composed
workflow. Use the CLI when you need a repeatable shell step or a CI fixture.

## What to learn next

<div class="card-grid">
  <div class="card">
    <h3>Need command syntax?</h3>
    <p>The <a href="../guides/cli/">CLI reference</a> lists every subcommand, defaults, and output artifact.</p>
  </div>
  <div class="card">
    <h3>Need bigger or custom data?</h3>
    <p>The <a href="../guides/scenarios-and-validation/">scenario guide</a> covers catalog, audit, and expansion workflows.</p>
  </div>
  <div class="card">
    <h3>Need a shareable bundle?</h3>
    <p>The <a href="../guides/release-workflow/">release guide</a> explains manifests, checksums, and formats.</p>
  </div>
</div>
