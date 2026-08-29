---
title: "Data model and grains"
description: "Understand Medicare-Synth's table families, record grains, keys, and source-to-release flow before joining data."
permalink: /concepts/data-model/
---

# Data model and grains

Medicare-Synth keeps source file layouts visible while giving callers a typed,
relational view. Start with the grain of a table before writing a join or
expansion rule.

## Source to release

<div class="flow">pinned CMS source + RKB evidence
                ↓
        manifest-aware normalization
                ↓
 beneficiary, claim, line, event, and MBSF-shaped tables
                ↓
      validation → expansion → release export</div>

Every step retains the evidence and provenance boundary it can support. The
pipeline validates before broad synthesis and never silently repairs a source
anomaly.

## Table families

### Beneficiary and enrollment

The beneficiary summary is the parent record used by claim and event tables.
The ten MBSF segments attach beneficiary-year context:

| Segment | Table name |
| --- | --- |
| Base / enrollment | `mbsf_base_enrollment` |
| Chronic conditions | `mbsf_chronic_conditions` |
| Cost & use | `mbsf_cost_and_use` |
| Part D characteristics | `mbsf_part_d` |
| Other chronic conditions | `mbsf_other_chronic_conditions` |
| National Death Index | `mbsf_ndi` |
| Risk adjustment | `mbsf_risk_adjustment` |
| Part C / Medicare Advantage | `mbsf_part_c` |
| Fee-for-service utilization | `mbsf_ffs_utilization` |
| Part D PDE utilization | `mbsf_pde_utilization` |

These are not interchangeable rows. MBSF fields are generally beneficiary-year
or beneficiary-month measures; the segment contract and reference year determine
how they should be joined.

### Claims and events

| Family | Table name | Typical grain |
| --- | --- | --- |
| Beneficiary root | `beneficiary_summary` | one record per beneficiary |
| Carrier | `carrier_claims` | claim line/header, keyed by claim and line |
| Outpatient | `outpatient_claims` | claim header/event |
| Inpatient | `inpatient_claims` | facility stay/header |
| Skilled nursing facility | `snf_claims` | post-acute stay/header |
| Home health agency | `hha_claims` | care episode/header |
| Durable medical equipment | `dme_claims` | claim line/item |
| Hospice | `hospice_claims` | hospice stay/header |
| Prescription drug event | `pde_events` | dispensing event |

The claim families intentionally retain their source-specific fields. A single
beneficiary can have many claims and events, and a claim can have many lines.
Avoid flattening those relationships unless the analysis explicitly needs an
aggregate.

## Keys and relationships

- `BENE_ID` identifies the beneficiary parent and propagates to child tables.
- `CLM_ID` identifies a claim header/event and is checked against beneficiary
  membership.
- `(CLM_ID, LINE_NUM)` preserves carrier and line-item identity where present.
- `PDE_ID` identifies a prescription drug event.
- Reference dates and death dates enforce temporal ordering where the evidence
  contract supports it.

The validator reports orphaned keys, duplicate identities, and date inversions as
findings. It does not infer a missing parent or drop a duplicate for you.

## Expansion implications

Horizontal expansion copies connected beneficiary subgraphs and re-keys related
records together. Vertical expansion adds fields within an existing grain. If a
new feature would change a table's grain or relationship, it needs an explicit
schema decision rather than a convenience join.

For the public boundary and unsupported interpretations, read
[Limitations &amp; scope](../reference/limitations/).
