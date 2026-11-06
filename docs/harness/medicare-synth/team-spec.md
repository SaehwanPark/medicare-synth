# Medicare-Synth Harness Team Spec

## Goal

Deliver one evidence-backed vertical slice at a time—structural contracts,
Evidence IR/estimands, synthesis, calibration, evaluation, or release
claims—through specify → test → implement → review.

## Pattern

Sequential pipeline; final edge is producer–reviewer, max two revision cycles.
One agent may run all roles. Delegate only for specialization or isolation.
Orchestrator owns scope and acceptance.

## Roles

| Role | Responsibility | Writes |
| --- | --- | --- |
| `medicare-synth-orchestrator` | Scope, sequencing, acceptance | `_workspace/00_request.md` |
| `medicare-evidence-specifier` | Sources, grain, Evidence IR semantics, provenance, constraints | `_workspace/01_evidence_contract.md` |
| `medicare-slice-builder` | Tests, implementation, checks, doc sync | `_workspace/02_test_spec.md`, `_workspace/03_implementation_report.md` |
| `medicare-domain-reviewer` | Fidelity, coherence, honest claims | `_workspace/04_qa_review.md` |

Literature discovery/extraction/formalization are specifier (or orchestrated)
tasks with human approval—not separate always-on skills.

## When to use the harness

Use for Medicare semantics, schemas, Evidence IR, calibration, worlds,
validators, generation, scenarios, release claims, or public CLI/API changes.

Skip for wording-only docs or local tooling that leave domain/release contracts
unchanged.

## Phase order

1. Scope → `00_request.md`
2. Evidence contract → `01_evidence_contract.md`
3. Tests → `02_test_spec.md` (failing first when a test surface exists)
4. Implement → `03_implementation_report.md`
5. Review → `04_qa_review.md` (`pass` / `fix` / `redo`)
6. On `pass`, sync `SPEC.md` / `ARCHITECTURE.md` / `ROADMAP.md` / `CHANGELOG.md`

## Handoffs

Local, gitignored `_workspace/` files. Durable contracts also live in code,
tests, schemas, manifests, or canonical docs. Volatile agent chat is not the
statistical source of truth.

## Failure policy

- Missing primary evidence/version/provenance stops the evidence phase.
- Unresolved product choices that change semantics, redistribution, public
  contracts, holdouts, or fidelity claims return to the requester.
- `fix`: bounded local correction. `redo`: evidence/scope/tests incomplete.
- After two failed review cycles, escalate.
- Leave unrelated test failures alone unless they block trustworthy validation.

## Human approval gates (calibrated work)

Require explicit approval for: new evidence records; new estimand
implementations; cohort/transport assumption changes; calibration target or
holdout partition changes; public evidence-calibrated releases.
