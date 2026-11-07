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

## Current objective (Phase 6 → independent evaluation)

Phases 0–5 are **complete**. Frozen corpus v1, calibration ladder A–C, and MVP
world family v1 exist; evaluation freeze keeps holdout evaluate-only.

Next path:

1. ~~Phases 0–5~~ — context, synthesizer, Evidence IR, corpus freeze, calibration
   engine, multi-world packaging (`docs/phase0/` … `docs/phase5/`).
2. **Independent evaluation** — held-out study comparisons without using them
   for calibration tuning; research-workflow and synthetic-truth benchmarks.
3. **Go / no-go** — predefined thresholds or documented limitations; no
   indefinite retuning against the same holdout set.
4. **Expand** — Phase 7 contexts / literature with regression of prior worlds.

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
| C | Calibrated path improves predeclared contextual metrics vs uncalibrated baseline on held-out compatible evidence, without breaking structural gates — Phase 5 worlds + evaluation freeze **done**; Phase 6 independent holdout protocol completes the milestone |

Phase 6 evaluates the Phase 5 family against independent criteria without
retuning against holdout.
