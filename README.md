# Medicare-Synth

> Build against Medicare-shaped data before restricted access.

Medicare-Synth is an open-source Python framework for **structurally valid,
provenance-backed** synthetic Medicare datasets and deterministic research
fixtures. The next program extends that foundation into an
**evidence-calibrated research playground**: literature-grounded, configurable
synthetic worlds for prototyping and stress-testing research ideas—not for
reconstructing real Medicare beneficiaries or publishing synthetic estimates as
empirical findings.

**[Open the documentation portal](https://saehwanpark.github.io/medicare-synth/)** ·
[Browse the source](https://github.com/SaehwanPark/medicare-synth) ·
[Program proposal](docs/medicare_synth_evidence_calibrated_playground_proposal.md) ·
[Goal prompt](docs/goal.md)

## Start here

The built-in scenarios need no CMS download, database, cloud account, or API
key. You need Python 3.13+ and [`uv`](https://docs.astral.sh/uv/):

```shell
git clone https://github.com/SaehwanPark/medicare-synth.git
cd medicare-synth
uv sync
uv run medicare-synth validate --scenario valid_baseline_cohort
```

Expected output:

```text
Scenario: valid_baseline_cohort
Valid: True
Findings Count: 0
```

Next, follow the [first useful run](https://saehwanpark.github.io/medicare-synth/getting-started/first-run/)
to inspect an intentional failure and call the Python API.

## What you can do today

- **Compile deterministic fixtures:** catalog scenarios include valid teaching
  cohorts and intentional anomaly cases.
- **Validate structure:** Pydantic record contracts plus Polars/PyArrow checks
  cover fields, keys, temporal order, administrative compatibility, code
  formats, and accounting bounds.
- **Preserve lineage:** source manifests and pinned RKB evidence snapshots make
  provenance statuses explicit.
- **Expand connected data:** vertical feature synthesis and horizontal
  connected-subgraph scaling preserve relationships and deterministic keys.
- **Export portable artifacts:** release bundles contain CSV/Parquet tables,
  SHA-256 manifests, validation/fidelity reports, and SQL DDL.

The [data model guide](https://saehwanpark.github.io/medicare-synth/concepts/data-model/)
lists supported domain tables and grains.

## Where the project is going

Canonical milestones live in [`ROADMAP.md`](ROADMAP.md). In short:

1. Keep the structural core honest (schema, keys, enrollment, claims integrity).
2. Add a reviewed **Evidence IR** so published CMS aggregates and Medicare-only
   study findings become executable estimands.
3. Calibrate coherent beneficiary worlds against approved evidence, with
   **multiple plausible worlds** where evidence underdetermines the joint.
4. Evaluate held-out agreement and research-workflow utility without claiming
   real-Medicare representativeness.

Agents assist discovery and formalization; they do not silently approve evidence
or rewrite scientific targets. See [`AGENTS.md`](AGENTS.md) and
[`docs/goal.md`](docs/goal.md).

## Common CLI workflows

```shell
uv run medicare-synth validate --scenario valid_baseline_cohort
uv run medicare-synth catalog --json
uv run medicare-synth audit --scenario valid_baseline_cohort
uv run medicare-synth export \
  --scenario valid_baseline_cohort \
  --output-dir ./dist/release_v1 \
  --format all
uv run medicare-synth auto-workflow --all-checks --dry-run
```

See the [CLI reference](https://saehwanpark.github.io/medicare-synth/guides/cli/)
and [release workflow](https://saehwanpark.github.io/medicare-synth/guides/release-workflow/).

## Python API

```python
import medicare_synth as ms

slice_data = ms.ScenarioCompiler.valid_baseline_cohort()
report = ms.RelationalValidator().validate_slice(slice_data)
print(report.is_valid, len(report.findings))
```

## Scope and source boundary

Default baseline: CMS 2021 Synthetic Claims (`CMS-2021-SYN-CLAIMS`). Raw CMS
files land in ignored `data/`; tracked manifests and evidence snapshots keep
retrieval metadata and checksums.

Structural validity is not clinical validity, population representativeness,
distributional fidelity, causal validity, or a formal privacy guarantee.
Literature calibration (when present) improves **contextual plausibility for a
declared research purpose**—not recovery of the real Medicare joint. Read the
[limitations statement](https://saehwanpark.github.io/medicare-synth/reference/limitations/)
before publishing a fixture.

## Contributing

Use `uv`. Keep changes small, typed, deterministic, and reviewable:

```shell
uv run pytest
uv run basedpyright
uv run ruff check .
uv sync --dry-run
git diff --check
```

Canonical state: [`SPEC.md`](SPEC.md), [`ARCHITECTURE.md`](ARCHITECTURE.md),
[`ROADMAP.md`](ROADMAP.md), [`CHANGELOG.md`](CHANGELOG.md), [`LESSONS.md`](LESSONS.md).
