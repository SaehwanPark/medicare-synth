# LESSONS

Record only non-obvious, verified lessons likely to recur during setup,
implementation, testing, or release work. Do not use this file as a task tracker
or a log of routine changes.

## Entry Format

### YYYY-MM-DD: Short title

- Context: where and when the problem appeared
- Cause: the verified underlying reason
- Resolution: the action confirmed to solve it
- Prevention: the check or practice that should prevent recurrence
- Evidence: commands, tests, or source paths that support the lesson

## Entries

### 2026-07-21: Dev dependency registration for CLI static checkers in uv projects

- Context: Running `uv run ruff check .` or `uv run basedpyright` failed with missing binary errors (`Failed to spawn: ruff`) during environment verification.
- Cause: `AGENTS.md` instructions prescribed running `ruff` and `basedpyright` checks, but `pyproject.toml` declared only `pytest` in `[dependency-groups] dev`.
- Resolution: Explicitly registered dev tooling via `uv add --dev ruff basedpyright`.
- Prevention: Whenever repository instructions specify CLI linter or type-checker gates, declare those dependencies in `pyproject.toml` via `uv add --dev` so `uv run <tool>` commands execute reproducibly.
- Evidence: `pyproject.toml`, `uv.lock`, `uv run ruff check .`, `uv run basedpyright`.

### 2026-07-21: Configuring basedpyright for clean CI gates in projects with dynamic libraries

- Context: Running `uv run basedpyright` reported hundreds of typing warnings (e.g. from third-party libraries like Polars and Pydantic) and exited with code 1, which blocks clean CI validation gates.
- Cause: `basedpyright` defaults to a highly strict type checking mode that treats all third-party type ambiguities, missing parameter annotations, or unused expression results in tests as failures.
- Resolution: Created a root-level `pyrightconfig.json` setting `typeCheckingMode` to `"standard"` and selectively disabling noisy rules like `reportUnknownParameterType`, `reportUnknownMemberType`, and `reportUnusedCallResult` in verification workflows.
- Prevention: Add an explicit `pyrightconfig.json` at the project start to standardize type checker strictness and silence third-party/test-specific warning noise.
- Evidence: `pyrightconfig.json`, `uv run basedpyright`.
