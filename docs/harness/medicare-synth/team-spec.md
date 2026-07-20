# Medicare-Synth Foundation Harness Team Spec

## Goal

Deliver one evidence-backed Medicare vertical slice at a time, from an explicit
domain contract through tests, implementation, and independent domain review.
The harness is repository-local, runtime-agnostic, and designed for foundation
work before broad data generation begins.

## Pattern

The outer pattern is a sequential Pipeline because evidence, tests,
implementation, and review depend on prior artifacts. The final edge is a
Producer-Reviewer loop capped at two revision cycles.

One agent may execute all roles sequentially. Delegation is optional and should
be used only for specialization or context isolation. The orchestrator owns
scope, synthesis, and final acceptance in either mode.

## Roles

| Role | Responsibility | Writes |
| --- | --- | --- |
| `medicare-synth-orchestrator` | Scope, sequencing, routing, and acceptance | `_workspace/00_request.md` |
| `medicare-evidence-specifier` | Evidence, grain, semantics, provenance, and constraints | `_workspace/01_evidence_contract.md` |
| `medicare-slice-builder` | Behavioral tests, implementation, checks, and document reconciliation | `_workspace/02_test_spec.md`, `_workspace/03_implementation_report.md` |
| `medicare-domain-reviewer` | Cross-boundary Medicare, provenance, and fidelity review | `_workspace/04_qa_review.md` |

## Routing Boundary

Use the harness when work changes Medicare semantics, executable schemas, data
or artifact contracts, normalization, validation, generation, scenarios,
release claims, or public CLI/API behavior.

Keep typo fixes, link repairs, wording-only documentation changes, and local
tooling maintenance direct when they do not change a domain or release contract.

## Phase Order

1. Scope: record the requested behavior, source scope, acceptance criteria,
  non-goals, ownership, and stop conditions.
2. Specify evidence: establish file grain, inputs, outputs, provenance,
  constraints, unknowns, and expected failures.
3. Specify tests: translate the approved evidence contract into observable
  success, boundary, and failure cases before production behavior changes.
4. Implement: deliver the smallest complete slice and record commands, results,
  deviations, and document updates.
5. Review: compare the request, evidence, tests, implementation, and both sides
  of every changed boundary; return `pass`, `fix`, or `redo`.
6. Reconcile: after `pass`, synchronize durable state into `SPEC.md`,
  `ARCHITECTURE.md`, `ROADMAP.md`, and `CHANGELOG.md` as applicable.

## Handoff Contract

- `_workspace/00_request.md`: request, scope, branch, ownership, acceptance
  criteria, non-goals, and stop conditions.
- `_workspace/01_evidence_contract.md`: sources, file-year scope, grain, fields,
  relationships, provenance statuses, constraints, assumptions, and unknowns.
- `_workspace/02_test_spec.md`: behavioral cases, fixtures, expected outputs,
  expected findings, and initially failing command evidence.
- `_workspace/03_implementation_report.md`: changed files, checks, results,
  deviations, bookkeeping updates, and remaining risks.
- `_workspace/04_qa_review.md`: `pass`/`fix`/`redo` verdict, severity-ranked
  findings, boundary evidence, and smallest correction path.

Handoffs are local and ignored by Git. Durable contracts must also live in code,
tests, schemas, manifests, or canonical bookkeeping documents.

## Coordination and Write Safety

- Keep the workflow sequential; no downstream phase starts before its required
  input is stable.
- Do not use concurrent writers in one checkout. If independent read-only
  analysis is delegated, each worker returns a bounded result to the
  orchestrator.
- The orchestrator is the sole synthesis owner and must disclose missing worker
  results or unresolved conflicts rather than filling gaps.
- Do not require a model pin, agent SDK, messaging runtime, or external
  orchestrator.

## Failure Policy

- Missing primary evidence, source version, or required provenance stops the
  evidence phase; assumptions cannot be presented as documented facts.
- An unresolved product choice that changes semantics, redistribution, public
  contracts, or fidelity claims returns to the requester.
- `fix` means the contract is sound and a bounded local correction is cheaper
  than rebuilding the slice.
- `redo` means evidence, scope, tests, or design is directionally incomplete.
- After two unsuccessful implementation-review cycles, stop and escalate with
  the unresolved findings.
- Unrelated test failures are recorded and left unchanged unless they block
  trustworthy validation of the slice.

## Validation Scenarios

- Normal flow: one evidence-backed schema or validator slice proceeds through
  all five handoffs, passes focused and repository checks, and receives `pass`.
- Near miss: a wording-only README correction remains direct and creates no
  `_workspace/` artifacts.
- Failure flow: missing or conflicting field provenance is recorded in the
  evidence contract and stops before tests or production behavior claim the
  field is verified.
