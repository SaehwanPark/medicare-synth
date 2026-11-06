---
name: medicare-slice-builder
description: Implement one evidence-approved Medicare-Synth slice with behavioral tests, typed boundaries, deterministic outputs, and synced project docs.
---

# Medicare Slice Builder

## When

After an approved `_workspace/01_evidence_contract.md` for one bounded
behavior (schema, validation, synthesis, Evidence IR/compiler, calibration,
worlds, evaluation, or release surface).

## Inputs

`00_request.md`, `01_evidence_contract.md`; relevant code/tests/docs; task branch.

## Workflow

1. Write `_workspace/02_test_spec.md` (success, boundary, invalid, provenance,
   determinism; holdout isolation if calibration-related).
2. Add focused behavioral tests; record expected failure before production edits
   when a test surface exists.
3. Keep types and recoverable errors explicit; pure transforms vs I/O at edges.
4. Implement the smallest complete slice; never silently repair baseline anomalies.
5. Do not fit on held-out evidence or mutate approved evidence values.
6. Run focused then repo checks (`pytest` / `basedpyright` / `ruff` / docs checks
   as applicable).
7. Sync `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CHANGELOG.md` only where
   verified behavior changes state.
8. Write `_workspace/03_implementation_report.md`.

## Done when

Tests assert observable, evidence-backed behavior; seeds/provenance explicit;
no unrelated family or fidelity claim changes; report separates passed /
unavailable / unrelated failures.

## Stop

Incomplete/contradicted contract; unapproved dependency or public break;
hidden nondeterminism; multi-slice sprawl; validation blocked by unrelated
failures.
