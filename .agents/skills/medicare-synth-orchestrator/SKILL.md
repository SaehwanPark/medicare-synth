---
name: medicare-synth-orchestrator
description: Coordinate one evidence-backed Medicare-Synth vertical slice through specification, tests, implementation, and bounded domain review.
---

# Medicare-Synth Orchestrator

## When to Use

- Use for changes to Medicare semantics, schemas, data contracts, validators,
  generation, scenarios, release artifacts, or public interfaces.
- Use when a change needs an inspectable provenance and review trail.
- Do not use for wording-only documentation or local tooling corrections that
  leave domain and release contracts unchanged.

## Required Inputs

- Requested observable behavior and intended user or consumer.
- Source, file-family, data-year, and release scope where applicable.
- Acceptance criteria, non-goals, quality claims, and known product decisions.
- Current specification, architecture, roadmap, relevant code, and tests.

## Workflow

1. Write `_workspace/00_request.md` with scope, branch, ownership, acceptance
  criteria, non-goals, and stop conditions.
2. Invoke `medicare-evidence-specifier` to produce
  `_workspace/01_evidence_contract.md`.
3. Confirm the contract contains no unresolved decision that would change
  semantics or fidelity claims.
4. Invoke `medicare-slice-builder` for the test specification, failing test
  evidence, smallest implementation, checks, and implementation report.
5. Invoke `medicare-domain-reviewer` to produce the QA verdict.
6. Route `fix` findings to the builder and `redo` findings to the earliest
  incomplete phase; allow no more than two review cycles.
7. On `pass`, verify durable decisions are reconciled into canonical documents
  and report files, checks, deviations, and unresolved risks.

One agent may execute these roles in order. Delegate only when specialization or
context isolation has concrete value, and never allow overlapping writers in
one checkout.

## Outputs

- `_workspace/00_request.md` through `_workspace/04_qa_review.md` as defined in
  `docs/harness/medicare-synth/team-spec.md`.
- One complete, tested vertical slice with synchronized project documents.
- Final acceptance summary owned by the orchestrator.

## Validation

- Every phase consumes the named prior artifact and produces its declared
  output.
- The evidence contract distinguishes documented facts, baseline observations,
  explicit assumptions, and unresolved conflicts.
- The QA review reads the original request and both sides of every changed
  boundary.
- No release or fidelity claim exceeds the recorded validation evidence.

## Stop Conditions

- Stop if required evidence, source versions, or provenance cannot be named.
- Stop for an unapproved public contract, redistribution, licensing, or fidelity
  decision.
- Stop if the slice expands beyond one reviewable vertical behavior.
- Escalate after two unsuccessful review cycles or with unresolved Critical or
  High findings.
