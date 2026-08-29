---
title: "CLI reference"
description: "Run validation, scenarios, audits, exports, expansion, and evidence workflows from the medicare-synth command line."
permalink: /guides/cli/
---

# CLI reference

All commands run through the project environment:

```shell
uv run medicare-synth <command> [options]
```

Use `uv run medicare-synth --help` or append `--help` to any command for the
current parser-level details.

## Everyday commands

| Command | Use it for | Example |
| --- | --- | --- |
| `validate` | Check a named scenario for relational, temporal, and domain findings. | `uv run medicare-synth validate --scenario valid_baseline_cohort` |
| `scenario` | Compile and print one deterministic scenario slice. | `uv run medicare-synth scenario --name valid_carrier_line_item` |
| `catalog` | List the 21 named fixtures; add `--json` for automation. | `uv run medicare-synth catalog --json` |
| `audit` | Compute join coverage, column metrics, and k-anonymity scores. | `uv run medicare-synth audit --scenario valid_baseline_cohort` |
| `expand` | Perform vertical feature synthesis or horizontal connected-subgraph scaling. | `uv run medicare-synth expand --mode horizontal --scale 2` |
| `export` | Write CSV/Parquet tables plus manifests and fidelity reports. | `uv run medicare-synth export --output-dir ./dist/release_v1 --format all` |
| `export-ci` | Export every catalog fixture for lightweight CI or teaching data. | `uv run medicare-synth export-ci --output-dir ./dist/fixtures` |

## Evidence and release commands

| Command | Required inputs | Notes |
| --- | --- | --- |
| `manifest` | `--type baseline` or `--type evidence` | Inspect the tracked source manifest or RKB evidence snapshot. |
| `diff` | `--source-a PATH --source-b PATH` | Compare two evidence/schema contracts before an annual update. |
| `profile` | `--output-dir PATH` | Generate the six-category limitations disclosure profile. |
| `puf` | `--source-dir`, `--manifest`, `--evidence`, `--output-dir` | Import only the bounded 2022 CMS PUF beneficiary/carrier slice. |

The `puf` path expects CMS source files to have been acquired locally and
verified against the supplied manifest. It is intentionally separate from the
default 2021 scenario workflow.

## Common recipes

### Save a validation report

```shell
uv run medicare-synth validate \
  --scenario valid_baseline_cohort \
  --output-dir ./dist/validation
```

### Compare a valid fixture with a broken one

```shell
uv run medicare-synth validate --scenario valid_baseline_cohort
uv run medicare-synth validate --scenario invalid_temporal_inversion
```

### Export a checksummed release bundle

```shell
uv run medicare-synth export \
  --scenario valid_baseline_cohort \
  --output-dir ./dist/release_v1 \
  --format all \
  --release-id v1.0.0-2021
```

### Run the autonomous verification workflow

```shell
uv run medicare-synth auto-workflow --all-checks --dry-run
```

`--dry-run` exercises the verification plan and prints the git actions without
committing, pushing, creating a PR, or merging. The workflow’s many focused
flags are useful when debugging one domain; `--all-checks` is the broad gate.

## Exit behavior and recovery

- A successful command returns exit code `0`.
- A validation command can return `0` while reporting `Valid: False`: intentional
  anomaly scenarios are expected data, not process failures.
- A parser error means a required option or value is missing; rerun with
  `--help` rather than guessing a flag name.
- Keep generated output under `dist/` or another ignored directory. Do not add
  downloaded CMS source files to the repository.

For the validator’s finding categories and provenance statuses, read
[Provenance &amp; validation](../../concepts/provenance-and-validation/).
