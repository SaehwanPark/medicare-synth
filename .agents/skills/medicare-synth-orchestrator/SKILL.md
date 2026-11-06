---
name: medicare-synth-orchestrator
description: Coordinate one Medicare-Synth vertical slice—structural, Evidence IR, synthesis, calibration, or release—through specify, test, implement, and review.
---

# Medicare-Synth Orchestrator

## When

Domain/release work: schemas, validators, Evidence IR, calibration, worlds,
generation, scenarios, public APIs. Skip wording-only or pure tooling edits.

## Inputs

Observable behavior; source/year/scope; acceptance and non-goals; current
`SPEC.md` / `ARCHITECTURE.md` / `ROADMAP.md` / `docs/goal.md` as applicable.

## Workflow

1. Write `_workspace/00_request.md` (scope, branch, acceptance, non-goals, stops).
2. Run `medicare-evidence-specifier` → `01_evidence_contract.md`.
3. Block if unresolved choices would change semantics, holdouts, or fidelity.
4. Run `medicare-slice-builder` (tests → impl → checks → report).
5. Run `medicare-domain-reviewer`; route `fix`/`redo`; ≤2 review cycles.
6. On `pass`, confirm canonical docs synced; summarize files, checks, risks.

One agent may play all roles. No overlapping writers in one checkout.

## Done when

Named handoffs exist; claims ≤ validation evidence; engines remain usable
without agents; human gates respected for evidence/holdouts/calibrated releases.

## Stop

Missing evidence/versions; unapproved public/fidelity decision; slice sprawl;
two failed review cycles or open Critical/High findings.
