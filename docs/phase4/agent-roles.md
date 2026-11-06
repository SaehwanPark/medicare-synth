# Phase 4 — Agent role contracts and review gates

**Runtime:** `medicare_synth.calibration.AGENT_ROLE_CONTRACTS`
**Rule:** Numerical engines run fully **without** agents.

## Roles

| Role | May | Must not | Human approval |
| --- | --- | --- | --- |
| Discovery | Search candidate sources | Claim comparability without inspection | Corpus inclusion |
| Extraction | Extract estimates/anchors | Invent SEs or eligibility | Evidence values |
| Formalization | Propose Evidence IR | Approve unsupported semantics | Estimand implementations |
| Compatibility reviewer | Flag mismatches/conflicts | Quietly discard conflicts | Transport changes |
| Calibration operator | Run approved calibrations | Fit holdout; mutate evidence/partitions | Target/holdout changes |
| Evaluation | Discrepancy reports | Declare match without thresholds | Public evaluation claims |
| Release | Assemble manifests | Unapproved representativeness | Public calibrated releases |

These mirror the playground proposal §8 and the harness team-spec human gates.
Agents assist; they are not the statistical source of truth.
