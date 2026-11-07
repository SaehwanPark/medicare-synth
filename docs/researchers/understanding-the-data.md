---
title: "Understanding the data"
description: "Plain-language view of beneficiary, enrollment, condition, and claims-style records, and why patient count is not claim count."
permalink: /researchers/understanding-the-data/
lang: en
lang_alternate: /ko/researchers/understanding-the-data/
---

# Understanding the data

Medicare-like research files usually separate **who the person is**, **whether
they were enrolled**, **condition indicators**, and **service/claim events**.
Medicare-Synth mirrors that shape in its fixtures and MVP worlds so analysis
code can practice joins and definitions.

## A minimal relationship picture

```text
Beneficiary (one row per person in the extract)
    │
    ├── Enrollment (membership over time / year rules)
    ├── Chronic-condition indicators (e.g. diabetes, heart failure flags)
    └── Claims / encounters (zero, one, or many rows per person)
            └── optional claim lines / detail rows in richer fixtures
```

| Idea | Plain meaning |
| --- | --- |
| What one row represents | The **grain**: person, enrollment spell, claim, or line |
| How records connect | Shared identifiers (keys) linking persons to events |
| Administrative indicator | A coded flag or algorithm result—not identical to a clinician’s chart diagnosis |
| Claim presence | An event occurred in the synthetic extract—not proof of clinical necessity |

## Why counts differ

- **Patient count ≠ claim count.** One hospitalized person may contribute one or
  many inpatient rows depending on the generator and fixture rules.
- In the current MVP generator, a hospitalized simulated beneficiary has **at
  most one** inpatient claim in the simplified world—useful for code tests, not
  for realistic readmission trajectories.
- Condition indicators can be present without a matching diagnosis-coded
  inpatient stay; the MVP outcome is all-cause admission presence, not
  diabetes-principal hospitalization.

## Where technical field definitions live

For table families, keys, and source-to-release flow, use the developer
[data model](../../developers/data-model/) guide. For lineage statuses and what
validation does (and does not) prove, see
[provenance and validation](../../developers/provenance-and-validation/).

## Related

- [Diabetes–hospitalization example](../diabetes-hospitalization-example/)
- [Interpreting results](../interpreting-results/)
