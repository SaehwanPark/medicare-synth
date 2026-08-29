# Medicare-Synth

> Build against Medicare-shaped data before restricted access.

Medicare-Synth is an open-source Python framework for provenance-backed
synthetic Medicare datasets and deterministic research fixtures. It helps
researchers, data engineers, educators, and methods developers test schemas,
joins, episodes, validation rules, and release workflows locally.

**[Open the documentation portal](https://saehwanpark.github.io/medicare-synth/)** ·
[Browse the source](https://github.com/SaehwanPark/medicare-synth)

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

## What you can do

- **Compile deterministic fixtures:** 21 catalog scenarios include valid
  teaching cohorts and intentional anomaly cases.
- **Validate structure:** Pydantic record contracts plus Polars/PyArrow checks
  cover fields, keys, temporal order, administrative compatibility, code
  formats, and accounting bounds.
- **Preserve lineage:** source manifests and pinned RKB evidence snapshots make
  baseline, normalized, re-keyed, derived, imputed, synthesized, calibrated,
  and scenario-generated values explicit.
- **Expand connected data:** vertical feature synthesis and horizontal
  connected-subgraph scaling preserve relationships and deterministic keys.
- **Export portable artifacts:** release bundles contain CSV/Parquet tables,
  SHA-256 manifests, validation/fidelity reports, and SQL DDL; a limitations
  profile can be generated alongside them.
- **Exercise the 2022 boundary:** the source-aware PUF importer is limited to
  the 2022 beneficiary and carrier files; the default workflow remains on the
  2021 CMS Synthetic Claims baseline.

The [data model guide](https://saehwanpark.github.io/medicare-synth/concepts/data-model/)
lists all 19 supported domain tables and their grains.

## Common CLI workflows

```shell
# Validate a scenario
uv run medicare-synth validate --scenario valid_baseline_cohort

# List scenarios (JSON is convenient in CI)
uv run medicare-synth catalog --json

# Audit join coverage and k-anonymity metrics
uv run medicare-synth audit --scenario valid_baseline_cohort

# Export a checksummed release bundle
uv run medicare-synth export \
  --scenario valid_baseline_cohort \
  --output-dir ./dist/release_v1 \
  --format all

# Run the broad verification plan without changing git state
uv run medicare-synth auto-workflow --all-checks --dry-run
```

See the [CLI reference](https://saehwanpark.github.io/medicare-synth/guides/cli/)
for all 12 subcommands and the [release workflow](https://saehwanpark.github.io/medicare-synth/guides/release-workflow/)
for manifest-verified source handling.

## Python API

```python
import medicare_synth as ms

slice_data = ms.ScenarioCompiler.valid_baseline_cohort()
report = ms.RelationalValidator().validate_slice(slice_data)
print(report.is_valid, len(report.findings))

audit = ms.AuditEngine().audit_dataset(slice_data)
print(audit.overall_privacy_score)
```

## Scope and source boundary

The default baseline is the official CMS 2021 Synthetic Claims collection
(`CMS-2021-SYN-CLAIMS`). Raw CMS files are acquired into ignored `data/`
directories; tracked manifests and evidence snapshots preserve retrieval
metadata, grains, row counts, and checksums.

Medicare-Synth supports software development, pipeline testing, education, and
feasibility work. Structural validity does not establish clinical validity,
population representativeness, distributional fidelity, causal validity, or
formal privacy guarantees. Synthetic outputs must not be cited as empirical
Medicare population statistics. Read the [limitations statement](https://saehwanpark.github.io/medicare-synth/reference/limitations/)
before publishing a fixture.

## Contributing

Use `uv` for environments and keep changes small, typed, deterministic, and
reviewable. The full local gate is:

```shell
uv run pytest
uv run basedpyright
uv run ruff check .
uv sync --dry-run
git diff --check
```

The [contributor guide](https://saehwanpark.github.io/medicare-synth/contributing/)
explains branch, documentation, provenance, and PR expectations. Canonical
technical state lives in [`SPEC.md`](SPEC.md), [`ARCHITECTURE.md`](ARCHITECTURE.md),
[`ROADMAP.md`](ROADMAP.md), [`CHANGELOG.md`](CHANGELOG.md), and [`LESSONS.md`](LESSONS.md).
