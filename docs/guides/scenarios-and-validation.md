---
title: "Scenarios and validation"
description: "Use deterministic fixtures to exercise relationships, temporal rules, domain constraints, audits, and expansion."
permalink: /guides/scenarios-and-validation/
---

# Scenarios and validation

Scenarios are small, named data slices with stable expected behavior. They make
it possible to test a pipeline before restricted data is available and to keep
an edge case reproducible in a bug report or CI job.

## The catalog

The catalog has **21 entries**:

- **Three valid fixtures:** `valid_baseline_cohort`, `valid_chronic_subgroup`,
  and `valid_carrier_line_item`.
- **Eighteen anomaly fixtures:** each introduces one explicit broken contract,
  such as an orphaned claim, an inverted date, a negative utilization count, or
  an invalid MBSF code.

List names and metadata with:

```shell
uv run medicare-synth catalog --json
```

An anomaly is intentionally invalid. Do not “fix” it before using it in a test;
the expected finding is the point of the fixture.

## Validation loop

```shell
uv run medicare-synth validate --scenario valid_baseline_cohort
uv run medicare-synth validate --scenario invalid_orphaned_claim
```

The first command should produce a valid report with no findings. The second
should identify `REL-001`, because a carrier claim references a beneficiary that
is not present in the parent table.

Use `--output-dir` to persist `validation_report.json` for a release or CI job:

```shell
uv run medicare-synth validate \
  --scenario valid_baseline_cohort \
  --output-dir ./dist/validation
```

## What is checked

The validator separates findings by contract boundary:

| Boundary | Representative checks |
| --- | --- |
| Field | Types, widths, code formats, valid value sets, and numeric ranges. |
| Record | Required fields, uniqueness, conditional presence, and arithmetic relationships. |
| Relational | Beneficiary/claim foreign keys, line identity, and parent-child coverage. |
| Temporal | Claim start/end order, admission/discharge order, and mortality timing. |
| Administrative | Enrollment compatibility, claim setting, and source-specific rules. |
| Accounting | Non-negative payments, charges, deductibles, coinsurance, and utilization counts. |

The available checks grow with each supported domain, but every check should be
read as a structural contract. Passing a check does not imply clinical or
distributional realism.

## Audits and expansion

Run a quality/privacy audit on a fixture:

```shell
uv run medicare-synth audit --scenario valid_baseline_cohort
```

Scale a connected subgraph while preserving deterministic re-keying:

```shell
uv run medicare-synth expand \
  --mode horizontal \
  --scenario valid_baseline_cohort \
  --scale 2
```

Use vertical expansion when the goal is to add evidence-graded attributes to
existing rows. Read [Data model &amp; grains](../concepts/data-model/) before
joining or expanding tables so one-to-many relationships remain visible.
