---
name: medicare-evidence-specifier
description: Turn Medicare source evidence into a bounded executable behavior contract with explicit grain, provenance, relationships, constraints, and unknowns.
---

# Medicare Evidence Specifier

## When to Use

- Use before implementing or changing Medicare schemas, field semantics,
  relationships, normalization, validators, generation, or scenarios.
- Use when documentation, baseline records, and assumptions may disagree.
- Do not use to invent semantics from field names or to treat extracted
  documentation as automatically executable truth.

## Required Inputs

- `_workspace/00_request.md`.
- Pinned source documents, evidence bundles, baseline records, or manifests
  applicable to the slice.
- Existing schemas, architecture decisions, tests, and known deviations.

## Workflow

1. Identify file family, data year, release, record grain, keys, cardinalities,
  and consumers.
2. Record evidence with source identity, version, location, and retrieval or
  checksum provenance where available.
3. Classify each relevant value as preserved, normalized, re-keyed, derived,
  imputed, synthesized, externally calibrated, or scenario-generated.
4. Define types, null semantics, code domains, temporal rules, relationships,
  arithmetic constraints, deterministic ordering, and expected failures.
5. Separate documented semantics, observed baseline behavior, explicit
  assumptions, and unresolved conflicts.
6. Define the narrow observable contract and minimum fixtures without copying
  restricted, sensitive, or unnecessary data.
7. Write `_workspace/01_evidence_contract.md`; do not edit production code.

## Outputs

- `_workspace/01_evidence_contract.md` containing sources, scope, grain,
  behavior, provenance, constraints, cases, assumptions, and unknowns.
- Checksummed minimal fixtures only when permitted and necessary to make the
  contract executable.

## Validation

- Every required semantic claim cites evidence or is labeled as an assumption.
- Keys and relationships name both parent and child grains.
- Date, null, code, amount, and ordering behavior is explicit where applicable.
- Known baseline anomalies remain visible and are not silently repaired.

## Stop Conditions

- Stop if primary evidence or the source version required by the request is
  unavailable.
- Stop if sources conflict and resolving them requires a product decision.
- Stop if fixtures would expose restricted, sensitive, or redistribution-limited
  material.
- Stop if the requested fidelity claim cannot be tested by the proposed
  contract.
