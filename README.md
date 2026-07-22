# Medicare-Synth

Medicare-Synth is an early-stage open-source project for building contemporary,
versioned Medicare synthetic datasets and deterministic research fixtures. It
will preserve CMS synthetic records where possible, attach provenance to every
extension, and validate relationships among enrollment, claims, lines,
providers, and care events.

The repository provides a complete Python API (`medicare_synth`), a CLI (`medicare-synth`), 19 domain table implementations (spanning clinical claims and Master Beneficiary Summary File segments), a Polars-backed relational validation engine, scenario compiler, release exporter, privacy audit engine, and autonomous workflow automation engine.

## Why This Project Exists

Researchers and developers often need to design Medicare analyses before they
can inspect restricted CCW VRDC data. Existing public synthetic files do not
fully represent current layouts, field coverage, or relational complexity.
Medicare-Synth aims to make schemas, joins, episodes, edge cases, and study code
testable earlier without presenting synthetic results as Medicare population
estimates.

The full motivation and strategic design are in the
[project proposal](docs/medicare-synth-project-proposal_20260720.md).

## Product Boundary & Capabilities

The current release covers the pinned official CMS synthetic baseline (`CMS-2021-SYN-CLAIMS`) and full schema coverage across 19 domain tables:

- **Master Beneficiary Summary File (MBSF)**: Base/Enrollment, Chronic Conditions, Cost & Use, Part D Characteristics, Other Chronic Conditions, National Death Index (NDI), Risk Adjustment, Part C / Medicare Advantage, Fee-For-Service (FFS) Utilization, Part D PDE Utilization
- **Clinical Claims**: Inpatient, Outpatient, Carrier, Skilled Nursing Facility (SNF), Home Health Agency (HHA), Durable Medical Equipment (DME), Hospice, Prescription Drug Event (PDE)
- **Pipeline & CLI Engine**: Normalization, Pydantic v2 + Polars relational validation, multi-format export (Parquet/CSV), vertical/horizontal dataset expansion, dataset diffing, limitations profiling, k-anonymity privacy auditing, and `auto-workflow` verification.

Subcommands available via `medicare-synth`: `validate`, `scenario`, `manifest`, `export`, `expand`, `catalog`, `diff`, `profile`, `export-ci`, `audit`, `auto-workflow`.

## Contributor Guide

- Use `uv` for Python environments, dependency changes, and command execution.
- Prefer static types, pure transformations, explicit state, and effects at
  system boundaries.
- Develop one evidence-backed vertical slice at a time and write behavioral
  tests before implementation when a test surface exists.
- Use 2-space indentation unless a file format requires otherwise.
- Keep the specification, architecture, roadmap, and changelog consistent with
  verified repository behavior.
- Keep temporary or archived data artifacts under the ignored `data/`
  directory.

Current repository checks:

```shell
uv run pytest
uv run basedpyright
uv run ruff check .
git diff --check
```

## Agent Harness

Domain or release-affecting changes use the repository-local workflow described
in [the team specification](docs/harness/medicare-synth/team-spec.md). The
workflow records request scope, evidence, tests, implementation evidence, and
domain review in deterministic `_workspace/` handoffs. Small documentation or
tooling corrections can remain direct.

Repository-wide instructions are in [AGENTS.md](AGENTS.md). The reusable role
skills live under `.agents/skills/`.

## Project Bookkeeping

- [SPEC.md](SPEC.md): completed, active, and planned capabilities
- [ARCHITECTURE.md](ARCHITECTURE.md): current and proposed system boundaries
- [ROADMAP.md](ROADMAP.md): canonical milestones and exit criteria
- [CHANGELOG.md](CHANGELOG.md): contributor-visible history
- [LESSONS.md](LESSONS.md): verified recurring setup and debugging lessons

## Interpretation and Limitations

Medicare-Synth is intended for software development, education, feasibility,
and methods testing. Structural or scenario validity does not imply population
representativeness, external validity, clinical validity, or formal privacy
guarantees. Every future release must state exactly which fidelity properties
were evaluated.
