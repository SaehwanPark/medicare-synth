# Medicare-Synth

> Build against Medicare-shaped data before restricted access.

Open-source Python toolkit for **structurally valid, provenance-backed**
Medicare synthetic fixtures—and, next, an **evidence-calibrated research
playground** for prototyping methods before restricted CMS data. It does not
reconstruct real beneficiaries or turn synthetic estimates into Medicare
findings.

**[Docs portal](https://saehwanpark.github.io/medicare-synth/)** ·
[Source](https://github.com/SaehwanPark/medicare-synth) ·
[Proposal](docs/medicare_synth_evidence_calibrated_playground_proposal.md) ·
[Goal](docs/goal.md)

## Quickstart

Python 3.13+ and [`uv`](https://docs.astral.sh/uv/). No CMS download required
for built-in scenarios:

```shell
git clone https://github.com/SaehwanPark/medicare-synth.git
cd medicare-synth
uv sync
uv run medicare-synth validate --scenario valid_baseline_cohort
```

```text
Scenario: valid_baseline_cohort
Valid: True
Findings Count: 0
```

Continue with the [first useful run](https://saehwanpark.github.io/medicare-synth/getting-started/first-run/).

## Today

- Deterministic valid/invalid scenario fixtures
- Pydantic + Polars/PyArrow structural validation (keys, dates, codes, accounting)
- Checksummed source manifests and RKB evidence snapshots with explicit provenance
- Vertical/horizontal expansion that preserves connected beneficiary subgraphs
- CSV/Parquet releases with manifests, validation reports, and limitations profiles

[Data model](https://saehwanpark.github.io/medicare-synth/concepts/data-model/) ·
[CLI](https://saehwanpark.github.io/medicare-synth/guides/cli/) ·
[Release workflow](https://saehwanpark.github.io/medicare-synth/guides/release-workflow/)

```shell
uv run medicare-synth catalog --json
uv run medicare-synth audit --scenario valid_baseline_cohort
uv run medicare-synth export \
  --scenario valid_baseline_cohort \
  --output-dir ./dist/release_v1 \
  --format all
```

```python
import medicare_synth as ms

data = ms.ScenarioCompiler.valid_baseline_cohort()
print(ms.RelationalValidator().validate_slice(data).is_valid)
```

## Next

Phases 0–1 are complete ([`docs/phase0/`](docs/phase0/),
[`docs/phase1/`](docs/phase1/); pinned MVP `mvp-2021-om-ffs-diabetes-ip` with a
verified conditional synthesizer). Phase 2+ program in
[`ROADMAP.md`](ROADMAP.md); agent prompt in [`docs/goal.md`](docs/goal.md):
Evidence IR → calibration → multiple plausible worlds → held-out / workflow
evaluation. Structural validity stays a hard gate; literature match is
contextual plausibility, not representativeness. Agents assist; humans approve
evidence and calibrated releases (`AGENTS.md`).

## Scope

Default baseline: CMS 2021 Synthetic Claims (`CMS-2021-SYN-CLAIMS`). Raw files
go under ignored `data/`; tracked manifests keep checksums. Not clinical
validity, population inference, causal truth, or a privacy guarantee—see
[limitations](https://saehwanpark.github.io/medicare-synth/reference/limitations/).

## Contributing

```shell
uv run pytest && uv run basedpyright && uv run ruff check .
uv sync --dry-run && git diff --check
```

State docs: [`SPEC.md`](SPEC.md), [`ARCHITECTURE.md`](ARCHITECTURE.md),
[`ROADMAP.md`](ROADMAP.md), [`CHANGELOG.md`](CHANGELOG.md), [`LESSONS.md`](LESSONS.md).
