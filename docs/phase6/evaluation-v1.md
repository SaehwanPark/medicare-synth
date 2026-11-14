# Phase 6 engineering and workflow evaluation v1

## Disposition

- **Engineering: conditional go** for this pinned run, conditional on the
  verification suite and clean-worktree replay described below. The solver's
  numerical tolerance is not an external fidelity criterion.
- **Workflow utility: conditional go** for the one beneficiary-grain workflow
  and controls specified in [protocol v1](protocol-v1.md), not for arbitrary
  analyses or transport to Medicare.
- **Independent fidelity: no-go, insufficient evidence.** The Andes women
  holdout had already been examined; the Andes example also fits an overall
  finding from the same paper. Source-year and algorithm differences remain.
  This is not a fresh independent evaluation. Calibrated public release is not
  approved.

The protocol was committed at `41d3c13` before these results were examined.
The first execution used producer `8ebe4b2`; after observing that its metadata
omitted OS and architecture, only environment metadata was amended, and the
final run was produced from `2f36337039a001f19da8fab55949c786ee0dffaa`. No
threshold, candidate grid, seed or analysis was changed after inspection.
The [machine-readable report](../../reports/phase6/engineering-evaluation-v1.json)
records the code, protocol, environment, lock, corpus, partition, finding and
historical-report hashes, target rows, solver status, weights diagnostics and
holdout results. SHA-256:
`7d5cd4ea7dbef61a1571d776a009777c5e0797c8b0fc70dee6b3cddcb4461990`.

## What was tested

Each of seeds 11, 42 and 73 had 2,000 eligible synthetic beneficiaries. Every
known-truth check passed its preregistered recovery rule; duplicate inpatient
claims did not change beneficiary-level results; all worlds retained 2,000
eligible records and had complete targets and valid structure. Level B
converged after full sweeps at `1e-6` and was analyzed using beneficiary
weights, not as altered records. In these three samples, the synthetic high
background-risk world had 178 vs 123, 214 vs 154, and 194 vs 126 inpatient
beneficiaries compared with its paired world. This is a generator-sensitivity
check, not a Medicare effect estimate.

The report also includes pre/post calibration residuals and the historical v1
summary. The historical run used 6,000 beneficiaries and seed 42, whereas the
new runs use 2,000; their summaries are not direct like-for-like comparisons.
The historical corpus and report files remain byte-identical.

## Replay

On the recorded OS, architecture, Python and locked dependency environment:

```sh
repo="$PWD"
tmp="$(mktemp -d)"
git worktree add --detach "$tmp/work" 2f36337039a001f19da8fab55949c786ee0dffaa
(cd "$tmp/work" && uv sync --locked && \
  uv run --no-sync python scripts/phase6_evaluate_v1.py --output "$tmp/replay.json")
cmp "$repo/reports/phase6/engineering-evaluation-v1.json" "$tmp/replay.json"
git worktree remove --force "$tmp/work"
rm -rf "$tmp"
```

The final run and a separate clean worktree replay produced the identical
SHA-256 shown above. Byte identity is asserted for the recorded environment;
other platforms should not assume identical bytes. The runner refuses an
existing output file and the historical Phase 5 output directory.
