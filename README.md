# Medicare-Synth

Medicare-Synth is an early-stage open-source project for building contemporary,
versioned Medicare synthetic datasets and deterministic research fixtures. It
will preserve CMS synthetic records where possible, attach provenance to every
extension, and validate relationships among enrollment, claims, lines,
providers, and care events.

The repository currently contains the project specification, architecture,
roadmap, and contributor harness. It does not yet provide a CLI, Python API, or
generated dataset.

## Why This Project Exists

Researchers and developers often need to design Medicare analyses before they
can inspect restricted CCW VRDC data. Existing public synthetic files do not
fully represent current layouts, field coverage, or relational complexity.
Medicare-Synth aims to make schemas, joins, episodes, edge cases, and study code
testable earlier without presenting synthetic results as Medicare population
estimates.

The full motivation and strategic design are in the
[project proposal](docs/medicare-synth-project-proposal_20260720.md).

## Initial Product Boundary

The first credible release is planned to cover one pinned official CMS
synthetic baseline and a narrow end-to-end slice:

- beneficiary enrollment needed for service-date validation
- carrier claim headers and lines
- outpatient claim headers and revenue-center lines
- provenance-bearing evidence for the selected files and years
- normalization, validation, and CSV/Parquet export
- deterministic valid and invalid scenarios with expected results

Baseline selection, target schema year, schema language, licensing, and artifact
publication remain open foundation decisions. Track their resolution in
[ROADMAP.md](ROADMAP.md).

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
uv sync --dry-run
git diff --check
```

Python lint, type-check, and test commands will be added when their corresponding
tools and source surfaces are introduced. Do not treat planned tooling as
currently configured.

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
