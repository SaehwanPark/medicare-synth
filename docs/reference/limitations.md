---
title: "Limitations and scope"
description: "Read the non-goals, source boundaries, and claims that Medicare-Synth deliberately does not make."
permalink: /reference/limitations/
---

# Limitations and scope

Medicare-Synth is a development and research-fixture system. It is not a
replacement for restricted CMS data and it is not an inferential model of the
Medicare population.

## What a release can support

- prototyping schemas, joins, episodes, and analytic code;
- testing code against valid and intentionally invalid records;
- exercising deterministic export, checksum, and CI workflows;
- teaching contemporary Medicare-shaped file relationships; and
- evaluating structural, relational, temporal, and declared accounting rules.

## What a release cannot establish

- national or subgroup-level population estimates;
- clinical effectiveness, policy effects, or causal conclusions;
- complete distributional, longitudinal, or provider-level fidelity;
- formal privacy guarantees solely because records are synthetic; or
- availability of a field, file, or relationship in a restricted CMS product
  without checking that product's current documentation.

<div class="callout callout-warning">
  <div class="callout-title">Use the right evidence</div>
  Structural validity is necessary for a useful fixture, but it is not evidence that a synthetic distribution matches Medicare. Cite the source manifest, evidence snapshot, validation report, and limitations profile with any published artifact.
</div>

## Current source boundary

- The default baseline is the official **2021 CMS Synthetic Claims** collection,
  identified as `CMS-2021-SYN-CLAIMS`.
- The additive **2022 CMS Synthetic Medicare Claims PUF** path is bounded to the
  beneficiary and carrier files. Other PUF claim families and unsupported years
  are outside that importer contract.
- Raw source files are acquired into ignored `data/` directories. Tracked
  manifests and evidence snapshots preserve retrieval metadata and checksums.

## Generated values and unknowns

Vertical synthesis, horizontal re-keying, scenario generation, and external
calibration each make different claims. The provenance status and release
profile must say which method produced a field. If evidence is missing or
conflicting, the project should preserve the uncertainty instead of silently
choosing a meaning.

## License and redistribution

The code is licensed under Apache-2.0. CMS synthetic source material is acquired
through manifest verification rather than redistributed in this repository. A
release owner is responsible for checking the source terms and publishing the
manifest, checksums, and disclosures that accompany any bundle.
