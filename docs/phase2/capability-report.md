# Phase 2 — Evidence IR capability report

**Date:** 2026-11-06
**Verdict:** Phase 2 exit criteria **met**.

## 1. What was verified

| Capability | Result | Evidence |
| --- | --- | --- |
| IR schema v0.1 | Pass | `medicare_synth.evidence_ir.FindingIR`; fixtures load |
| Concept/estimand vocabulary | Pass | prevalence, binary_risk, rate; diabetes/HF/IP concepts |
| Parse rejects under-specified IR | Pass | rate without `time_unit`; wrong schema version |
| Compiler compatibility report | Pass | LIT-03 gaps (year/age/FFS/algorithm) |
| Explicit refusal of unsupported semantics | Pass | LIT-02 planned-admission rate |
| Reviewed finding executes on synthetic tables | Pass | LIT-03 vs Phase 1 world; deterministic report |
| Draft extraction cannot run as accepted | Pass | `draft_finding_from_fields` + execution gate |
| Source anchors retained | Pass | MMWR URL + location in fixture |

## 2. Exit criteria checklist

| Criterion | Status |
| --- | --- |
| Human-reviewed real Medicare-only finding formalizes | **Met** (LIT-03 / Andes MMWR 2015 prevalence 31.6%) |
| Executes against compatible synthetic dataset | **Met** (Phase 1 `generate_diabetes_ip_world` tables) |
| Compares reproducibly | **Met** (`reports/phase2/lit03_comparison.json`; identical dumps) |
| Errors are explicit | **Met** (compatibility issues; LIT-02 refusal; missing tables; unreviewed gate) |

## 3. Limitations (honest)

1. v0.1 estimands are crude only—no adjusted models, standardization, or
   survival contrasts.
2. Person-time rates approximate 1.0 year per Option-B eligible beneficiary.
3. Source claims-diabetes algorithms are approximated by MBSF flags with
   warnings—not re-implemented from ICD lookbacks.
4. Acceptance is for Milestone B formalization, not Phase 3 corpus freeze.
5. Optional draft extraction is a structured-field helper, not an autonomous
   literature authority.
6. Matching a synthetic world to 0.316 is a controllability demonstration when
   params are set near the evidence value—not evidence calibration.

## 4. Next (Phase 3)

Curate and freeze a small reviewed evidence corpus with train / holdout /
diagnostic partitions and checksums—without treating Phase 2 diagnostic
formalizations as silent training targets.
