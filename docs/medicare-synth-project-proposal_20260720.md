---
title: "Medicare-Synth"
subtitle: "A Provenance-Backed System for Contemporary Medicare Synthetic Data and Research Fixtures"
author: "Sae-Hwan Park"
date: "2026-07-20"
status: "Project proposal"
project: "Medicare-Synth"
repository: "medicare-synth"
repository_url: "https://github.com/SaehwanPark/medicare-synth"
keywords:
  - Medicare
  - synthetic data
  - claims data
  - CCW
  - ResDAC
  - research software
  - reproducibility
---

# Medicare-Synth

**A Provenance-Backed System for Contemporary Medicare Synthetic Data and Research Fixtures**

*Canonical CMS synthetic baseline · executable CCW-style schemas · relational validation · evidence-graded expansion*

*Prepared for project planning and contributor alignment*

# Executive Summary

**Medicare-Synth** is a proposed open-source system for constructing contemporary, versioned Medicare synthetic datasets and research fixtures. The project is motivated by a practical gap: researchers and developers often need to design and test Medicare analyses before they can access restricted data in the Chronic Conditions Warehouse Virtual Research Data Center (CCW VRDC), yet older public synthetic files do not fully match current Medicare file structures, field coverage, or relational complexity.

The proposed system will treat CMS’s current synthetic Medicare collection as the canonical empirical baseline rather than recreating Medicare-like data from first principles. It will preserve official synthetic records where possible, add missing fields or structures through evidence-graded methods, expand the cohort horizontally when larger datasets are needed, and generate deterministic scenarios for software testing and education. The system will emphasize structural and relational validity over claims of population representativeness.

Three existing projects provide a distinctive foundation. `rkb-rust` and `resdac-knowledge-base` can supply preserved, citation-bearing CMS and ResDAC documentation and structured variable metadata. `tabdat-synth` can provide transparent, directed acyclic graph (DAG)-based conditional synthesis within tables. **Medicare-Synth** will sit above these systems, owning executable file schemas, cross-table relationships, event construction, domain constraints, validation, scenario generation, and release packaging.

> **Core proposition**
>
> Build a reproducible compiler from official CMS synthetic data, public documentation, explicit Medicare domain constraints, statistical generation specifications, and named scenarios into versioned Medicare research fixtures.

The primary users will be Medicare researchers, VRDC programmers, research software engineers, educators, statistical-methods developers, feasibility teams, and open-source maintainers. The project’s value is not that analyses on synthetic data reproduce real Medicare estimates. Its value is that programs, schemas, joins, episodes, edge cases, and study workflows can be developed and tested much earlier, more openly, and with clearer provenance.

# 1. Background and Problem Statement

## 1.1 The development gap in Medicare research

Medicare research frequently begins before investigators can inspect the eventual analytic files. Teams must select data products, define cohorts, choose fields, estimate computing requirements, and design code while relying primarily on documentation. Real data may later be available only in a controlled environment, often after substantial administrative and financial commitment.

This sequence creates a costly mismatch between when design decisions are made and when the data structure can be tested. Researchers may discover late that a file has a different grain than assumed, that a claim definition requires multiple file families, that joins multiply rows, that code arrays are represented differently across years, or that an apparently straightforward episode definition requires complex header-line and cross-setting logic.

## 1.2 Limitations of existing public synthetic data

The original Medicare SynPUF remains useful for training and software development, but it reflects older data years and older file structures. It does not fully represent the current breadth of Medicare fields, revised beneficiary summary files, contemporary claim layouts, or the increasingly complex relationships among enrollment, claims, lines, providers, plans, and prescription events.

CMS’s newer synthetic Medicare collection materially improves the starting point. It should be treated as the canonical baseline because it is official, contemporary, already relational, and designed to resemble current Medicare research files. The proposed project will therefore focus on preserving, validating, extending, scaling, and operationalizing this official baseline rather than replacing it.

## 1.3 Why a pipeline is more valuable than a static synthetic release

Medicare schemas change over time. Variables are added, retired, renamed, redefined, or moved across file families. Documentation and data availability also evolve. A static synthetic dataset will become outdated quickly. A pipeline can instead encode versioned schemas, preserve evidence snapshots, compare documentation changes, regenerate releases, and maintain deterministic fixtures across data years.

The project should therefore be understood as infrastructure: a versioned data construction and validation system that can produce multiple releases, scales, scenarios, and schema-year targets.

# 2. Project Vision and Objectives

## 2.1 Vision

Enable researchers and developers to move from a Medicare research idea to a tested, documented, and structurally credible implementation before executing against restricted data.

## 2.2 Primary objectives

1. Preserve and normalize CMS’s official synthetic Medicare data as the canonical baseline.

1. Translate public CMS and ResDAC documentation into provenance-bearing executable file specifications.

1. Represent and validate beneficiary, enrollment, claim, line, provider, and event relationships explicitly.

1. Support evidence-graded vertical expansion of missing fields and file structures.

1. Support relationally coherent horizontal expansion for larger populations and performance testing.

1. Provide deterministic named scenarios, expected outputs, and intentionally invalid fixtures.

1. Export data in formats suitable for Python, R, SQL, PySpark, Databricks, and continuous integration.

1. Make every release reproducible through pinned data sources, evidence snapshots, models, assumptions, and checksums.

## 2.3 Non-goals

- Replacing real Medicare data for population inference, policy estimation, or clinical conclusions.

- Claiming national representativeness without explicit supporting calibration evidence.

- Providing formal privacy guarantees solely because the data are synthetic.

- Attempting immediate coverage of every CMS file family and historical layout.

- Using complex generative models where transparent rules or conditional models are sufficient.

- Automatically treating documentation extraction as authoritative executable semantics without review.

# 3. Intended End Users and Needs Analysis

The project serves several related user clusters. Their needs overlap, but the required form of fidelity differs. Researchers need realistic structure and feasibility support; programmers need stable relational fixtures; educators need manageable examples; methods developers need known truth and controllable data-generating mechanisms.

| **User cluster**                          | **Typical pain points**                                                                                                                           | **Project contribution**                                                                                                                  |
|-------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Medicare claims researchers               | Cannot inspect final data during study design; difficult file grain and linkage; late discovery of unavailable fields or impractical definitions. | Local prototyping environment, executable schemas, reference workflows, file and field planning, relationally credible examples.          |
| CCW VRDC teams                            | Restricted tooling, expensive debugging cycles, asymmetric access among collaborators, limited ability to share examples.                         | Develop-locally/execute-remotely workflow, deterministic fixtures, version-specific schemas, reduced avoidable VRDC failures.             |
| Research programmers and data engineers   | No dependable test data; manually fabricated rows miss edge cases and one-to-many structures; no known expected output.                           | Unit and integration fixtures, invalid cases, schema compatibility suites, scalable benchmark releases.                                   |
| Educators and trainees                    | Students lack realistic current Medicare data; old or flattened examples hide core administrative structure.                                      | Tiered instructional datasets, exercises, expected outputs, current file layouts, reproducible local setup.                               |
| Statistical and causal-methods developers | Clean one-row datasets do not resemble claims; claims-like data often lack known truth.                                                           | Optional latent-truth simulation, claims observation models, benchmark estimands, controlled confounding and misclassification scenarios. |
| Study feasibility and data-request teams  | Must choose files and years before understanding relationships or implementation needs.                                                           | Executable data-needs analysis, field manifests, unresolved dependency reporting, prototype-based feasibility checks.                     |
| Open-source and product developers        | Cannot ship restricted test data or reproduce customer defects publicly.                                                                          | Redistributable CI fixtures, scenario reproduction, API/database seed data, performance benchmarks.                                       |

# 4. Strategic Positioning

## 4.1 Product category

The project should not be positioned primarily as a general-purpose synthetic data package or as a substitute for Medicare claims. Its strongest category is a Medicare data emulator and research-fixture compiler with optional statistical calibration.

> **Data flow**
>
> Public documentation → RKB evidence snapshot → executable Medicare schemas. Official CMS synthetic files → baseline normalization → canonical entities and events. Schemas + baseline + `tabdat-synth` models + domain constraints → validated releases and deterministic scenarios.

# 6. Data and Evidence Strategy

## 6.1 Canonical baseline

CMS’s current synthetic Medicare data should be preserved as immutable source material. Each release will record source URLs, retrieval dates, checksums, file names, data years, and raw sizes. Normalized derivatives must retain lineage back to source rows and files.

## 6.2 Evidence hierarchy

1. Official CMS synthetic baseline records and observed relationships.

1. Current CMS and ResDAC data dictionaries, layouts, user guides, and technical documentation.

1. Current public CMS aggregate, provider, utilization, payment, and enrollment data.

1. Other government datasets and technical references.

1. Peer-reviewed literature.

1. Older public synthetic data such as DE-SynPUF.

1. Explicit domain assumptions and sensitivity profiles.

The hierarchy is not a mechanical ranking of truth. Documentation may define semantics while aggregate data provide calibration and the synthetic baseline provides joint structure. The project should record how each evidence type contributes to each field or relationship.

## 6.3 Field provenance statuses

| **Status**            | **Meaning**                                                                                |
|-----------------------|--------------------------------------------------------------------------------------------|
| Preserved             | Copied from the official CMS synthetic baseline without semantic modification.             |
| Normalized            | Reformatted or typed while retaining the baseline meaning and recoverable raw value.       |
| Re-keyed              | Synthetic identifier replaced deterministically to support expansion or release isolation. |
| Derived               | Calculated deterministically from documented source fields.                                |
| Imputed               | Completed conditionally where the baseline or target layout lacks a value.                 |
| Synthesized           | Generated statistically from fitted or specified models.                                   |
| Externally calibrated | Adjusted to match documented external aggregate targets.                                   |
| Scenario-generated    | Created intentionally to support a named test or educational case.                         |

## 6.4 Documentation-driven, not documentation-determined

RKB can establish that a variable exists, belongs to a file, is available in certain years, and has a documented definition. The executable project must still determine grain, physical type, null semantics, key relationships, arithmetic constraints, and generation behavior. Conflicts or gaps should remain explicit rather than being resolved silently.

# 7. Data Model and Generation Approach

## 7.1 Two-level DAG design

The project should separate a relation-level DAG from column-level DAGs. The relation DAG determines entity and table generation order, cardinalities, key propagation, event relationships, and cross-table constraints. Within each table, `tabdat-synth` or deterministic rules generate fields in topological order.

| **Layer**          | **Examples of responsibilities**                                                                                                                                          |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Relation/event DAG | Beneficiary before enrollment; claim before lines; episode before related facility and professional records; parent-child counts; provider assignment; temporal sequence. |
| Column DAG         | Place of service → HCPCS → modifier → units → allowed amount → payment; demographics → condition indicators → utilization propensity.                                     |

## 7.2 Canonical internal model

The internal representation should include beneficiaries, beneficiary-years, beneficiary-months, enrollment episodes, providers, facilities, plans, claims, lines, diagnoses, procedures, prescription events, and care episodes. A canonical event should be able to render into multiple file records, such as an emergency encounter producing outpatient facility, carrier professional, and possible inpatient records.

## 7.3 Vertical expansion

Vertical expansion adds fields, arrays, line structures, or file families to existing baseline entities. Methods should be selected in the following order: deterministic derivation, rule-constrained completion, empirical conditional sampling, transparent statistical modeling, external calibration, and explicit assumptions. Each field must retain its source status and evidence.

## 7.4 Horizontal expansion

Horizontal expansion creates additional beneficiaries, providers, claims, events, and years. The initial method should resample connected beneficiary subgraphs rather than independent rows. Re-keying must preserve all relationships, temporal order, and event coherence. More advanced models can later generate claim counts, event sequences, and provider assignments conditionally.

## 7.5 Scenario generation

Scenario mode should create small, interpretable datasets with stable expected outputs. Scenarios may represent common workflows, rare but valid cases, and intentional invalidity. They should be defined declaratively, generated deterministically, and versioned with their expected analytic results.

- Minimal carrier claim and multi-line professional claim.

- Emergency department visit followed by inpatient admission.

- Observation services converted to admission.

- Ambulance-linked emergency encounter.

- Inpatient-to-SNF-to-home-health sequence.

- Enrollment gap, death during follow-up, and post-death invalid claim.

- Original, replacement, and final-action claim sequence.

- Zero-paid, denied, deductible, coinsurance, and adjustment cases.

# 8. Validation and Quality Assurance

## 8.1 Validation layers

| **Layer**      | **Illustrative checks**                                                                                        |
|----------------|----------------------------------------------------------------------------------------------------------------|
| Field          | Type, width, date format, code domain, nullability, numeric range.                                             |
| Record         | Date ordering, conditional presence, mutually exclusive fields, arithmetic relationships.                      |
| Relational     | Primary and foreign keys, parent-child cardinality, claim-line counts, enrollment-service compatibility.       |
| Administrative | Claim setting, code compatibility, adjustment logic, provider role, final-action behavior.                     |
| Scenario       | Expected episode count, utilization indicator, total payment, continuous enrollment, known validation failure. |
| Distributional | Marginals, joint distributions, counts, payments, provider concentration, longitudinal patterns.               |

## 8.2 Validation philosophy

The validator should be built before broad synthesis. It must distinguish errors, warnings, informational findings, baseline exceptions, documentation ambiguities, and assumption conflicts. Official baseline anomalies should not be silently repaired; they should be registered and handled deliberately.

## 8.3 Release claims

Each release should publish an explicit fidelity profile. For example, a release may claim verified schema and referential fidelity, strong temporal validation, partial accounting fidelity, and only descriptive distributional similarity. This prevents the term “realistic” from obscuring which properties were actually tested.

# 9. User-Facing Products

## 9.1 Release formats

- CSV for portability and simple teaching workflows.

- Parquet for typed, scalable Python, R, Spark, and Databricks workflows.

- DuckDB or SQLite fixtures for SQL-first exploration and testing.

- Small package-embedded fixtures for continuous integration.

- Optional fixed-width or other layout-specific exports where justified.

## 9.2 Interfaces

A command-line interface should be the primary operational interface, with a focused Python API for programmatic composition. Commands should cover source acquisition, evidence synchronization, schema inspection, normalization, validation, generation, scenario construction, export, reporting, and data-needs analysis.

## 9.3 Documentation and teaching materials

Documentation should include a schema reference, relationship diagrams, scenario catalog, evidence guide, validation guide, limitations, release notes, and cross-language examples. Educational modules should progress from beneficiary files and enrollment to claim headers, lines, episodes, costs, and common join errors.

# 10. Additional Strategic Analyses

## 10.1 Build-versus-reuse analysis

| **Capability**                                      | **Reuse existing project?**                   | **Recommended decision**                                                                               |
|-----------------------------------------------------|-----------------------------------------------|--------------------------------------------------------------------------------------------------------|
| CMS/ResDAC documentation preservation and retrieval | Yes: `rkb-rust` / `resdac-knowledge-base` | Consume versioned evidence artifacts; avoid duplicating crawler and retrieval infrastructure.          |
| Within-table conditional synthesis                  | Yes: `tabdat-synth`                         | Integrate through stable public APIs and fitted bundles.                                               |
| Medicare executable schemas and relation graph      | No suitable existing component                | Build in the **Medicare-Synth** repository.                                                                    |
| Medicare-specific validation and event semantics    | No                                            | Build as a first-class core, before broad generation.                                                  |
| Scenario DSL and expected outputs                   | Partially reusable generic patterns           | Build domain-specific layer with possible future extraction of generic primitives.                     |
| Distributional calibration                          | Some generic methods reusable                 | Implement transparently in the domain project; upstream generic components only after proven reusable. |

## 10.2 Adoption pathway analysis

Early adoption is most likely among expert users who already experience the pain directly: Medicare programmers, VRDC analysts, and claims-methods developers. Education and broader product use should follow after the file models and scenarios stabilize. The initial release should therefore optimize correctness, inspectability, and reproducibility rather than ease-of-use for every audience.

1. Expert alpha: baseline inventory, validators, carrier/outpatient fixtures, CLI.

1. Research developer beta: deterministic scenarios, horizontal scaling, reference workflows.

1. Teaching and open-source release: small curated datasets, tutorials, CI adapters.

1. Methods platform: latent truth, observation models, benchmark protocols.

1. Broader ecosystem integration: data-needs planning, agent interfaces, enterprise-scale benchmarks.

## 10.3 Sustainability analysis

The primary maintenance burden will arise from annual data-layout changes, documentation drift, baseline release changes, and expanding file coverage. Sustainability depends on machine-readable schemas, automated evidence and schema diffs, generated documentation, bounded release targets, and a strict separation between verified core specifications and experimental community contributions.

## 10.4 Ethical and interpretive analysis

A plausible synthetic dataset can create false confidence. The project must repeatedly distinguish software validity, structural validity, methodological validity, and external validity. Passing a synthetic scenario proves that code behaves under that scenario; it does not prove that a Medicare population estimate is correct. Release documentation and APIs should reinforce this distinction.

## 10.5 Competitive and complementary landscape

The project is complementary to generic synthetic-data libraries, EHR simulators, common data models, claims documentation portals, and CMS public-use files. Its differentiation lies in making contemporary Medicare structures executable, relationally testable, provenance-bearing, and configurable. It should integrate with broader tools rather than attempt to replace them.

# 11. Risks and Mitigation

| **Risk**                     | **Consequence**                                                 | **Mitigation**                                                                                        |
|------------------------------|-----------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Scope expansion              | Attempting all files and years delays a credible release.       | Start with beneficiary, carrier, and outpatient structures; require file-family milestones.           |
| False inferential confidence | Users may interpret plausible results as Medicare estimates.    | Publish explicit fidelity profiles, limitations, and separate baseline/test/methods modes.            |
| Documentation ambiguity      | Conflicting or incomplete semantics lead to hidden assumptions. | Preserve conflicts, evidence status, reviewer decisions, and unresolved registries.                   |
| Relational inconsistency     | Independent table synthesis produces impossible data.           | Generate from event/relation DAGs; validate foreign keys, time, counts, and accounting.               |
| Repository coupling          | Changes in RKB or `tabdat-synth` destabilize releases.        | Use versioned evidence artifacts, pinned packages, stable public interfaces, and compatibility tests. |
| Maintenance burden           | Annual updates become labor-intensive.                          | Automate schema/evidence diffs, generated docs, and annual update playbooks.                          |
| Model opacity                | Sophisticated models obscure administrative errors.             | Rules before models; transparent methods; retained fitted artifacts and diagnostics.                  |
| Performance constraints      | Large synthetic releases become impractical locally.            | Streaming, partitioned Parquet, bounded-memory validation, deterministic parallelism.                 |

# 12. Governance and Contribution Model

## 12.1 Roles

- Core maintainers: architecture, release approval, dependency policy, and backward compatibility.

- Schema reviewers: file grain, field definitions, year availability, keys, and layout compatibility.

- Domain reviewers: claims semantics, enrollment, payments, code relationships, and event logic.

- Methods reviewers: synthesis assumptions, calibration, simulation truth, and evaluation design.

- Evidence maintainers: RKB snapshots, provenance, source conflicts, and documentation coverage.

## 12.2 Specification status model

Schemas and models should progress through explicit states such as proposed, evidence-backed, experimentally implemented, validated against baseline, reviewed, stable, and deprecated. Experimental extensions should not inherit the credibility of verified core fields merely because they appear in the same output.

## 12.3 Release manifest

Every release should pin the software version, CMS synthetic baseline release, raw checksums, RKB evidence snapshot, schema version, constraint set, assumption profile, `tabdat-synth` version, fitted artifacts, calibration targets, validation results, and known deviations.

# 13. Evaluation and Success Metrics

## 13.1 Structural metrics

- Percentage of output fields with verified documentation or explicit assumption status.

- Primary-key and foreign-key violation rates.

- Temporal and enrollment-compatibility violation rates.

- Claim-line and payment reconciliation rates.

- Round-trip fidelity for preserved baseline fields.

- Coverage of file-year schema differences.

## 13.2 Engineering metrics

- Deterministic reproduction under fixed manifests and seeds.

- Generation and validation throughput at standard scale profiles.

- Memory use and partitioning behavior.

- Number of downstream libraries or pipelines using project fixtures.

- Number and type of VRDC failures prevented or identified locally.

- Continuous-integration runtime for compact fixtures.

## 13.3 User and scientific metrics

- Completion of representative local-to-VRDC workflows.

- Use in teaching modules, workshops, and reproducible manuscripts.

- Accuracy of expected outputs for named scenarios.

- For methods mode, recovery of known estimands within Monte Carlo error.

- User-reported clarity of file selection, relationships, and limitations.

# 14. High-Level Implementation Roadmap

The detailed, phase-by-phase project roadmap is maintained as a separate companion document. The proposal intentionally summarizes the implementation sequence rather than duplicating that operational plan.

| **Stage**                | **High-level outcome**                                                                                             |
|--------------------------|--------------------------------------------------------------------------------------------------------------------|
| Foundation               | Finalize scope, governance, fidelity definitions, manifests, and architecture decisions.                           |
| Baseline and evidence    | Acquire and inventory the official CMS synthetic collection; integrate a pinned RKB evidence snapshot.             |
| Executable model         | Define canonical entities, event model, table schemas, relation graph, constraints, and schema compiler.           |
| Validation-first release | Normalize and round-trip the baseline; publish validation findings and a focused relational release.               |
| Expansion                | Add fields and file families vertically; expand beneficiaries and events horizontally; integrate `tabdat-synth`. |
| Scenario framework       | Publish deterministic valid and invalid fixtures with expected analytic outputs.                                   |
| Calibration and methods  | Add evidence-based aggregate calibration, latent truth, and claims observation models where justified.             |
| Adoption and maintenance | Stabilize CLI/API, education, cross-language support, annual update workflows, and release governance.             |

> **Roadmap boundary**
>
> The separate roadmap document should remain the canonical source for phases, sub-phases, deliverables, exit criteria, milestone ordering, and implementation acceptance tests.

# 15. Recommended Initial Scope

The first credible release should be intentionally narrow. It should demonstrate the complete architecture rather than broad but weak file coverage.

- One pinned official CMS synthetic baseline release.

- Beneficiary enrollment records sufficient for service-date validation.

- Carrier claim headers and lines.

- Outpatient claim headers and revenue-center lines.

- RKB evidence bundle for the selected files and years.

- Canonical import, validation, and Parquet/CSV export.

- A small CLI and Python API.

- Five deterministic scenarios, including ED-to-inpatient and enrollment-gap cases.

- Reference analyses in pandas and SQL, with PySpark support soon after.

- One narrowly selected vertical expansion using `tabdat-synth` to prove integration.

# 16. Immediate Decisions Required

1. Select the project name and repository boundary.

1. Select the first official CMS synthetic baseline release and target schema year.

1. Confirm the first file families: beneficiary, carrier, and outpatient are recommended.

1. Define the RKB evidence-bundle contract and snapshot policy.

1. Choose the canonical schema language and runtime validation library.

1. Define the minimum set of constraints required before any expansion is permitted.

1. Specify the first five scenarios and their expected analytic outputs.

1. Define release licensing, source-data redistribution rules, and artifact publication strategy.

# 17. Conclusion

This project addresses a concrete and persistent problem in Medicare research: the inability to develop, test, teach, and share realistic claims workflows before restricted data access. Its strongest design choice is to begin with CMS’s official synthetic Medicare data and extend it conservatively, transparently, and reproducibly rather than synthesizing an entire Medicare-like world from assumptions.

The combination of RKB’s provenance-bearing documentation, `tabdat-synth`’s explicit conditional generation, and **Medicare-Synth** as the Medicare-specific relational and validation layer creates a differentiated technical foundation. The resulting system could serve simultaneously as a local development environment, claims testing framework, educational resource, feasibility tool, and eventually a known-truth methods platform.

The project should initially optimize for correctness, inspectability, and practical transfer to real CCW workflows. If those foundations are strong, broader statistical realism, file coverage, and scale can be added without compromising trust.

# References and Project Resources

**CMS Synthetic Medicare Enrollment, Fee-for-Service Claims, and Prescription Drug Event collection:** https://data.cms.gov/collection/synthetic-medicare-enrollment-fee-for-service-claims-and-prescription-drug-event

**CMS Medicare Claims Synthetic Public Use Files:** https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files

**CCW data dictionaries and standard analytic files:** https://www2.ccwdata.org/web/guest/data-dictionaries

**TabDat-Synth repository:** https://github.com/SaehwanPark/tabdat-synth

**RKB Rust repository:** https://github.com/SaehwanPark/rkb-rust

**ResDAC Knowledge Base repository:** https://github.com/SaehwanPark/resdac-knowledge-base
