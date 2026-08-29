---
title: "Install and verify"
description: "Set up Medicare-Synth locally and confirm that the package and deterministic fixtures are ready."
permalink: /getting-started/installation/
---

# Install and verify

Medicare-Synth is a local Python package. The built-in fixtures run without a
CMS download, database, cloud account, or API key, so you can reach a useful
result before deciding which source files you need.

## Prerequisites

- Python **3.13 or newer**
- [`uv`](https://docs.astral.sh/uv/) for the reproducible environment
- Git

The supported Python range is declared in `pyproject.toml`; if `uv` reports an
older interpreter, install a current Python and rerun the sync step.

## Install from a clean checkout

```shell
git clone https://github.com/SaehwanPark/medicare-synth.git
cd medicare-synth
uv sync
```

`uv sync` creates or updates the project environment from `pyproject.toml` and
`uv.lock`. It does not download restricted Medicare data.

## Verify the installation

Run the CLI help and a known-good deterministic fixture:

```shell
uv run medicare-synth --help
uv run medicare-synth validate --scenario valid_baseline_cohort
```

Expected output includes:

```text
Scenario: valid_baseline_cohort
Valid: True
Findings Count: 0
```

Run the test suite when you want to verify the complete checkout:

```shell
uv run pytest
uv run basedpyright
uv run ruff check .
```

## If setup fails

| Symptom | Recovery |
| --- | --- |
| `uv: command not found` | Install `uv` from its [official installation guide](https://docs.astral.sh/uv/getting-started/installation/), reopen the shell, and rerun `uv sync`. |
| Python version is too old | Install Python 3.13+ and use `uv python pin 3.13` before `uv sync`. |
| CLI cannot be found | Run it through the project environment with `uv run medicare-synth ...`; do not rely on a global install. |
| You expected source files after sync | Source acquisition is a separate, manifest-verified step. Start with the [release workflow](../../guides/release-workflow/). |

## Next step

Continue with the [first useful run](../first-run/) to inspect a valid fixture,
exercise an intentional failure, and call the Python API.
