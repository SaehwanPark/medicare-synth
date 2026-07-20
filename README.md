# Medicare-Synth

This project is to build an open-source system for constructing contemporary, versioned Medicare synthetic datasets and research fixtures. The project is motivated by a practical gap: researchers and developers often need to design and test Medicare analyses before they can access restricted data in the Chronic Conditions Warehouse Virtual Research Data Center (CCW VRDC), yet older public synthetic files do not fully match current Medicare file structures, field coverage, or relational complexity.

Full roadmap: `docs/medicare-synth-project-proposal_20260720.md`
Temporary or archived datasets (incl. data-related artifacts): `data/`

## Preferred Development Paradigms

- Static types as much as possible
- Return-oriented programming
- Spec-Driven Developments (SDD)
- Test-Driven Developments (TDD)
- Absolute Data Types + Domain/Type-Driven Developments

## Tooling Consideration

- Use `uv` to manage Python runtime and packages always (e.g., `uv add`, `uv run`)
- Preferred Python tooling: `pytest`, `basedpyright`, `pydantic`, `comp-builders`, `ruff`
- Strictly use 2 spaces of tabsize throughout (codes and documents)
- Be ready for the cases where spawned terminals or agents may suffer from path issues (e.g., path environments might not be well-inherted). Always try to search for the necessary/required CLI tools even when they are not found in the current path configuration.
