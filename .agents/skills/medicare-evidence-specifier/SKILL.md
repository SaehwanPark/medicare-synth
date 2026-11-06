---
name: medicare-evidence-specifier
description: Turn CMS baseline, RKB, aggregate, or literature evidence into a bounded executable contract with grain, provenance, estimand semantics, and unknowns.
---

# Medicare Evidence Specifier

## When

Before changing schemas, field semantics, relationships, validators,
generation, Evidence IR, or calibration targets. Do not invent semantics from
names or treat scraped text as executable truth.

## Inputs

`_workspace/00_request.md`; pinned sources/manifests/snapshots or candidate
literature; existing schemas and known deviations.

## Workflow

1. Name file family / program / year / grain / keys / consumers.
2. Record source identity, version, location, checksum or stable citation.
3. For structural fields: provenance status and constraints.
4. For literature/aggregates: population, time, eligibility, variables,
   estimand, analysis, estimate+uncertainty, comparability, evidence role
   (train/holdout/diagnostic/excluded), review status.
5. Separate documented facts, baseline observations, assumptions, conflicts.
6. Define the narrow observable contract and minimal fixtures (no restricted data).
7. Write `_workspace/01_evidence_contract.md`; do not edit production code.

## Done when

Every semantic claim cites evidence or is labeled assumption; parent/child
grains named; unsupported fields/estimands fail explicitly rather than guess.

## Stop

Missing primary evidence/version; conflicts needing a product decision;
fixtures that would expose restricted material; fidelity claim the contract
cannot test; silent FFS/MA or year conflation.
