# Phase 6 engineering and evaluation protocol v1

**Status:** frozen before examining the results of this protocol. **Context:**
`mvp-2021-om-ffs-diabetes-ip`, 2021 Original Medicare FFS-like beneficiaries
aged 65+ at year end, full-year Parts A/B and zero annual HMO/MA months; frozen
corpus `mvp-2021-om-ffs-diabetes-ip-corpus-v1`. This protocol does not approve
new evidence, estimands, partitions, transport or a calibrated public release.
The numerical results are synthetic engineering demonstrations, not Medicare
findings. Historical reports and corpus bytes must not be rewritten.

## Inputs and preregistered analysis

- Use current corrected v2 world code and the three existing approved
  calibration findings. Retain source-year and algorithm approximation notes.
- Fixed evaluation seeds **11, 42, 73**, each with **2,000** beneficiaries.
  Baseline: diabetes 0.18, HF 0.04, inpatient risk given diabetes 0.05 and
  otherwise 0.04. Candidate grids: diabetes `(0.18, 0.277, 0.32)`, HF
  `(0.04, 0.12)`, inpatient risk given diabetes `(0.05, 0.13)`; W2 background
  0.04, W3 background 0.08. Also exercise W1 Level B with solver tolerance
  `1e-6`, at most 40 sweeps and its beneficiary weights.
- Identical analyst code joins beneficiary → enrollment → chronic condition →
  inpatient, with one row per eligible beneficiary and an admission-presence
  flag from distinct beneficiary IDs with admission date in 2021. Report
  denominator retention, diabetes prevalence and all-cause inpatient risk.
  Analyze W1 separately with beneficiary weights; do not treat its unchanged
  raw records as an ordinary calibrated sample. Duplicate each inpatient row
  once as a negative control: person-level estimates and denominator must not
  change. Verify sensitivity: W3's inpatient count must exceed W2's in each
  paired seed. This demonstrates synthetic control, not a real effect.
- Known-truth synthetic control for each seed: N=2,000, diabetes probability
  0.30, HF probability 0.20, inpatient risk 0.20 with diabetes and 0.04 without.
  Compare observed diabetes prevalence, HF prevalence and both conditional
  risks with generator parameters using absolute tolerance
  `max(0.03, 3.5 * sqrt(p*(1-p)/n_stratum))`, using the realized stratum size.
  This is the existing Phase 1 recovery rule, not a literature threshold.
- Report every target ID, evidence and synthetic estimate, signed residual,
  support and compatibility. Level B's numerical tolerance is **1e-6** per
  target after a full sweep. For Level C, complete target coverage is a hard
  gate; report agreement without treating a fitted error threshold as a claim
  of external fidelity. The historical Phase 5 reports are comparisons only,
  not the producer of corrected results.

## Gates and predeclared disposition

1. **Engineering correctness:** relational validity, correct 2021 period and
   beneficiary keys, all approved targets covered, truthful Level B convergence,
   frozen-candidate holdout ordering, weight integrity and replay checks must
   pass. Report each failure and set engineering **no-go** if any fail.
2. **Workflow utility:** identical analyst code must retain the expected eligible
   denominator, withstand duplicated claims, reproduce declared synthetic truth
   within the rule above and show the prespecified background-risk sensitivity
   on all three seeds. Set workflow **no-go** if any gate fails. This establishes
   only the tested synthetic workflow, not general research fitness.
3. **External agreement:** the Andes women holdout was previously exposed; in
   the Andes demonstration its overall finding is an input from the same paper.
   Report this overlap and its year/algorithm transport limitations. No fresh
   compatible, human-approved source-independent finding is supplied, so
   independent fidelity is **no-go / insufficient evidence**, regardless of
   the first two dispositions. Do not retune on any holdout or substitute one.

## Versioning and replay

The implementation producer must be a clean, committed Git revision after this
protocol commit. Record producer commit and code hash, locked environment and
`uv.lock` hash, protocol hash, corpus registry and finding hashes, frozen
partition IDs, world configuration, seed and N, solver status, candidate and
holdout identities, and historical-report checksums in a new machine-readable
report under `reports/phase6/`. Store a concise human summary separately. The
runner must write only to an explicitly supplied new output path; rerun from a
separate worktree of the producer commit with `uv sync --locked` and compare the
report bytes. Preserve the historical `reports/phase5/`, all frozen corpus bytes,
and existing example reports. The Phase 5 producer `7673670` and corrected
producer are distinct identities; compare rather than overwrite.
