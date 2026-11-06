---
title: "Medicare-Synth: Evidence-Calibrated Research Playground"
subtitle: "Project proposal and phased implementation roadmap"
author: "Sae-Hwan Park"
date: "2026-11-06"
status: "Proposal / discussion draft"
repository: "https://github.com/SaehwanPark/medicare-synth"
version: "0.1-draft"
keywords:
  - Medicare
  - synthetic data
  - research playground
  - literature-informed calibration
  - evidence representation
  - reproducibility
  - multi-world simulation
---

# Medicare-Synth: An Evidence-Calibrated Research Playground

**Project proposal and phased implementation roadmap**  
**Date:** November 6, 2026  
**Status:** Discussion draft; not an implementation or evaluation report  
**Repository:** [SaehwanPark/medicare-synth](https://github.com/SaehwanPark/medicare-synth)

> **Core proposition**  
> Build an open-source, configurable, literature-grounded Medicare research playground: a system that produces structurally valid and contextually plausible synthetic datasets so researchers can prototype, debug, and stress-test ideas before incurring the substantial time, access, and financial costs of working with restricted Medicare data.

> **Boundary statement**  
> The goal is **not** to reconstruct actual Medicare beneficiaries, reproduce individual claims or patient trajectories, or recover the full joint distribution of the real Medicare population. Synthetic results are not empirical Medicare estimates and do not substitute for analysis on authorized real data.

## Executive summary

Medicare research often demands substantial up-front work: identifying appropriate Medicare data products, specifying beneficiary cohorts, understanding multiple claims grains and enrollment rules, developing code for longitudinal features and outcomes, and determining whether a methodological idea is feasible. Restricted data access, costly computing environments, governance procedures, and long setup cycles can prevent early experimentation. Public synthetic Medicare data reduce some barriers, but structural plausibility alone does not create a useful statistical environment for research.

**Medicare-Synth** currently focuses on provenance-backed Medicare-like data structures and reproducible research fixtures. Its repository includes an official synthetic CMS baseline, 2021-schema-oriented domain models, extensive field and relational validation, deterministic scenarios, export bundles, and expansion mechanisms. These capabilities provide a foundation for a more ambitious—but carefully bounded—extension: **evidence-calibrated synthesis**.

The proposed extension will use official public aggregate statistics and well-characterized findings from studies restricted to Medicare populations as **contextual statistical constraints**. A machine-readable evidence intermediate representation (IR) will express study populations, eligibility, variables, outcomes, estimands, uncertainty, and applicability. A calibration engine will search for synthetic distributions that satisfy relevant constraints while preserving administrative integrity and providing meaningful statistical variation. An agent harness will support discovery, extraction, translation, compatibility assessment, orchestration, and auditing, without becoming the unreviewed authority for statistical decisions.

Rather than emit one allegedly representative “synthetic Medicare population,” the system should support **multiple plausible synthetic worlds** that satisfy shared evidence and differ transparently in poorly identified dimensions, modeling assumptions, missingness patterns, confounding, and heterogeneity. This better serves the intended use: rapid, low-cost *research preparation*, not inference about actual Medicare beneficiaries.

The development program is organized into eight coordinated phases (0–7), culminating in a bounded MVP, independent validation, and controlled expansion across additional literature and use cases. A successful MVP will demonstrate that the platform (i) generates valid, nontrivial synthetic beneficiary/claims data, (ii) executes formalized published findings against those data, (iii) improves selected contextual realism through calibration, and (iv) enables realistic analytic workflows and controlled stress tests without making unsupported fidelity claims.

## 1. Motivation and problem statement

### 1.1 The research-development gap

Medicare studies are expensive to set up and difficult to iterate on. Teams frequently need to make consequential choices before they can see the authorized study data:

- Which Medicare products, files, years, and enrollment definitions are required?
- Which joins operate at beneficiary, beneficiary-year, claim-header, claim-line, encounter, or prescription-event grain?
- Can exposure, covariate, outcome, and follow-up definitions be implemented correctly?
- What forms of temporal confounding, missingness, censoring, class imbalance, or sparse subgroups might undermine the proposed method?
- Can a proposed modeling or evaluation pipeline be developed and tested before access to restricted data is approved?
- How will code and assumptions transfer into the eventual secure environment?

CMS's historical description of synthetic Medicare claims explicitly emphasizes developing programs and familiarizing analysts with Medicare data without first purchasing restricted files. Medicare-Synth builds on this established developer-support role, adding controlled, study-relevant statistical context where the existing public synthetic files are insufficient. See [CMS Medicare Claims Synthetic Public Use Files](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files).

### 1.2 Structural validity is necessary but not sufficient

A dataset may satisfy valid ICD code formats, date sequences, foreign keys, accounting constraints, and enrollment logic while still being an unhelpful statistical test environment. Examples include:

- all patients with a chronic condition being assigned exactly the same event probability;
- implausibly strong or weak associations between chronic disease and hospitalization;
- nonexistent variation in treatment utilization across age groups;
- uninformative censoring or missingness when the intended method is meant to handle those difficulties;
- mechanically duplicated patients that inflate nominal sample size without adding statistical support;
- unrealistically easy classification tasks because outcomes are nearly deterministic.

Such datasets are suitable for software smoke tests but may fail to expose meaningful problems in research ideas. Conversely, exact recreation of the true Medicare distribution is neither necessary nor attainable from the available public evidence. The practical requirement is **adequate contextual realism for a declared research purpose**.

### 1.3 Opportunity: use the literature as evidence, not as a claim of reconstruction

Published Medicare studies and CMS public aggregate products expose selected characteristics of underlying populations: disease prevalence, utilization rates, spending summaries, associations, risks, and outcome distributions. These measurements can constrain generated worlds even when the individual-level data underlying them are unavailable.

The proposed system will use such evidence to build and evaluate plausible analysis environments. It will not assume that a collection of reported results fully determines the real joint distribution. Indeed, several distinct synthetic worlds may satisfy the same evidence. That uncertainty is a feature to expose, not a problem to conceal.

## 2. Mission, vision, and positioning

### Mission

**Medicare-Synth is an open-source framework for generating structurally valid, contextually realistic synthetic Medicare datasets that enable researchers to develop, prototype, and stress-test research ideas before transitioning to restricted Medicare data.**

It combines administrative specifications, transparent synthetic generation, and reviewed empirical constraints drawn from public CMS products and published Medicare research. Its output is a configurable **research playground**, not a statistical replacement for the real Medicare population.

### Long-term vision

A researcher should be able to select a Medicare research context, request a modest synthetic cohort with connected administrative records, construct a cohort and longitudinal analytic table, fit or evaluate a model, explore failure modes across several plausible worlds, and export the same analysis specification or code structure for subsequent execution in an authorized Medicare environment.

### Product positioning

| Layer | Core question | Success looks like | Out of scope |
|---|---|---|---|
| Structural realism | Is this recognizable, valid Medicare-like data? | Correct grains, keys, codes, enrollment logic, and chronology | One-to-one representation of real claims |
| Contextual statistical realism | Does this environment exhibit plausible domain relationships? | Evidence-compatible marginals and conditional associations, with uncertainty | Recovery of the full real Medicare distribution |
| Research-workflow realism | Can researchers meaningfully exercise their methods? | Executable cohort/feature/outcome definitions; useful heterogeneity and edge cases | Synthetic effect estimates treated as real findings |
| Reproducible experimentation | Can a colleague repeat and inspect the work? | Pinned generator, evidence, seeds, assumptions, and release manifests | Hidden, mutable agent decisions |

### Intended users

- **Medicare investigators and methodologists:** early feasibility, model prototyping, analytic plan stress tests.
- **Research data scientists and statisticians:** simulation, sensitivity analysis, survival/prediction-method development.
- **Research programmers and VRDC teams:** schema-aware ETL, cohort logic, longitudinal feature pipelines, transfer of code into secure environments.
- **Educators and trainees:** practical Medicare-like datasets with known assumptions and exercise-ready scenarios.
- **Software and infrastructure developers:** regression tests, performance experiments, and integration validation using shareable fixtures.

### Non-goals and forbidden inferences

1. No intent to recover, approximate, or identify actual individual beneficiaries, claims, or providers.
2. No claim of population representativeness merely because a dataset matches published statistics.
3. No publication of synthetic-data estimates as if they were estimates from restricted Medicare data.
4. No claim that a synthetic model's effect sizes, accuracy, calibration, or subgroup performance will transfer unchanged to real data.
5. No claim of causal validity unless a separate simulation design explicitly defines causal truth and assumptions; synthetic associations are not real causal effects.
6. No guarantee of formal privacy or non-disclosure solely because the output is called synthetic. Privacy and licensing reviews remain necessary if source inputs change.
7. No autonomous adoption of extracted literature facts without reviewable evidence, compatible estimand semantics, and approval.
8. No commitment to universal coverage of all Medicare programs, years, claim families, or published studies in the MVP.

## 3. Starting point: current repository and capability gap

The [current repository](https://github.com/SaehwanPark/medicare-synth) provides the architectural foundation. A read-only examination of its public `main` branch and canonical documents (November 6, 2026) indicates the following.

| Area | Present capability | Implication for the extension |
|---|---|---|
| Source and metadata | Checksummed CMS 2021 Synthetic Claims baseline; bounded 2022 PUF path; evidence snapshots | Preserve provenance, versions, and documented file-year boundaries |
| Domain and validation | Pydantic v2 contracts and Polars-based record, relational, temporal, administrative, and accounting checks | Reuse hard validity constraints for all calibrated worlds |
| Breadth | Canonical documentation references 19 domain tables across claims, MBSF, and related data | Select only the subset demonstrated end-to-end for the MVP |
| Vertical synthesis | Built-in `TabDatSynthAdapter` presently generates deterministic features from row indices and seeds | Replace or extend with a genuine conditional generation capability for statistical research contexts |
| Horizontal expansion | `HorizontalExpander` replicates connected beneficiary subgraphs with deterministic re-keying | Useful for structural load testing, but not an independent statistical sample or a new generator |
| Release system | Versioned CSV/Parquet export, checksums, validation, provenance, limitation profiles | Extend to evidence and calibration reports, model manifests, world definitions |
| Calibration | `EXTERNALLY_CALIBRATED` is already recognized as a provenance status | Add a substantive calibration engine; do not assume it already exists |
| Fidelity reporting | Predominantly structural indicators | Add contextual, external, uncertainty, and workflow-utility evaluation |

Repository entry points:

- [README.md](https://github.com/SaehwanPark/medicare-synth/blob/main/README.md)
- [ARCHITECTURE.md](https://github.com/SaehwanPark/medicare-synth/blob/main/ARCHITECTURE.md)
- [SPEC.md](https://github.com/SaehwanPark/medicare-synth/blob/main/SPEC.md)
- [ROADMAP.md](https://github.com/SaehwanPark/medicare-synth/blob/main/ROADMAP.md)
- [src/medicare_synth/expansion.py](https://github.com/SaehwanPark/medicare-synth/blob/main/src/medicare_synth/expansion.py)
- [Documented limitations](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/reference/limitations.md)

**Important interpretation:** Current structural and deterministic capabilities are real project assets. They do **not** establish that the present generator has already learned realistic conditional distributions, or that the entire advertised table breadth is ready for a calibrated longitudinal research context. Phase 1 must verify this with experiments rather than relying on documentation alone.

## 4. Research hypotheses and questions

The extension is motivated by the following *testable*, not assumed, propositions.

**H1 — Contextual evidence improves useful realism.** Relative to an uncalibrated structural generator, external evidence constraints reduce pre-specified discrepancies in selected population, condition, utilization, and outcome summaries without breaking structural validity.

**H2 — Calibration generalizes within a coherent context.** Compared with the uncalibrated baseline, calibrated worlds exhibit better agreement on **held-out**, compatible empirical findings, not just fitted evidence.

**H3 — Multiple plausible worlds improve methodological stress testing.** Controlled variation in weakly identified aspects of the data-generating process exposes more research-method failure modes than a single fixed synthetic dataset, while respecting common empirical constraints.

**H4 — The system measurably improves research preparation.** Users can implement and test cohort logic, analytic workflows, or method behavior with lower development friction than manual fixture construction. Actual transfer to restricted data must be evaluated separately when authorized access becomes available.

Associated research questions:

1. Which published quantities can be expressed as executable estimands on the supported Medicare-like schema?
2. How much compatible information is required to obtain useful, nontrivial conditional relationships?
3. When are literature constraints incompatible because of differing populations, time periods, definitions, or actual heterogeneity?
4. When can reweighting calibrate existing samples, and when must a generative mechanism add new support?
5. How should uncertainty and non-identification be communicated in generated worlds?
6. What evaluation criteria best capture *fitness for early research development* rather than superficial summary matching?

## 5. Conceptual operating model

### 5.1 The central workflow

```text
CMS synthetic baseline + schema evidence
                |
                v
       Structural synthesizer --------------------+
                |                                |
                v                                |
      Candidate beneficiary/claims worlds         |
                |                                |
                v                                |
     Evidence-calibration engine <--- Evidence IR <--- Curated CMS aggregates
                |                   ^                      + published studies
                |                   |
                |           Human-reviewed agent workflow
                v
       Calibrated plausible worlds
                |
                +-- structural and temporal validation (hard gates)
                +-- evidence agreement and feasibility diagnostics
                +-- held-out study evaluation
                +-- research-workflow and perturbation benchmarks
                |
                v
          Versioned, transparent releases
```

### 5.2 Distinct responsibilities

- **Synthesis engine:** produces coherent beneficiary-level histories and corresponding administrative records from a controllable generative model.
- **Evidence compiler:** validates and executes literature-derived estimands using explicitly defined cohort and analytic semantics.
- **Calibration engine:** adjusts distributions, weights, or generator parameters using compatible evidence and calibrated uncertainty assumptions.
- **Evaluation engine:** measures hard validity, in-sample and held-out evidence agreement, support/diversity, statistical robustness, and research utility.
- **Agent harness:** assists and orchestrates the work; never silently rewrites empirical facts or scientific objectives.
- **Release/provenance layer:** packages all relevant inputs, hashes, code versions, assumptions, evidence partitions, results, and limitations.

### 5.3 Unit of statistical and administrative coherence

Beneficiaries and their connected enrollment and care histories should be generated or sampled as **coherent subgraphs**. The system should not independently adjust a carrier line, death date, hospitalization, and enrollment month if doing so breaks their logical relationships. Evidence calibration may operate through beneficiary-level weights or generator parameters, while the administrative layer compiles compatible claims records.

The framework does **not** try to match real beneficiaries or real claim lines. It tries to create useful, realistic *types of analytical situations*.

### 5.4 Multiple plausible worlds

Evidence may constrain diabetes prevalence and a hospitalization association without identifying a full distribution of disease severity, treatment selection, or missingness. Rather than fill these gaps with one opaque model, releases should optionally include alternative worlds:

- **Reference world:** central, evidence-compatible assumptions.
- **Heterogeneity world:** stronger, documented subgroup variability within supported bounds.
- **Confounding world:** varied relationships between latent burden, utilization, and outcomes.
- **Missingness/censoring world:** meaningful departures from simple missing-at-random or complete-follow-up settings.
- **Stress-test world:** selected rare events, sparse support, and edge conditions while retaining declared administrative validity.

These are **scenario labels**, not statements that any one world is a faithful representation of actual Medicare. Every variation must document which empirical constraints remain common, which are relaxed, and why.

## 6. Evidence as a first-class, executable research artifact

### 6.1 Why a formal representation is central

Scientific publications typically provide natural-language definitions and summary statistics. They differ in eligibility, enrollment criteria, covariate adjustment, time horizons, coding algorithms, and reporting conventions. A numeric point estimate, stripped of these conditions, is not a valid calibration target.

The project therefore needs a **machine- and agent-friendly evidence intermediate representation** (Evidence IR): a constrained, typed, reviewed object describing exactly what a finding measures and how it can be computed or approximated on the synthetic data.

### 6.2 Proposed Evidence IR capabilities

Each registered finding should record at least:

| Field family | Required content |
|---|---|
| Bibliographic provenance | DOI or stable URL, title, authors, version/date, table/figure/page, extraction provenance |
| Population | Medicare program (Original Medicare FFS, Medicare Advantage, mixed), age, geography, enrollment, coverage, claims availability |
| Time | Study years, baseline/index date, lookback, follow-up, censoring, measurement window |
| Eligibility | Inclusion/exclusion logic, cohort construction, event definitions, denominators |
| Variables | Canonical identifiers, code sets or algorithms, transformations, missingness conventions |
| Estimand | Prevalence, incidence, mean, utilization rate, conditional probability, model coefficient, risk ratio, odds ratio, hazard ratio, survival contrast, etc. |
| Analysis | Stratification, adjustment set, link function, standardization, weighting, model or estimator details |
| Estimate and uncertainty | Point estimate(s), standard error or CI, sample size, covariance where available, rounding |
| Comparability | Year/population mapping, transport assumptions, definition alignment, data-source overlap |
| Evidence role | Calibration, validation hold-out, diagnostic-only, excluded, or pending review |
| Governance | Reviewer, review timestamp, acceptance status, conflicts, and rationale |

### 6.3 Illustrative Evidence IR

The following is **synthetic example syntax**, not an extracted result from a real publication. It sketches the intended structure; no implementation is asserted.

```yaml
schema_version: "0.1"
finding_id: "demo_diabetes_prevalence_65plus"
source:
  type: "official_aggregate"
  identifier: "DEMO_ONLY"
  location: "example/table-1"
population:
  program: "original_medicare_ffs"
  years: [2021]
  age:
    minimum: 65
  enrollment:
    part_a: "continuous_observed_time"
    part_b: "continuous_observed_time"
    hmo_months: 0
cohort:
  index_date: "2021-01-01"
  observation_end: "2021-12-31"
  death_policy: "follow_until_death"
estimand:
  type: "prevalence"
  numerator:
    concept: "diabetes"
    algorithm: "registry:diabetes_v1"
  denominator: "eligible_beneficiaries"
result:
  estimate: 0.30  # fabricated demonstration value
  standard_error: 0.01  # fabricated demonstration value
role: "pending_review"
comparability:
  grade: "unassessed"
  assumptions: []
```

The compiler should reject under-specified expressions (e.g., a rate lacking a denominator or time scale) and expose missing implementation support rather than guessing. ICD/HCPCS mappings and chronic-condition algorithms should be versioned references, not informal strings.

### 6.4 Estimand compiler architecture

The evidence pipeline should translate an IR object into:

1. **Eligibility query:** determines which beneficiaries/episodes qualify.
2. **Derivation plan:** computes required conditions, exposure, outcome, and time-at-risk variables.
3. **Estimator:** computes the same reported quantity where possible, including adjustment and uncertainty semantics.
4. **Compatibility report:** indicates exactly which source fields, years, definitions, or assumptions are unsupported.
5. **Execution result:** synthetic estimate(s), diagnostics, differences from the evidence, and machine-readable provenance.

This should work independently of calibration. A research user should be able to run an evidence specification against any compatible dataset and obtain a transparent comparison.

### 6.5 Literature selection and contradictions

**MVP selection principle:** favor coherent evidence covering a bounded population and related research context, not simply a large count of publications. Original Medicare FFS and Medicare Advantage must not be silently conflated. Calendar year, continuous enrollment, death exceptions, and denominator definitions must be reconciled.

For the initial calibration set:

- Prioritize CMS official population aggregates, then carefully selected Medicare-only observational studies.
- Prefer directly reproducible estimands and clear standard errors/intervals.
- Include complementary targets (composition, disease, utilization, outcomes, conditional relationships), not repeated estimates of the same marginal.
- Screen for overlapping CMS source populations and repeated analyses of the same source study.
- Treat apparent conflicts as evidence to investigate: population mismatch, coding definition, era effects, model adjustment, sampling variability, and actual heterogeneity.
- **Do not erase inconvenient evidence.** Keep excluded/conflicting studies in the registry with reasons and retain appropriate ones for diagnostic or external evaluation.
- Prespecify training/held-out partitions before inspecting calibration outcomes.

## 7. Statistical calibration design

### 7.1 Conceptual target: plausible, valid research worlds

Let $P_0$ denote an initial synthetic data-generating distribution, and $P$ a candidate distribution over coherent beneficiary histories and connected records. Let $\mathcal{E}$ be the reviewed evidence registry, with estimand $T_s(P)$ and reported estimate $\hat\eta_s$ for study or finding $s$.

A generic design objective is:

$$
P^* = \arg\min_{P\in\mathcal{P}_{\mathrm{valid}}}
\left\{
D(P,P_0)
+ \sum_{s\in\mathcal{E}_{\mathrm{train}}}
\lambda_s L_s\!\left(T_s(P),\hat\eta_s\right)
+ \gamma R_{\mathrm{utility}}(P)
\right\}.
$$

- $\mathcal{P}_{\mathrm{valid}}$ enforces hard structural and administrative constraints.
- $D(P,P_0)$ discourages unmotivated departure from the starting world; it does **not** imply that CMS synthetic data are a valid empirical prior for real Medicare.
- $L_s$ measures evidence disagreement with uncertainty, estimand applicability, and potential dependence accounted for.
- $R_{\mathrm{utility}}$ formalizes controlled qualities useful to research (e.g., sufficient subgroup variation and nondegenerate challenges), without simply maximizing synthetic predictive accuracy.

The optimization is a conceptual objective. It should not be implemented as one monolithic algorithm unless experiments support that choice.

### 7.2 Bayesian and non-Bayesian interpretations

If a parameterized generator $P_\theta$ and a genuine parameter prior $p_0(\theta)$ are available, evidence can update the parameters through a Bayesian model:

$$
p(\theta\mid\mathcal{E}) \propto p_0(\theta)\,p(\mathcal{E}\mid\theta),
\qquad
p(D_{\mathrm{new}}\mid\mathcal{E})
=\int p(D_{\mathrm{new}}\mid\theta)p(\theta\mid\mathcal{E})\,d\theta.
$$

An initial generated data table is **not itself a Bayesian prior over $\theta$**. Early stages may instead use regularization toward that table's distribution or empirical calibration. If published summaries are represented by an approximate discrepancy loss rather than a full sampling likelihood, the result should be called generalized Bayesian calibration or regularized statistical calibration, not a uniquely identified posterior for real Medicare.

For a compatible summary vector, an illustrative discrepancy model is:

$$
\hat{\boldsymbol\eta}
\sim \mathcal{N}\!\left(
\mathbf{T}(P_\theta),\,
\Sigma_{\mathrm{sampling}}+\Omega_{\mathrm{transport}}+\Omega_{\mathrm{model}}
\right).
$$

This equation is a design sketch: off-diagonal dependence, shared cohorts, non-Gaussian estimands, selection of publications, and uncertainty in transport models must not be ignored when material.

### 7.3 Recommended calibration ladder

**Level A — No calibration.** Validate and benchmark the existing generator. Establish which relationships are merely structural and which are statistically nontrivial.

**Level B — Beneficiary-level reweighting.** Use constrained or entropy-regularized weights to reproduce selected compatible moments without modifying connected records. Monitor weight ranges, effective sample size, support failure, and hidden instability. Reweighting cannot generate combinations not present in the baseline and is not a substitute for generation.

**Level C — Parametric conditional generation.** Model disease states, utilization, outcomes, missingness, and event processes under plausible dependencies. Calibrate parameters jointly rather than repairing columns independently. Begin with a modest number of interpretable mechanisms.

**Level D — Hierarchical/uncertainty-aware calibration.** Incorporate study heterogeneity, correlated evidence, posterior predictive ensembles, and partially identified dimensions only when motivated by MVP results.

**Level E — Multi-world scenario controls.** Expose explicit variation in weakly identified dimensions while preserving declared common evidence constraints and administrative validity.

The recommendation is to **prove Levels A–C on a narrow MVP before building an elaborate hierarchical system**.

### 7.4 Guardrails for unrealistic optimization

- Published study estimates are **contextual reference targets**, not ground-truth observations of the synthetic world.
- Do not enforce exact matching when the evidence provides sampling uncertainty, rounding, model dependence, or transport uncertainty.
- Do not treat multiple papers using overlapping underlying claims populations as independent replications.
- Keep structural validity as a hard gate; make evidence agreement a measured, graded objective.
- Detect infeasible constraints and report them rather than silently weakening or replacing facts.
- Never tune the model against the final held-out evaluation studies.
- Avoid producing nearly deterministic outcomes or artificially perfect prediction tasks.
- Track the effect of each added evidence family on previously established relationships.

## 8. Agent harness: assistance without unreviewed scientific authority

### 8.1 Candidate roles

| Role | Responsibilities | Must not do autonomously |
|---|---|---|
| Discovery agent | Search candidate CMS aggregates and Medicare-only literature; generate screening records | Claim eligibility/comparability without source inspection |
| Extraction agent | Extract estimates, uncertainty, definitions, and table/page provenance | Invent missing SEs, eligibility rules, or adjusted covariates |
| Formalization agent | Propose Evidence IR and variable mappings | Approve unsupported semantics or fabricate estimators |
| Compatibility reviewer agent | Flag cohort/year/program mismatch, overlap, contradictions | Quietly discard inconsistent findings |
| Calibration operator | Execute approved configurations and reproducible experiments | Change evidence values or train/holdout partitions to improve metrics |
| Evaluation agent | Run checks, produce discrepancy and robustness reports | Decide that evidence matches without declared thresholds |
| Release agent | Assemble manifests and limitations reports | Publish unapproved claims of statistical representativeness |

### 8.2 Human review checkpoints

Require explicit approval for (i) a new evidence record, (ii) a new estimand implementation, (iii) changed cohort definitions or transport assumptions, (iv) revised calibration targets, (v) changes to held-out partitions, and (vi) a public evidence-calibrated release. Agent outputs should include source excerpts or anchors, proposed mappings, uncertainty assessments, and machine-readable diffs.

### 8.3 Reproducible harness contracts

Each run should include pinned source/evidence versions, code revision, generator version, world configuration, seed(s), approved evidence-set hash, calibration method and hyperparameters, data product targets, diagnostics, and output checksums. Tool calls, human approvals, rejected hypotheses, and failed runs should be inspectable without putting volatile agent conversations into the statistical source of truth.

The numerical and validation engines must remain fully operable **without** the agent harness. This prevents agent nondeterminism from contaminating statistical reproducibility.

## 9. MVP: recommended population and research context

### 9.1 Initial scope

**Recommended target:** a bounded **2021 Original Medicare FFS** research context, initially focusing on a **65+** beneficiary population with explicitly defined Parts A/B enrollment and managed-care exclusions or adjustments. The precise cohort should be finalized after inspecting available source variables and compatible evidence.

**Recommended initial domain:** chronic disease and hospitalization, with diabetes and/or heart failure as example condition families. These conditions offer tractable links among demographics, chronic conditions, utilization, and costs. Specific claims-based algorithms and outcome definitions must be pinned, not inferred from general labels.

**Candidate quantities:** age/sex composition, selected condition prevalences, condition co-occurrence, annual hospitalization probabilities or rates, utilization counts, spending distribution summaries, and a small number of adjusted/stratified relationships. Mortality or readmission can be included only if the required follow-up and event semantics are adequately supported.

**Suggested corpus for scoping, not an immutable target:** roughly 10–20 compatible calibration findings spanning several distinct statistical relationships, plus 5–10 held-out or diagnostic-only findings. Counts are illustrative; target quality, independence, and coverage matter more than quantity.

### 9.2 MVP researcher journey

1. Select `original_medicare_ffs_2021/chronic_hospitalization_v1`.
2. Inspect dataset scope, source years, supported fields, known omissions, and evidence coverage.
3. Generate a reproducible cohort and linked claims data with a chosen scale and seed.
4. Define or run a research example: cohort selection, lookback, condition ascertainment, hospitalization outcome, prediction or survival method.
5. Run the same pipeline across alternative plausible worlds or perturbation scenarios.
6. Receive structural and contextual diagnostic reports, including which published findings were used for calibration and which remained held out.
7. Export data, schema, executable workflow examples, IR specifications, manifests, and limitations for local development.
8. Later, adapt and validate the analysis against restricted Medicare data when appropriately authorized.

### 9.3 MVP boundaries

- No complete replication of claim-line content or real patient trajectories.
- No requirement to implement every listed canonical table for the first calibrated domain.
- No demand to reproduce every publication; incompatible or inexpressible evidence is reported as such.
- No claim that synthetic causal estimates or prediction performance transport to real data.
- No requirement for expensive neural generative architectures if a transparent model suffices.

## 10. Roadmap and acceptance gates

The ordering below preserves the original proposed sequence while moving lightweight evidence scouting earlier and distinguishing the literature corpus from the calibration engine. Phases 2 and 3 may proceed in parallel; later evidence additions are iterative rather than one-shot.

### Phase 0 — Feasibility and evidence scouting

**Objective:** Ensure that a coherent, useful first research context and sufficient implementable evidence exist before hardening the IR and calibration design.

**Work:**

- Review current generator, supported tables, and validation/test coverage.
- Select candidate 2021 Original Medicare FFS research context and enumerate necessary fields.
- Identify official CMS aggregate data sources and a small sample of Medicare-only research findings.
- Test whether cohort definitions, outcome definitions, and uncertainty are reported clearly enough for programmatic reproduction.
- Identify potentially conflicting programs/years and reused source populations.

**Deliverables:** Feasibility memo, candidate MVP specification, initial evidence inventory, capability-gap list.

**Exit gate:** At least one meaningful population/condition/utilization analysis can be expressed using available or reasonably implementable data fields; no known fatal comparability issue is ignored.

### Phase 1 — Establish and verify the synthesizer

**Objective:** Demonstrate that Medicare-Synth can generate new, nontrivial and coherent synthetic worlds—not just structurally valid fixtures.

**Work:**

- Audit the existing vertical and horizontal expansion paths, including whether variation is genuinely generated versus duplicated.
- Introduce or validate an independently testable conditional synthesis interface.
- Establish beneficiary/event-level generation and dependent record compilation where needed.
- Design controlled simulation distributions with known ground truth and measured conditional relationships.
- Exercise schema, keys, chronology, enrollment, claims accounting, reproducibility, diversity, and scalability.

**Deliverables:** Synthesizer contract, baseline benchmark suite, generator capability report, reference synthetic worlds, known limitations.

**Exit gate:** Repeated runs with pinned inputs/seeds reproduce outputs; structural checks pass; held-out synthetic ground-truth relationships can be recovered to predeclared tolerances; generated datasets exhibit genuine statistical support and useful variation.

### Phase 2 — Evidence IR and executable study language

**Objective:** Convert heterogeneous study findings into validated, inspectable, executable estimands.

**Work:**

- Define canonical variable vocabulary, program/year/population semantics, time windows, cohort and estimator grammar.
- Implement a typed schema and static validation; support an initial handful of estimand types.
- Build IR-to-execution compilation and compatibility checks.
- Prototype AI-assisted extraction/formalization with source anchors and reviewer workflows.
- Include complete errors for unsupported fields, absent algorithms, or unexpressed uncertainty.

**Deliverables:** Evidence IR specification and versioning policy, parser/validator/compiler, sample fixtures, documentation, source-to-estimand tests.

**Exit gate:** A human-reviewed real Medicare-only finding can be formalized, executed against a compatible synthetic dataset, and compared with its published estimate in a reproducible report; errors are explicit.

### Phase 3 — Curate and freeze the MVP evidence corpus

**Objective:** Assemble a varied, compatible and provenance-rich set of evidence to drive and independently evaluate calibration.

**Work:**

- Screen eligible CMS aggregate sources and published Medicare-only studies.
- Grade comparability, estimand executability, uncertainty quality, temporal relevance, and probable cohort overlap.
- Resolve or classify conflicting findings; document exclusions rather than deleting them.
- Partition evidence into training, held-out evaluation, and diagnostic-only groups.
- Freeze the initial selection before calibration and define maintenance/versioning rules.

**Deliverables:** Versioned evidence registry, eligibility/compatibility reports, held-out list, review audit trail, evidence-set checksums.

**Exit gate:** All active findings are formally executable or transparently mapped to defensible approximations; training and held-out partitions are fixed and reviewer-approved.

### Phase 4 — Build calibration engine and agent harness

**Objective:** Integrate deterministic statistical calibration with reviewable AI-assisted evidence operations.

**Work:**

- Implement baseline reweighting with feasibility, support, weight, and effective sample size diagnostics.
- Define the generator-parameter calibration interface and an initial joint conditional model.
- Introduce uncertainty and study-overlap handling appropriate to the MVP corpus.
- Implement calibration-only runs in synthetic known-truth experiments before connecting to literature.
- Build agent orchestration for extraction, review, run planning, execution, diagnostics, and reproducible releases.

**Deliverables:** Calibration engine/API, agent role contracts, review gates, synthetic truth simulations, deterministic run manifests, failure diagnostics.

**Exit gate:** In controlled simulations, the engine improves predeclared targets without invalidating records; dependence/uncertainty assumptions are visible; the pipeline runs independently of agents.

### Phase 5 — Complete the MVP calibration

**Objective:** Produce a small family of literature-compatible Medicare research worlds for the selected context.

**Work:**

- Run pre-specified calibration against approved training evidence only.
- Compare no-calibration, beneficiary-reweighting, and conditional-generator approaches.
- Examine infeasible constraints, weight collapse, overconcentration, or degenerate features.
- Produce a reference world and a few controlled alternative worlds.
- Export linked data, evidence agreements, model configurations, provenance, and known deviations.

**Deliverables:** Versioned MVP worlds, training evidence fit reports, discrepancy report, release manifests, limitations profiles, reproducible examples.

**Exit gate:** The chosen release meets all hard structural gates, avoids known degenerate statistical behavior, demonstrates meaningful improvement on predeclared contextual metrics, and transparently describes what remains underdetermined.

### Phase 6 — Evaluate and refine against independent criteria

**Objective:** Determine whether the calibrated playground meaningfully improves research preparation and generalizes beyond fitted evidence.

**Work:**

- Run held-out study comparisons without using them for calibration tuning.
- Evaluate support, heterogeneity, longitudinal behavior, and uncertainty across worlds.
- Conduct synthetic known-truth tests to measure recovery of uncalibrated relationships and robustness to misspecification.
- Test representative research workflows: cohort construction, prediction, survival analysis, diagnostics, and sensitivity analysis.
- Where authorized, pilot code portability against restricted Medicare infrastructure without treating synthetic results as empirical substitutes.
- Record failures and refine the model using a separate development benchmark; preserve a truly untouched final evaluation set or introduce new external evidence after a revision cycle.

**Deliverables:** Evaluation protocol, benchmark suite, held-out evaluation report, issue backlog, updated model card and release decision.

**Exit gate:** Predefined quality thresholds are met, or limitations are documented and a no-go decision is issued. No indefinite “improve until it looks good” loop against the same hold-out set.

### Phase 7 — Expand literature coverage and research contexts

**Objective:** Grow the evidence registry and supported playground contexts without compromising auditability or prior utility.

**Work:**

- Introduce new estimand types, disease domains, utilization contexts, time periods, and data-product boundaries incrementally.
- Group evidence into compatible research contexts rather than forcing incompatible studies into one universal distribution.
- Establish regression testing of earlier worlds, including evidence-consistency and workflow-utility checks.
- Manage schema-year evolution, study retractions or corrections, and changes in official aggregate sources.
- Enable user-defined context presets and explicit cross-world sensitivity analysis.

**Deliverables:** Modular context catalog, reusable evidence registry, compatibility graph, extended benchmarks, versioned calibration profiles.

**Exit gate:** New context(s) show independent value and pass the same structural, contextual, and research-utility gates; prior releases remain reproducible.

## 11. Evaluation framework and proposed quality gates

A single “fidelity score” would conceal important trade-offs. Evaluation should preserve separate dimensions and clearly distinguish **hard gates**, **graded metrics**, and **scenario-specific aims**.

| Dimension | Example measures | Evaluation role |
|---|---|---|
| Structural correctness | PK/FK validity, code constraints, enrollment compatibility, date order, accounting constraints | Hard release gate |
| Generator validity | Synthetic ground-truth moment/association recovery; support diversity; duplicate/clone diagnostics; deterministic seeds | Phase 1/4 gate |
| In-sample evidence agreement | Standardized residuals, uncertainty-aware coverage, discrepancy by estimand family | Training diagnostic, not decisive evidence of generalization |
| Held-out agreement | Compatible study coverage, prespecified standardized error, interval inclusion and discrepancies | Primary external plausibility benchmark |
| Robustness | Stability across seeds, perturbation scenarios, evidence leave-one-family-out analyses | Required for strong quality claims |
| Statistical nondegeneracy | Effective sample size, propensity support, outcome prevalence, separation, rare-subgroup counts, trivial predictability checks | Guardrail |
| Longitudinal coherence | Event ordering, utilization trajectories, enrollment risk sets, follow-up/censoring behaviors | Context-specific validity |
| Research utility | Ability to execute end-to-end study workflows, detect intentionally inserted failures, complete tasks with documented effort | Core product benchmark |
| Transparency | Reconstructible inputs, model/evidence hashes, decisions, run manifests, known deviations | Hard release gate |

### 11.1 Suggested experimental comparisons

Always compare at least:

- **B0:** existing structurally valid but uncalibrated baseline;
- **B1:** entropy/constrained beneficiary-level reweighting;
- **B2:** conditional generator with jointly calibrated parameters;
- **B3 (optional):** posterior predictive or scenario-ensemble generator.

Compare on the same defined research context and frozen evidence partition. Do not reward a method for changing the task, denominator, or target population.

### 11.2 What improvement means—and what it does not

For the MVP, a successful improvement means reduced discrepancy on selected, compatible empirical summaries; improved behavior on distinct held-out summaries when supported; increased ability to exercise meaningful analytic workflows; and preserved structural validity. It **does not** mean the simulated risk model, effect estimate, or expenditure estimate has become a trustworthy real-Medicare result.

### 11.3 Prespecification and guardrails

Before each consequential calibration experiment, register:

1. Target research context and supported variables.
2. Evidence IDs and calibration/held-out roles.
3. Calibration objective and uncertainty assumptions.
4. Hard constraint set and expected failure behavior.
5. Diagnostic metrics and acceptable limits.
6. Research-workflow test cases.
7. Stopping rule, model selection criterion, and no-go criteria.

Thresholds should be established empirically during Phase 0/1 pilots, then frozen ahead of the Phase 5/6 evaluation. Avoid fictitious universal numerical standards.

## 12. Proposed software interfaces and repository organization

The following structure is an **architectural sketch**, not a mandatory refactor. Prefer adding narrow modules consistent with current conventions rather than introducing a large new framework prematurely.

```text
src/medicare_synth/
  # Existing domain, validation, scenario, release modules retained.
  evidence/
    models.py             # typed Evidence IR and provenance
    vocabulary.py         # canonical concepts, estimands, variables
    compiler.py           # cohort/measure/analysis execution plans
    compatibility.py      # population, year, and algorithm coverage
    registry.py           # evidence indexing and immutable versions
  synthesis/
    protocol.py           # parameterized generator interface
    context.py            # coherent beneficiary-world construction
  calibration/
    objectives.py         # evidence residuals, uncertainty, penalties
    reweight.py           # baseline beneficiary-level calibration
    fit.py                # generator-parameter calibration
    diagnostics.py        # feasibility and support evaluation
  evaluation/
    evidence_fit.py       # training and held-out comparison
    synthetic_truth.py    # known-truth simulation experiments
    workflow_utility.py   # research pipeline benchmarks
  worlds/
    config.py             # scenario presets and world metadata

# Candidate supporting directories:
evidence_registry/        # reviewed literature metadata and IR
configs/worlds/           # versioned contexts and assumptions
benchmarks/               # controlled simulations and study workflows
reports/                  # calibration/evaluation summaries
```

### Minimal public APIs (illustrative)

```python
spec = evidence_registry.load("finding_id")
plan = evidence_compiler.compile(spec, schema=target_schema)
result = plan.evaluate(synthetic_tables)

world = synthesizer.generate(context="ffs_2021_chronic_v1", seed=42)
calibrated = calibration_engine.fit(world, evidence_set="mvp_train_v1")
report = evaluator.evaluate(calibrated, evidence_set="mvp_holdout_v1")
```

The API should make it difficult to accidentally fit on held-out evidence or silently change source population assumptions. The functions above are conceptual examples, **not present repository APIs**.

### Proposed release artifacts

A calibrated world release should include:

- CSV/Parquet linked synthetic tables and schema/year identifiers.
- Generator manifest, parameters, random seeds, and hashes.
- Training evidence-set IDs, versions, licenses/links, and IR snapshots.
- Held-out evidence-set identifiers and isolation policy (without revealing hold-out results during fitting).
- Calibration objective/method/configuration and diagnostics.
- Structural, contextual, diversity, and research-utility reports.
- World/scenario assumptions and which constraints were relaxed.
- Explicit non-goals, known unknowns, and intended-use labels.
- Executable example workflows and transfer caveats.

## 13. Open-science, governance, and responsible use

### 13.1 Data governance

Use publicly available CMS synthetic material and public aggregate evidence according to their terms. Keep raw baseline acquisition and checksummed manifests separate from generated releases. If the project ever introduces nonpublic Medicare data for a separate validation study, that data must remain in an authorized environment and must not be treated as distributable training material or exported through the public pipeline.

Published aggregate tables generally avoid individual-level disclosure but do not by themselves establish a formal privacy guarantee for a data-generation workflow. Ensure that source provenance and re-identification/privacy review match the actual release inputs.

### 13.2 Literature governance

Maintain source IDs, versions, correction/retraction status, study population provenance, evidence grading, and licenses. Store only lawful excerpts or derived facts as needed; prefer citations/links and structured estimates rather than wholesale republication of papers.

### 13.3 Claim control

Each release should prominently disclose:

> These are synthetic Medicare-like records for research development and stress testing. Literature constraints provide contextual plausibility for selected quantities, not a guarantee of real Medicare representativeness. Estimates and model performance from these records must not be interpreted as real Medicare findings.

Avoid labels such as “realistic enough for causal inference” or “validated against Medicare” unless a separate study demonstrates exactly what was validated and under which conditions.

## 14. Risks and mitigation plan

| Risk | Why it matters | Mitigation |
|---|---|---|
| Incomplete identifiability | Many distributions satisfy the same summaries | Multiple worlds, explicit assumptions, synthetic truth experiments, no representativeness claims |
| Mis-specified estimands | Similar reported numbers can measure different constructs | Typed IR, denominators/time scales, executable algorithms, human review |
| Source-population mismatch | FFS/MA, age, enrollment, geography, and years may differ | Compatibility grading, context-specific evidence groups, transport uncertainty |
| Literature publication and selection bias | Published findings are a selective view of real analysis results | Official aggregates first; full candidate registry; sensitivity to evidence selection |
| Dependence of findings | Multiple papers can reuse the same underlying CMS population | Shared-source metadata, clustered/correlated uncertainty, discount redundant evidence |
| Infeasible constraints | Starting generator may lack required combinations or support | Weight/ESS diagnostics; conditional generation; explicit infeasibility reports |
| Overfitting held-out studies | Repeated evaluation and tweaking leak hold-out evidence | Frozen test sets, development sets, prospective/new evidence evaluation |
| Cross-table corruption | Local adjustments can break enrollment and claims relationships | Beneficiary-level calibration and coherent generation; post-fit hard validation |
| Unrealistic research difficulty | Perfect outcome signals or trivial missingness produce misleading tests | Nondegeneracy benchmarks and adjustable stress-world scenarios |
| Agent hallucination and drift | Automated literature extraction can invent semantics | Source anchors, validation failures, review gates, immutable evidence versions |
| Scope explosion | Every estimand and CMS file family can become a new project | One focused 2021 FFS MVP, explicit non-goals, gate-driven expansion |
| Misinterpretation by downstream users | Synthetic estimates may be presented as empirical Medicare results | Prominent labeling, limitations profile, user-facing warnings, examples of appropriate uses |

## 15. Project organization and decision policy

A lightweight project governance model is recommended:

- **Scientific owner:** determines intended research contexts, estimand semantics, evidence eligibility, and quality gates.
- **Statistical methods owner:** reviews calibration assumptions, identifiability, uncertainty, and simulation evaluation.
- **Domain/data owner:** verifies Medicare data products, enrollment logic, code/variable definitions, and administrative validity.
- **Engineering owner:** maintains reproducible implementation, CI, typed interfaces, manifests, and performance.
- **Agent review process:** proposes evidence/experiments but requires explicit sign-off for scientific changes.

One person may cover multiple roles initially. The aim is separation of responsibilities, not process-heavy bureaucracy.

**Versioning policy:** separately version the generator, Evidence IR schema, evidence corpus, study algorithm library, world configuration, and release artifact. A new paper or new schema year must not silently mutate an old published world.

## 16. Scientific contribution and dissemination opportunities

The primary near-term product is an open-source *research-enabling system*, not a synthetic reconstruction of the national Medicare population. A potential research contribution emerges if the project demonstrates that heterogeneous external summary evidence improves a generative playground's ability to reproduce **held-out, compatible contextual relationships** while preserving relational constraints and exposing uncertainty.

Potential publishable questions include:

1. **Evidence representation:** an executable, citation-backed formal language for published administrative-claims estimands.
2. **Statistical calibration:** principled integration of partially overlapping and heterogeneous summary evidence into coherent relational synthetic-world generation.
3. **Evaluation:** benchmarks for contextual realism and research utility that do not equate distributional similarity with real-world inferential validity.
4. **Multi-world stress testing:** whether explicitly varying underidentified assumptions improves detection of failure modes in healthcare research workflows.

Novelty is not established merely by using literature-based targets. Prior work exists on entropy balancing and integration of external summary models; the more distinctive contribution would be the *operational combination* of those ideas with formal estimands, connected Medicare-like data, reviewable provenance, and measured researcher utility. Research claims should be tested against that prior art.

Likely outputs: a software/system description, a benchmark/evaluation report, reusable evidence-IR examples, and—conditional on methodological results—a statistical-methods paper.

## 17. Near-term execution plan: first vertical slice

Before parallelizing all eight phases, conduct a small proof of concept with the following bounded steps:

1. **Select one study context:** 2021 Original Medicare FFS, age 65+, explicit enrollment and follow-up rules, one or two chronic conditions, and hospitalization-related outcomes.
2. **Audit a minimal data dependency graph:** beneficiary, enrollment, relevant chronic-condition fields, and just the claim families needed for the example. Identify the fields genuinely present and those requiring modeled generation.
3. **Prepare three verified public targets:** one population composition measure, one condition prevalence measure, and one utilization conditional estimate; then identify one genuinely independent diagnostic/hold-out finding. The number is intentionally small.
4. **Formalize one finding end-to-end:** source → Evidence IR → validated cohort/estimand execution → comparison report.
5. **Prove generator controllability:** on synthetic ground truth, recover an intentionally specified conditional association while retaining valid linked records.
6. **Implement reweighting before advanced Bayesian calibration:** measure support, ESS, and target agreement; document where it cannot work.
7. **Produce two or three explicitly different worlds:** same supported targets, different weakly identified assumptions; run an identical analysis in each.
8. **Freeze a first evaluation protocol:** choose quality gates and an untouched held-out set before substantive iterative fitting.

**First major milestone:** A real, human-reviewed external estimate can be executed as a reproducible test against generated Medicare-like data.  
**Second major milestone:** A calibrated generator improves held-out contextual plausibility and research-task utility, compared with the uncalibrated baseline, without losing administrative integrity.

## 18. Open decisions for project planning

The following should remain explicit decisions rather than being silently resolved by coding agents:

- Which 2021 Medicare population definition is the exact MVP target, including mortality and partial-year enrollment handling?
- Which minimal table families and chronic-condition algorithms are sufficiently supported today?
- Which outcome family best balances scientific interest and implementability: hospitalization, readmission, medication utilization, or spending?
- How much Evidence IR expressiveness should be in v0.1 (prevalence/rates only versus selected regression coefficients)?
- Which evidence should be considered authoritative, and under what rules should older-year studies be transported?
- How should provenance and statistical assumptions be displayed to researchers exploring worlds?
- What user-study or workflow benchmark will demonstrate real practical value beyond calibration metrics?
- Which advanced Bayesian/hierarchical capabilities are truly justified by the MVP diagnostics?

## 19. Proposed success definition

The project succeeds when an investigator can **quickly and safely develop a realistic Medicare research workflow** on a public, reproducible, contextually plausible dataset, understand exactly which aspects of that world are supported by external evidence and which remain assumptions, exercise the method across meaningful variations, and carry the resulting *code and research design*—not the synthetic empirical conclusions—into an authorized real-data analysis.

> **Final principle:** Build a credible playground for Medicare research, not a replica of Medicare. Use published findings to improve context and expose uncertainty, not to claim recovery of individual-level or population-level truth.

## References and source materials

**Project source of truth**

1. Medicare-Synth repository: <https://github.com/SaehwanPark/medicare-synth>.
2. Medicare-Synth current architecture: <https://github.com/SaehwanPark/medicare-synth/blob/main/ARCHITECTURE.md>.
3. Medicare-Synth current roadmap: <https://github.com/SaehwanPark/medicare-synth/blob/main/ROADMAP.md>.
4. Medicare-Synth expansion implementation: <https://github.com/SaehwanPark/medicare-synth/blob/main/src/medicare_synth/expansion.py>.
5. Medicare-Synth limitations: <https://github.com/SaehwanPark/medicare-synth/blob/main/docs/reference/limitations.md>.

**Public administrative data and precedent**

6. Centers for Medicare & Medicaid Services. *Medicare Claims Synthetic Public Use Files (SynPUFs).* <https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files>.
7. Centers for Medicare & Medicaid Services. *Medicare Geographic Variation—by National, State & County.* <https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-geographic-comparisons/medicare-geographic-variation-by-national-state-county>.
8. Centers for Medicare & Medicaid Services. *Medicare Data for the Original Medicare Geographic Variation Public Use File: A Methodological Overview* (May 2026 update). <https://data.cms.gov/sites/default/files/2026-05/Original%20Medicare%20Geographic%20Variation%20Public%20Use%20File%20Methods%20Paper.pdf>.

**Methodological context**

9. Hainmueller J. Entropy balancing for causal effects: A multivariate reweighting method to produce balanced samples in observational studies. *Political Analysis.* 2012;20(1):25–46. <https://doi.org/10.1093/pan/mpr025>.
10. Gu T, Taylor JMG, Mukherjee B. A synthetic data integration framework to leverage external summary-level information from heterogeneous populations. *Biometrics.* 2023;79(4):3831–3845. <https://doi.org/10.1111/biom.13852>.

*The references motivate design choices and provide potential evidence sources; none constitute an already-curated, approved calibration corpus. Literature eligibility and numerical estimates must be reviewed in the proposed evidence-registry workflow.*
