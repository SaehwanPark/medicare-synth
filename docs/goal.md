# Goal

Advance Medicare-Synth from a **structurally valid fixture compiler** into an
**evidence-calibrated research playground**, without claiming reconstruction of
real Medicare beneficiaries or treating synthetic estimates as empirical
findings.

Authoritative design:
[`medicare_synth_evidence_calibrated_playground_proposal.md`](medicare_synth_evidence_calibrated_playground_proposal.md).
Canonical state: `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CHANGELOG.md`.
Harness: `AGENTS.md`, `docs/harness/medicare-synth/team-spec.md`,
`.agents/skills/`.

## Success

An investigator can generate a reproducible, structurally valid 2021 Original
Medicare FFS–like cohort; see which published quantities constrain the world and
which assumptions remain free; run the same analysis across a few plausible
worlds; and carry **code and design**—not synthetic conclusions—into authorized
real-data work.

## Current objective (Phase 0 → first vertical slice)

Complete the smallest path that proves the program is feasible:

1. **Pin MVP context** — 2021 Original Medicare FFS, age 65+, explicit
   enrollment/managed-care rules; chronic condition → hospitalization
   (diabetes and/or heart failure candidates). Record open cohort decisions;
   do not invent them silently.
2. **Audit minimal tables/fields** — beneficiary/enrollment, needed chronic
   fields, claim families required for the example; mark present vs must-generate.
3. **Scout evidence** — prefer CMS official aggregates, then Medicare-only
   studies with clear estimands and uncertainty; inventory conflicts and
   overlapping source populations.
4. **Formalize one finding end-to-end** — source → reviewed Evidence IR →
   execute on synthetic tables → comparison report with explicit gaps.
5. **Prove synthesizer controllability** — on synthetic ground truth, recover a
   declared conditional association while keeping linked records valid
   (characterize today’s generator honestly first).
6. **Calibrate lightly** — beneficiary reweighting before richer generators;
   report ESS/support/infeasibility.
7. **Emit 2–3 worlds** — shared supported targets; different documented weak
   assumptions; identical downstream analysis in each.
8. **Freeze evaluation** — hard structural gates, graded evidence metrics,
   untouched holdout/diagnostic set **before** iterative fitting.

## Operating rules

- Structural validity is a **hard gate**; evidence agreement is graded.
- Multiple worlds that fit the same evidence are a feature—expose them.
- Agents assist extraction and orchestration; **humans approve** evidence
  records, estimand implementations, transport assumptions, calibration
  targets, holdout changes, and public calibrated releases.
- Engines and validators must run **without** the agent harness.
- Prefer the simplest method that meets the exit gate (reweight before
  hierarchical Bayes; transparent conditionals before opaque nets).
- Keep docs and claims synchronized with verified behavior only.

## Non-goals

Recover individuals or the full real joint; silent FFS/MA or year conflation;
autonomous adoption of extracted facts; publishing synthetic effect sizes or
model performance as Medicare results; expanding every CMS file family before
the MVP context works end-to-end.

## First milestones

| Milestone | Done when |
| --- | --- |
| A | Feasibility memo + capability gaps + initial evidence inventory land under `docs/` or reports, and Phase 0 exit criteria in `ROADMAP.md` are met |
| B | One human-reviewed external finding executes as a reproducible comparison against generated Medicare-like data |
| C | A calibrated path improves predeclared contextual metrics vs uncalibrated baseline on held-out compatible evidence, without breaking structural gates |

Start at Milestone A unless `ROADMAP.md` shows Phase 0 already closed.
