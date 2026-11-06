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

## Current objective (Phase 5 → calibrated worlds)

Phases 0–4 are **complete**. Frozen corpus v1 and calibration ladder A–C
(reweight + generator-parameter search) exist; holdout stays evaluate-only.

Next path:

1. ~~Phases 0–4~~ — context, synthesizer, Evidence IR, corpus freeze, calibration
   engine (`docs/phase0/` … `docs/phase4/`).
2. **Emit 2–3 worlds** — shared supported calibration targets; different
   documented weak assumptions; identical downstream analysis in each.
3. **Freeze evaluation** — hard structural gates, graded evidence metrics,
   untouched holdout/diagnostic set **before** iterative fitting.
4. **Independent evaluation / expand** — Phases 6–7.

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
- **Never fit on holdout.**

## Non-goals

Recover individuals or the full real joint; silent FFS/MA or year conflation;
autonomous adoption of extracted facts; publishing synthetic effect sizes or
model performance as Medicare results; expanding every CMS file family before
the MVP context works end-to-end.

## First milestones

| Milestone | Done when |
| --- | --- |
| A | Feasibility memo + capability gaps + initial evidence inventory — **done** |
| B | One human-reviewed external finding executes as reproducible comparison — **done** |
| C | Calibrated path improves predeclared contextual metrics vs uncalibrated baseline on held-out compatible evidence, without breaking structural gates — **engine ready (Phase 4)**; Phase 5 worlds + Phase 6 holdout protocol complete the milestone |

Phase 5 packages multi-world releases on top of the Phase 4 engine without
retuning against holdout.
