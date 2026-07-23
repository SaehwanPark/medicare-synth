# Medicare-Synth

Medicare-Synth is an open-source framework for compiling contemporary,
versioned Medicare synthetic datasets and deterministic research fixtures. It
preserves official CMS synthetic baselines (`CMS-2021-SYN-CLAIMS`), attaches field-
and record-level provenance lineage to every extension, and enforces relational,
temporal, administrative, and accounting constraints across beneficiary enrollment and
clinical claims.

The project provides a complete Python API (`medicare_synth`), a CLI tool (`medicare-synth`), 19 domain table implementations, a Polars-backed relational validation engine, scenario compiler, release exporter, privacy audit engine, dataset expander, and autonomous workflow automation engine.

## Quickstart

### Prerequisites

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (recommended Python package manager)

### Installation

```shell
git clone https://github.com/SaehwanPark/medicare-synth.git
cd medicare-synth
uv sync
```

### Python API Example

```python
import medicare_synth as ms

# 1. Compile a deterministic scenario cohort fixture
slice_data = ms.ScenarioCompiler.valid_baseline_cohort()

# 2. Perform high-performance relational & temporal validation
validator = ms.RelationalValidator()
report = validator.validate_slice(slice_data)
print(f"Validation status: {'PASSED' if report.is_valid else 'FAILED'}")
print(f"Findings count: {len(report.findings)}")

# 3. Compute k-anonymity privacy score across tables
audit_engine = ms.AuditEngine()
audit_report = audit_engine.audit_dataset(slice_data)
print(f"Overall dataset privacy score: {audit_report.overall_privacy_score:.2f}")
```

### Command-Line Interface (CLI)

The `medicare-synth` command line tool exposes 11 subcommands for validation, release export, dataset expansion, profiling, and automated verification:

```shell
# Validate a scenario fixture for relational and temporal integrity
uv run medicare-synth validate --scenario valid_baseline_cohort

# Export a checksummed release bundle (Parquet/CSV, manifests, SQL reference DDL)
uv run medicare-synth export --scenario valid_baseline_cohort --output-dir ./dist/release_v1 --format all

# Expand dataset vertically (feature synthesis) or horizontally (subgraph re-keying)
uv run medicare-synth expand --mode vertical --scenario valid_baseline_cohort --scale 2.0

# Audit k-anonymity privacy and join coverage across domain tables
uv run medicare-synth audit --scenario valid_baseline_cohort

# Run full autonomous workflow verification suite (40+ verification checks)
uv run medicare-synth auto-workflow --all-checks
```

## Why This Project Exists

Researchers and software engineers often need to construct and test Medicare data pipelines before obtaining restricted CMS Chronic Conditions Data Warehouse (CCW) VRDC access. Standard public synthetic files lack contemporary file layouts, field coverage, or relational complexity.

Medicare-Synth enables early, deterministic testing of schemas, entity joins, clinical episodes, and analytic code without presenting synthetic outputs as actual Medicare population estimates.

Strategic design rationale is documented in the [project proposal](docs/medicare-synth-project-proposal_20260720.md).

## Core Capabilities & Domain Coverage

Medicare-Synth provides full schema contracts, evidence snapshots, and validators across 19 contemporary Medicare tables:

### 1. Master Beneficiary Summary File (MBSF) (10 Segments)
- **Base / Enrollment**: Beneficiary demography, Medicare enrollment months, Part A/B buy-in status, dual eligibility (`mbsf_base_enrollment`).
- **Chronic Conditions**: 27 chronic condition flag indicators (`mbsf_chronic_conditions`).
- **Cost & Use**: Annual Medicare payments, beneficiary cost-sharing, covered days (`mbsf_cost_and_use`).
- **Part D Characteristics**: Part D plan contract/PBP identifiers, low-income subsidy, TRCC/MOOP amounts (`mbsf_part_d`).
- **Other Chronic Conditions**: Additional chronic condition flags (`mbsf_other_chronic_conditions`).
- **National Death Index (NDI)**: NDI match indicator and underlying cause of death code (`mbsf_ndi`).
- **Risk Adjustment**: CMS-HCC and RxHCC risk scores (`mbsf_risk_adjustment`).
- **Part C / Medicare Advantage**: Medicare Advantage plan contract identifiers and enrollment months (`mbsf_part_c`).
- **Fee-For-Service (FFS) Utilization**: Annual FFS encounter counts by care setting (`mbsf_ffs_utilization`).
- **Part D PDE Utilization**: Annual Part D prescription fill counts and expenditure metrics (`mbsf_pde_utilization`).

### 2. Clinical Claims & Events (9 Tables)
- **Beneficiary Root**: Core beneficiary demographic and mortality record (`beneficiary_summary`).
- **Inpatient Claims**: Hospital stays, admission/discharge dates, DRG codes, utilization days (`inpatient_claims`).
- **Outpatient Claims**: Facility encounters, service dates, HCPCS procedure codes, APCs (`outpatient_claims`).
- **Carrier Claims**: Professional claims, NPI provider IDs, HCPCS procedure codes, diagnosis codes (`carrier_claims`).
- **Skilled Nursing Facility (SNF) Claims**: Post-acute SNF stays, admission/discharge dates, covered days (`snf_claims`).
- **Home Health Agency (HHA) Claims**: HHA care episodes, visit counts, LUPA indicators (`hha_claims`).
- **Durable Medical Equipment (DME) Claims**: DME supplies, line-item counts, service type codes (`dme_claims`).
- **Hospice Claims**: Terminal illness diagnosis codes, hospice care stay days (`hospice_claims`).
- **Prescription Drug Event (PDE)**: Part D drug dispenses, NDC drug codes, days supply, quantity, cost fields (`pde_events`).

### 3. Engine Features
- **Relational & Temporal Validation**: Polars-backed FK checks (`CLM_ID` -> `BENE_ID`), date sequence integrity (`CLM_FROM_DT` <= `CLM_THRU_DT`), age bounds, mortality temporal constraints, and code format contracts (ICD, HCPCS, NPI, NDC, DRG, POS, Taxonomy, REV_CNTR).
- **RKB Evidence Framework**: Pinned ResDAC Knowledge Base evidence snapshot (`rkb-v1.0-20211231.json`) enforcing variable definitions, types, formats, and valid value sets.
- **Scenario Compiler & Catalog**: 21 named valid and anomaly scenario fixtures (`valid_baseline_cohort`, `invalid_orphaned_claim`, `invalid_temporal_inversion`, etc.).
- **Dataset Expansion Engine**: Vertical within-table attribute synthesis (`TabDat-Synth` adapter) and Horizontal connected-subgraph scaling with deterministic re-keying.
- **Privacy & Quality Audit**: Tabular join coverage profiling and k-anonymity privacy scoring across all 19 domain tables.
- **Release Exporter & CI Fixtures**: SHA256 checksummed Parquet/CSV release bundles, SQL reference DDL generation, and automated CI fixture export.
- **Autonomous Workflow Automation**: Integrated `auto-workflow` engine executing 40+ verification checks, static analysis, test suites, git status verification, and GitHub CLI PR merges.

## CLI Subcommands

| Subcommand | Description |
| :--- | :--- |
| `validate` | Run relational and temporal validation on scenario fixtures |
| `scenario` | Compile and inspect deterministic scenario slices |
| `manifest` | Inspect source baseline manifests or RKB evidence snapshots |
| `export` | Export scenario fixtures or baseline slices to release bundles |
| `expand` | Scale datasets vertically (synthesis) or horizontally (re-keying) |
| `catalog` | List catalog scenario fixtures or export teaching/CI fixtures |
| `diff` | Compare RKB evidence snapshots to identify schema changes |
| `profile` | Generate dataset limitations and fidelity disclosure profiles |
| `export-ci` | Export lightweight CI test fixtures in Parquet or CSV |
| `audit` | Compute join coverage and k-anonymity privacy scores |
| `auto-workflow` | Run autonomous verification checks, git integration, and PR workflows |

## Contributor Guide

- Use `uv` for Python environments, dependency management, and tool execution.
- Maintain static typing (`basedpyright`), pure transformations, explicit state, and side-effect isolation.
- Write behavioral unit tests prior to feature implementation.
- Use 2-space indentation unless a file format specifies otherwise.
- Keep `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, and `CHANGELOG.md` synchronized with codebase capabilities.
- Store temporary data artifacts under the ignored `data/` directory.

### Local Verification Suite

Run the full local check suite before committing changes:

```shell
uv run pytest
uv run basedpyright
uv run ruff check .
git diff --check
```

## Agent Harness

Domain or release-affecting changes follow the repository-local workflow in [docs/harness/medicare-synth/team-spec.md](docs/harness/medicare-synth/team-spec.md). Handoffs and review artifacts are recorded in ignored `_workspace/` directories.

Repository-wide agent rules are defined in [AGENTS.md](AGENTS.md), and reusable domain skills live in `.agents/skills/`.

## Canonical Documentation

- [SPEC.md](SPEC.md): Completed, active, and planned technical specifications
- [ARCHITECTURE.md](ARCHITECTURE.md): System component boundaries and data flow contracts
- [ROADMAP.md](ROADMAP.md): Milestone progress and exit criteria
- [CHANGELOG.md](CHANGELOG.md): Version history and contributor notes
- [LESSONS.md](LESSONS.md): Verified setup and operational traps

## Limitations and Disclaimer

Medicare-Synth is designed for software engineering, pipeline development, methods testing, and education. Structural and relational validity does not imply population representativeness, clinical validity, or formal privacy guarantees. Synthetic outputs should never be cited as empirical Medicare population statistics.
