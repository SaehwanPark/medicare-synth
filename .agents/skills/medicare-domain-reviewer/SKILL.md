---
name: medicare-domain-reviewer
description: Review a Medicare-Synth slice for evidence fidelity, file grain, provenance, relational coherence, deterministic behavior, and honest release claims.
---

# Medicare Domain Reviewer

## When to Use

- Use after a domain or release-affecting slice is implemented and before it is
  declared complete.
- Use when producer and consumer schemas, claim headers and lines, enrollment and
  service dates, or manifests and artifacts may disagree.
- Do not use as a second implementation pass or as authority to invent missing
  Medicare semantics.

## Required Inputs

- The original request and `_workspace/00_request.md` through
  `_workspace/03_implementation_report.md`.
- Diff, implementation, tests, fixtures, manifests, and relevant canonical
  documents.
- Primary evidence and both producer and consumer sides of changed boundaries.

## Workflow

1. Compare request scope, evidence contract, test specification,
  implementation report, diff, and project documents.
2. Review file grain, keys, parent-child cardinalities, enrollment and service
  dates, code and setting compatibility, arithmetic, nullability, and ordering
  where applicable.
3. Trace preserved and transformed values through source identity, raw value,
  normalized value, provenance status, manifest, and exported artifact.
4. Confirm deterministic seeds, identifiers, outputs, and expected scenario
  results where the contract requires them.
5. Verify validator severity distinguishes invalid data, warnings, baseline
  exceptions, evidence ambiguity, and explicit assumptions.
6. Check that fidelity and limitation statements claim only what tests and
  reports demonstrate.
7. Classify the result as `pass`, `fix`, or `redo` and write
  `_workspace/04_qa_review.md` with severity-ranked evidence and correction
  paths.

## Outputs

- `_workspace/04_qa_review.md` with verdict, findings, evidence, affected
  boundaries, and smallest safe correction path.

## Validation

- Read both sides of every changed data, schema, API, or artifact boundary.
- Distinguish confirmed defects from missing evidence and product decisions.
- Require Critical and High findings to be fixed or explicitly accepted before
  `pass`.
- Confirm tests and canonical documents describe the implementation that
  actually exists.

## Stop Conditions

- Return `redo` when evidence, grain, scope, or the test contract is
  directionally incomplete.
- Return `fix` only for bounded defects that do not change the approved contract.
- Stop if provenance gaps are silently filled or unsupported fidelity is
  presented as verified.
- Escalate when correction changes approved scope or after two review cycles.
