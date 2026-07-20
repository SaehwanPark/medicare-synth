---
name: medicare-slice-builder
description: Implement one evidence-approved Medicare-Synth vertical slice with behavioral tests, typed functional boundaries, deterministic outputs, and synchronized project documents.
---

# Medicare Slice Builder

## When to Use

- Use after an approved evidence contract exists for one bounded behavior slice.
- Use for schemas, normalization, validation, generation, scenarios, exports,
  or public interface behavior covered by that contract.
- Do not use for broad file-family implementation without a vertical acceptance
  test or for unresolved domain semantics.

## Required Inputs

- `_workspace/00_request.md` and `_workspace/01_evidence_contract.md`.
- Relevant implementation, tests, fixtures, and canonical project documents.
- An isolated task branch and available verification commands.

## Workflow

1. Write `_workspace/02_test_spec.md` with success, boundary, invalid-input,
  provenance, and deterministic-output cases.
2. Add focused behavioral tests and record the expected failing command before
  changing production behavior when a test surface exists.
3. Model domain states with explicit types and recoverable errors; keep pure
  transformations separate from source, filesystem, clock, and environment
  effects.
4. Implement the smallest complete slice required by the evidence contract.
5. Preserve raw values and lineage where normalization changes representation;
  never silently repair or discard a baseline anomaly.
6. Run focused checks followed by applicable repository-wide checks.
7. Reconcile `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, and `CHANGELOG.md` only
  where verified behavior changes their state.
8. Write `_workspace/03_implementation_report.md` with changed files, commands,
  results, deviations, document updates, and remaining risks.

## Outputs

- `_workspace/02_test_spec.md` and `_workspace/03_implementation_report.md`.
- Focused tests and one complete implementation slice.
- Synchronized canonical documents where applicable.

## Validation

- Tests assert observable behavior and evidence-backed constraints rather than
  internal implementation details.
- State, side effects, failures, ordering, seeds, and provenance are explicit at
  boundaries.
- No unrelated file family, dependency, public contract, or release claim
  changes.
- The implementation report distinguishes passed checks, unavailable checks,
  unrelated failures, and unverified behavior.

## Stop Conditions

- Stop if the evidence contract is incomplete or contradicted by repository
  reality.
- Stop before adding an unapproved dependency, public incompatibility, hidden
  nondeterminism, or broad abstraction.
- Stop if more than one vertical slice must change unexpectedly.
- Stop if validation is blocked by unrelated failures that prevent trustworthy
  evidence.
