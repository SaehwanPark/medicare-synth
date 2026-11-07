# Medicare-Synth

Explore and test Medicare research ideas with synthetic, Medicare-like datasets
before working with restricted Medicare files. Medicare-Synth supports
realistic-looking data structures and, for one limited study setting, synthetic
populations adjusted toward selected published statistics. It is a research
preparation and methods-testing sandbox—not a substitute for estimating what is
true of Medicare beneficiaries.

**[Docs portal](https://saehwanpark.github.io/medicare-synth/)** ·
[For researchers](https://saehwanpark.github.io/medicare-synth/researchers/) ·
[For developers](https://saehwanpark.github.io/medicare-synth/developers/) ·
[Source](https://github.com/SaehwanPark/medicare-synth)

## Why this exists

Restricted CMS work has time, access, workflow, and cost constraints. Early
prototyping on artificial Medicare-shaped tables helps teams debug joins, cohort
definitions, and analysis code before DUAs and extracts—without pretending the
synthetic answers are Medicare findings.

## What you can do today

- **Structural exercises:** study file relationships, keys, and valid/invalid
  teaching fixtures; export ordinary CSV/Parquet with developer tooling.
- **Specific evidence-calibrated MVP:** generate 2021 Original Medicare
  FFS-like adults aged 65+ with diabetes and heart-failure indicators and
  **any** inpatient admission, adjusted toward three selected public targets.
- **Code and workflow tests:** practice definitions and sensitivity to
  assumptions across multiple synthetic “worlds.”

Not supported as current product: arbitrary disease/year calibration, one-click
website downloads of calibrated data, or population/causal/clinical claims.

Details: [What you can do](https://saehwanpark.github.io/medicare-synth/researchers/what-you-can-do/).

## One concrete example

Pinned context `mvp-2021-om-ffs-diabetes-ip`: artificial 2021 FFS-like cohort,
age 65+, diabetes → all-cause inpatient presence (not diagnosis-specific
admission). Selected calibration anchors are illustrative/approximate—diabetes
prevalence ~27.7% (2018 source), heart failure ~12% (2022 source), and ~13%
inpatient risk among people with diabetes (weaker industry prior). Stored Phase 5
worlds at 6,000 beneficiaries can match those targets yet show different
inpatient claim counts (for example **404** vs **572**) when free background-risk
assumptions differ.

→ [Worked example](https://saehwanpark.github.io/medicare-synth/researchers/diabetes-hospitalization-example/)

## Current limits

- No universal condition/year support; MVP is pinned and experimental
- No claim of full clinical, longitudinal, or provider realism
- Calibration success ≠ general research utility (Phase 6 evaluation is **active**)
- No hosted browser generator or one-click calibrated CSV on the docs site
- Synthetic outcomes must not be reported as Medicare population findings

→ [Limitations](https://saehwanpark.github.io/medicare-synth/researchers/limitations/)

## How to get started

1. **Explore as a researcher** — read the
   [docs portal](https://saehwanpark.github.io/medicare-synth/) and
   [researcher hub](https://saehwanpark.github.io/medicare-synth/researchers/)
   (no install required for the narrative path).
2. **Install/use as a developer** — Python 3.13+ and
   [`uv`](https://docs.astral.sh/uv/); see
   [installation](https://saehwanpark.github.io/medicare-synth/developers/installation/)
   and the [first useful run](https://saehwanpark.github.io/medicare-synth/developers/first-run/).

Researcher-friendly public download workflows may still need a technical
collaborator; do not assume a ready-made calibrated release asset on the website.

```shell
git clone https://github.com/SaehwanPark/medicare-synth.git
cd medicare-synth
uv sync
uv run medicare-synth validate --scenario valid_baseline_cohort
```

## Responsible use

Do not cite generated estimates, associations, or model performance as empirical
Medicare findings. Disclose assumptions, evidence anchors, and remaining
evaluation. Code is Apache-2.0; check CMS synthetic source terms separately when
acquiring upstream files.

## Status and contributing

Phases 0–5 are complete for the pinned MVP. Phase 6 independent evaluation is
**active**; Phase 7 is planned ([`ROADMAP.md`](ROADMAP.md)). State docs:
[`SPEC.md`](SPEC.md), [`ARCHITECTURE.md`](ARCHITECTURE.md),
[`CHANGELOG.md`](CHANGELOG.md), [`LESSONS.md`](LESSONS.md). Contributor guide:
[developers/contributing](https://saehwanpark.github.io/medicare-synth/developers/contributing/).

```shell
uv run pytest && uv run basedpyright && uv run ruff check .
uv sync --dry-run && git diff --check
```
