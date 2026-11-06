---
name: medicare-domain-reviewer
description: Review a Medicare-Synth slice for evidence fidelity, grain, provenance, coherence, determinism, and honest structural or calibrated claims.
---

# Medicare Domain Reviewer

## When

After a domain/release-affecting slice is implemented, before declaring done.
Not a second implementation pass; not authority to invent Medicare semantics.

## Inputs

Request + `_workspace/00`–`03`; diff, tests, fixtures, manifests; both sides of
changed boundaries; primary evidence / Evidence IR when applicable.

## Workflow

1. Compare request, evidence contract, tests, implementation, docs, and diff.
2. Check grain, keys, cardinalities, enrollment/service dates, codes, arithmetic,
   nulls, ordering.
3. Trace lineage: source → raw → normalized → provenance → manifest → artifact.
4. Confirm determinism and expected scenario/estimand results where required.
5. For calibrated work: train vs holdout isolation; compatibility grades;
   underidentification disclosed; no representativeness overclaim; engines
   usable without agents.
6. Verdict `pass` / `fix` / `redo` in `_workspace/04_qa_review.md` with
   severity-ranked findings and smallest correction path.

## Done when

Both sides of every changed boundary were read; Critical/High fixed or
explicitly accepted; docs match what exists.

## Stop

`redo` if evidence/grain/scope/tests are directionally incomplete; `fix` only
for bounded defects; escalate if correction changes approved scope or after two
cycles; reject silent provenance fills or unsupported fidelity.
