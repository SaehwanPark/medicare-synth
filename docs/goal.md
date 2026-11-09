# Goal

Evolve Medicare-Synth from a structurally valid fixture compiler and bounded
**evidence-calibrated research playground** toward a **literature-constrained,
continually calibrated shared Medicare-like population model**. The central
asset is versioned generative model state, not a single ever-growing dataset.
Reproducible general-purpose datasets and purpose-specific research worlds are
its intended derivatives, not capabilities already delivered.

Do not reconstruct real beneficiaries, claim recovery of the real joint
distribution, or treat synthetic estimates as Medicare findings.

Canonical state and precedence: `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`,
`CHANGELOG.md`. Planning input:
[November 8 audit](audits/audit-for-project-realignement-20261108.md).
The [earlier playground proposal](medicare_synth_evidence_calibrated_playground_proposal.md)
remains design history; current canonical documents supersede conflicting
strategy and ordering. Harness: `AGENTS.md`,
`docs/harness/medicare-synth/team-spec.md`, `.agents/skills/`.

## Success

An investigator can pin a model/evidence version, generate a structurally valid
Medicare-like cohort, inspect which published analyses constrain it and which
relationships remain uncertain, and run the same workflow across plausible
worlds. Later reviewed evidence produces a traceable child model with explicit
preservation or justified revision of earlier constraints. Researchers carry
**code and study design**, not synthetic conclusions, into authorized real data.
A shared reference model is not a uniquely correct or representative Medicare
population; multiple plausible worlds remain essential.

## Current objective — evaluation and correctness before expansion

Phases 0–5 are historical deliveries: frozen corpus v1, calibration ladder A–C,
MVP world family v1 and evaluation freeze exist. Phase 6 independent evaluation
remains active. The November 8 adoption is **documentation only**: it implements
no fixes, estimators, joint models or continual updates and runs no tests.

The static audit identifies correctness/interpretation risks that gate renewed
convergence or affirmative calibrated-release claims. Preserve old artifacts;
do not rewrite historical completion as if these risks had already been fixed.

## Ordered execution handoff (future implementation, separately scoped)

1. **Recover contracts and approve the slice:** read canonical docs, the audit,
   pinned cohort/corpus and current source. Retain 2021 FFS age 65+ Option B;
   do not silently change evidence roles, variables or denominators.
2. **Phase 6 + 7A:** continue independent-evaluation protocol work while
   hardening full-sweep IPF convergence, approved-target coverage, and fit/report
   cohort alignment. Make Level B weights-only semantics explicit; move holdout
   evaluation after calibration-only selection and disclose prior exposure.
   Correctness gates precede affirmative release decisions. Record go/no-go,
   including no-go where findings remain unresolved; never retune indefinitely
   against exposed holdout results.
3. **7B → 7C, first joint + inferential MVP:** formalize supported crude effects,
   then one real Medicare adjusted logistic finding; extend joint
   age/sex/diabetes/HF/IP support. Reevaluate the existing prevalence and IP-risk
   constraints while adding comorbidity, age/sex relationships and one adjusted
   OR. Compare the OR estimated by the declared analysis on generated data—not a
   coefficient copied into the generator. Use a new reviewed corpus version,
   predeclared tolerances, known-truth controls, per-target coverage and hard
   structural gates. Audit example numbers are not evidence targets.
4. **7D, versioned continual calibration:** preserve parent model/corpus versions,
   warm-start a child on new reviewed evidence, account for uncertainty and
   source dependence, and reevaluate all prior active constraints. Report drift,
   conflict/supersession and justified revisions; unapproved regression blocks
   promotion. This is a separate gate beyond the bounded inferential MVP.
5. **7E, base/world separation:** generalize cohort-conditioned, locally
   calibrated and scenario/alternative worlds from pinned base versions;
   local updates cannot mutate the base or sibling worlds. Materialized data
   pin population, size, seed and export version in addition to model lineage.
6. **7F, scaling/evaluation:** expand estimators (Poisson, survival/Cox, complex
   designs), conditions, years, longitudinal data and sizes only after earlier
   gates; independently assess each context and regress prior model/worlds.

`ROADMAP.md` owns detailed outputs and exit criteria. Implement exactly the
separately approved slice; do not broaden scope. If the plan conflicts with the
codebase, stop and report instead of improvising. Stop before the inferential
MVP if no compatible source/variables can support the declared analysis without
unapproved transport. The present documentation change authorizes no code work.

## Operating rules

- Structural validity is a **hard gate**; evidence agreement is graded, but a
  missing approved target is not success on a smaller denominator.
- Multiple worlds fitting the same evidence expose underidentification. More
  literature or larger samples do not guarantee greater realism.
- Classify compatible, overlapping, transport-dependent, contradictory and
  superseded evidence before calibration; never average incompatible findings
  automatically. Preserving prior calibration does not mean retaining obsolete
  relationships forever.
- Agents assist; **humans approve** evidence, estimand implementations, transport
  assumptions, calibration targets, holdout changes and calibrated releases.
- Engines and validators must run **without** the agent harness.
- Prefer transparent conditional models and explicit analysis dispatch before
  opaque nets or generalized hierarchical machinery.
- Keep delivered vs planned claims explicit and anchored in code/test/report
  evidence. Follow proportional verification for future code slices; this
  document-only adoption intentionally runs no tests.
- **Never fit on holdout.** Evaluate after selection; never silently relabel
  previously exposed evidence as fresh independent validation.

## Non-goals

Recover individuals or the full real joint; claim universal Medicare coverage;
silent FFS/MA, year or algorithm conflation; autonomous evidence adoption;
publishing synthetic effects or performance as Medicare results; collecting a
large literature corpus or expanding every CMS family before the bounded joint
and inferential feasibility gate passes.

## Risk and unresolved approvals

**Risk: medium** — this plan changes strategic direction across canonical
consumers, not runtime behavior. Source/design compatibility, estimator coding,
uncertainty/dependence policy, preservation thresholds, context transport and
workflow benchmarks still need human decisions. No corpus, partition or model
release approval is implied by adopting this plan.
