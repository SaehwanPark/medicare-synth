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

## Current objective (Phase 2 → first vertical slice)

Phases 0–1 are **complete** (`docs/phase0/`, `docs/phase1/`). Pinned context:
`mvp-2021-om-ffs-diabetes-ip`. Conditional synthesizer
(`medicare_synth.synthesis`) recovers known-truth diabetes→IP relationships
under pinned seeds with structural gates.

Next path:

1. ~~**Pin MVP context**~~ / ~~**Audit**~~ / ~~**Scout evidence**~~ — Phase 0.
2. ~~**Prove synthesizer controllability**~~ — Phase 1 (`docs/phase1/`).
3. **Formalize one finding end-to-end** — source → reviewed Evidence IR →
   execute on synthetic tables → comparison report with explicit gaps —
   **Phase 2 active**.
4. **Calibrate lightly** — beneficiary reweighting before richer generators;
   report ESS/support/infeasibility.
5. **Emit 2–3 worlds** — shared supported targets; different documented weak
   assumptions; identical downstream analysis in each.
6. **Freeze evaluation** — hard structural gates, graded evidence metrics,
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
| A | Feasibility memo + capability gaps + initial evidence inventory land under `docs/` or reports, and Phase 0 exit criteria in `ROADMAP.md` are met — **done** (`docs/phase0/`) |
| B | One human-reviewed external finding executes as a reproducible comparison against generated Medicare-like data |
| C | A calibrated path improves predeclared contextual metrics vs uncalibrated baseline on held-out compatible evidence, without breaking structural gates |

Start Phase 2 Evidence IR work toward Milestone B; do not treat Phase 0
scouting magnitudes or Phase 1 known-truth params as Medicare findings.
