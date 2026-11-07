# Medicare-Synth Documentation Reorganization Plan

**Status:** Implemented on `docs/researcher-first-reorganization` (plan PR1–PR4; PR5 deferred)
**Repository:** <https://github.com/SaehwanPark/medicare-synth>  
**Audit basis:** `main` at `1b91988510c39a4f1942bdb4af9496eef47cc48c` (reviewed November 7, 2026)  
**Primary audiences:** Medicare investigators, clinical researchers, health services researchers, biostatisticians, research programmers, and project contributors  
**Primary decision:** `README.md` and the GitHub Pages homepage are **researcher-first**. Technical documentation is easy to find, but secondary.

## 1. Executive recommendation

Separate **who the product serves and what they can do today** from **how its implementation works**. Reorganize documentation into:

1. **Root README (`README.md`)** — public orientation in plain English, a concise capability/limitation summary, one representative research use case, and clear pathways into the docs site.
2. **GitHub Pages** — one site with two explicit, distinct navigational tracks: **For Researchers** (default) and **For Developers**. Researcher pages prioritize tasks, usable artifacts, example analyses, and interpretation boundaries; developer pages prioritize installation, commands, schema/contracts, testing, and extension.
3. **Canonical technical/project records** — root `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `AGENTS.md`, `CHANGELOG.md`, `LESSONS.md`; `docs/goal.md`, phase-specific reports/fixtures, proposals, and harness instructions. Preserve technical precision and histories. These source files need not be rewritten in lay terminology or promoted to the researcher sidebar.

**Outcome sought:** A researcher who has never written Python should, within minutes, understand why Medicare-Synth exists, the concrete 2021 diabetes–hospitalization use case, which tasks are possible without/with technical help, what is not implemented, and why synthetic outcomes are not Medicare population estimates.

This reorganization must not silently promise a hosted generator, one-click research-ready CSV, generalized disease calibration, realistic longitudinal patterns, or automatic paper-to-dataset creation. Where a desired user flow is not supported by current code, label it *planned* or open a separate development issue.

## 2. Evidence-based inventory: current state

### Public entry points

- `README.md` currently begins with an installation/validation quickstart, CLI and Python examples, technical library names, and phase IDs. These are relevant but not the first questions of a clinical/health-services investigator.
- `docs/index.md` currently leads with fixtures, pipelines, source manifests, and an install-and-validate exercise. It includes cards for installation, CLI, releases, and provenance; this is a developer-oriented information hierarchy.
- `docs/_layouts/default.html` exposes sidebar categories `Getting Started`, `Use the project`, `Understand the data`, and `Contribute & reference`, without a researcher/developer split.
- `docs/_config.yml` contains the GitHub Pages Jekyll configuration and excludes `phase0` and `phase1`, but not all later phase-report folders. This creates inconsistent handling of source-only records.
- `scripts/check_documentation_site.py` checks a hard-coded set of current pages and recurses only through `getting-started`, `guides`, `concepts`, and `reference`; it will not automatically protect newly introduced researcher/developer sections.

### Demonstrated capabilities that public documentation may claim

- A structural toolkit with 19 modeled domain tables, validation, 21 named deterministic fixtures (3 valid, 18 intentionally invalid), and CSV/Parquet export for the documented fixture/release paths.
- A bounded 2022 PUF beneficiary/carrier importer; not universal support for all Medicare years and file families.
- A specific conditional synthesizer for 2021 Original Medicare FFS-like beneficiaries aged 65+ with diabetes, heart failure, and all-cause inpatient admission (not diagnosis-specific admission).
- Evidence representation, frozen calibration/holdout evidence partitions, calibration through reweighting and generator parameter search, and three Phase 5 example worlds using the same selected public targets.
- Phase 5 calibration diagnostics report success against the chosen calibration moments; Phase 6 independent research-utility and held-out evaluation remains active. Passing a calibration gate is not the same as general clinical realism or population representativeness.

### Important constraints that must remain visible

- The Phase 5 prototype matches **selected** moments: diabetes prevalence 27.7% (2018 source), heart failure prevalence 12% (2022 source), and approximately 13% inpatient risk among people with diabetes (weaker industry source, different time framing); these are not a comprehensive, clean 2021 Medicare benchmark.
- The current generator treats diabetes and HF independently, draws a limited number of binary features, and does not model realistic multiyear disease trajectories, repeated admissions, provider effects, causal mechanisms, or robust clinical comorbidity dependence. At most one inpatient claim per hospitalized simulated beneficiary in the MVP generator; no inpatient principal diagnosis for diagnosis-specific analyses.
- The optional literature finding drafting helper is not an automatic, authoritative literature ingestion service. Human review and approvals remain gates.
- The general scenario exporter and the Phase 5 world-emission script are separate workflows: the latter primarily writes reports/manifests, not an already documented nontechnical, one-click calibrated CSV product.
- Synthetic cohorts, even if matching selected public statistics, cannot yield defensible real-Medicare prevalence/effect estimates, validation performance, clinical or policy conclusions, or population-representative findings.
- No restricted Medicare claims are bundled or needed for the built-in fixture demonstrations; code is Apache-2.0, while acquisition/use/distribution terms for upstream CMS synthetic data must be checked separately.

## 3. Documentation principles and editorial contract

**Researcher-first, not researcher-only.** The README and homepage should answer, in this order: Why should I care? What can I do now? What can I not do? Can I see an example? What is the appropriate interpretation? How do I begin? Where are technical details?

**Use demonstrated verbs.** Prefer “generate a 2021 FFS-like diabetes–hospitalization cohort using a Python API” to “generate Medicare data for any research question.” Distinguish **available**, **limited/experimental**, **planned**, and **not intended**. “Implemented” is not equivalent to “evaluated for research use.”

**Separate four forms of validity.** (1) structurally plausible tables and links, (2) closeness to selected published summary statistics, (3) realism for a stated analysis workflow, and (4) legitimate population-level inference. The first two have a bounded basis; the third needs Phase 6 evaluation; the fourth is not a project claim.

**Give a practical default path.** A researcher should not need to know what Pydantic, IR, IPF, ESS, provenance statuses, or table grain mean to learn whether the tool is useful. Include brief definitions and link technical detail, rather than removing precision from technical pages.

**Source-aware, current, and explicit.** For each capabilities statement, identify an implementation/test/report anchor, intended audience, limitations, and review owner. Keep old proposals labeled historical; do not elevate planned functionality to a current claim.

**Avoid duplication.** Treat code, tests, and canonical state records as implementation truth; researcher pages are curated summaries, not parallel specifications. A documented release state must point at the relevant validation/evaluation report.

## 4. Proposed information architecture

The root README stays at the root. `docs/` remains the Jekyll source. Paths below are proposed; exact display names can be refined during editing.

```text
README.md                                   # Public/researcher-first landing page
SPEC.md                                     # Canonical technical state — stays
ARCHITECTURE.md                             # Canonical architecture — stays
ROADMAP.md                                  # Canonical milestone plan — stays
AGENTS.md                                   # Contributor/agent policy — stays
CHANGELOG.md, LESSONS.md                    # History and technical lessons — stay

docs/
  index.md                                  # Researcher-first GitHub Pages homepage
  researchers/
    index.md                                # Researcher hub / choose your task
    what-you-can-do.md                     # Honest capability matrix, by use case
    diabetes-hospitalization-example.md   # End-to-end narrative of actual MVP
    getting-started.md                     # Zero-jargon access paths and prerequisites
    understanding-the-data.md             # What tables/records mean to an analyst
    interpreting-results.md               # Statistical realism, uncertainty, interpretation
    limitations.md                         # Plain-language limits and responsible use
    faq.md                                 # Researcher FAQ / terminology
  developers/
    index.md                                # Technical entry and architecture overview
    installation.md                        # Migrate original installation guide
    first-run.md                           # Migrate original validation walkthrough
    cli.md                                 # Migrate original CLI reference
    scenarios-and-validation.md            # Migrate original scenarios guide
    export-and-release.md                  # Migrate original export guide
    data-model.md                          # Migrate technical data model guide
    provenance-and-validation.md           # Migrate technical provenance guide
    calibrated-worlds.md                   # NEW accurate Phase 5 Python use case
    contributing.md                        # Migrate original contributor guide
    project-documents.md                   # Canonical source map, all phases
    documentation-maintenance.md           # NEW editorial and consistency contract
  _layouts/default.html                    # Researcher / Developer navigation
  _config.yml                               # Publication inclusion/exclusion rules
  assets/css/style.css                      # Accessibility and typography updates
  assets/js/site.js                         # Active nav behavior; keep JS minimal
  ... existing phase*/goal.md/harness/...    # Source-only engineering records

scripts/check_documentation_site.py          # Updated link and required-page checks
.github/workflows/pages.yml                 # Build/verify/deploy site
```

### Site navigation hierarchy

Top navigation: **Overview | For Researchers | For Developers | GitHub**. Default/home is the Overview oriented toward researchers. Primary sidebar under Researchers: *What you can do → Worked example → Getting started → Understanding the data → Interpreting results → Limits & FAQ*. Developers: *Start developing → Install & run → CLI and scenarios → Data model → Calibration worlds → Exports → Contribute → Technical reference*.

Do not build two separate websites or introduce a new publishing stack. Reuse the existing Jekyll site, CSS shell, and standard GitHub Pages deploy workflow. Consider persistent cross-track links in the page template, but keep the researcher journey dominant on the homepage.

### Protect old URLs

Existing URLs are public, so migration should **not** strand users. Maintain small human-readable forwarding pages or reliable Jekyll-compatible redirects at legacy paths; test the rendered destinations. Avoid adding an unsupported redirect plugin as a prerequisite.

| Existing path | Proposed destination |
| --- | --- |
| `/getting-started/installation/` | `/developers/installation/` |
| `/getting-started/first-run/` | `/developers/first-run/` |
| `/guides/cli/` | `/developers/cli/` |
| `/guides/scenarios-and-validation/` | `/developers/scenarios-and-validation/` |
| `/guides/release-workflow/` | `/developers/export-and-release/` |
| `/concepts/data-model/` | `/developers/data-model/` |
| `/concepts/provenance-and-validation/` | `/developers/provenance-and-validation/` |
| `/reference/limitations/` | `/researchers/limitations/` |
| `/reference/project-documents/` | `/developers/project-documents/` |
| `/contributing/` | `/developers/contributing/` |

Redirect/forwarder content should clearly state “This guide has moved” with a functional destination link, even if automatic redirection is also offered. Maintain 404 guidance to both audience hubs.

## 5. README.md: target structure and writing requirements

**Target length:** approximately 450–700 words before link reference details. No installation code block in the first screenful; at most one short technical quickstart snippet placed after the researcher-oriented content, or link directly to the developer quickstart instead.

Recommended order:

1. **Title + one-sentence value proposition.** “Explore and test Medicare research ideas with synthetic data before working with restricted Medicare files.” Qualify that this is a research sandbox, not an inferential substitute.
2. **Why this exists.** Restricted CMS work has time, access, workflow, and cost constraints. Describe how early prototyping helps.
3. **What you can do today.** Researcher-use cases in everyday language, segmented as (a) structural exercises, (b) specific evidence-calibrated MVP, and (c) code/analysis workflow tests.
4. **One concrete example.** 2021 Original Medicare FFS-like adults aged 65+; diabetes, heart failure, and any inpatient admission. Explain three selected calibration targets are illustrative/approximate; synthetic results are not Medicare claims.
5. **Current limits.** No universal condition/year support, no full clinical/temporal realism, no claim that statistical outcomes generalize, no one-click browser-based generator, and no complete independent Phase 6 evaluation. The limits should be visible without scrolling through extensive code.
6. **How to get started.** Two clear routes: “Explore as a researcher” and “Install/use as a developer.” Describe that researcher-friendly public download workflows may still require a technical collaborator; do not invent a ready-made release asset.
7. **Responsible-use notice.** Do not cite generated estimates or model performance as empirical Medicare findings; call out assumptions and remaining evaluation.
8. **Links.** GitHub Pages, technical reference, contribution instructions, license/source terms, current development status.

Suggested opening copy (editorial example, not a verified release promise):

> Medicare-Synth helps researchers explore ideas using artificial, Medicare-like datasets before they work with restricted Medicare data. It supports realistic-looking data structures and, for one limited study setting, synthetic populations adjusted toward selected published statistics. It is designed for research preparation and methods testing—not for estimating what is true of Medicare beneficiaries.

Avoid putting “Pydantic,” “Polars,” “Evidence IR,” “validation fixture,” “synthetic known-truth,” or 19/21 counts in the lead paragraph. Exact counts may remain in developer reference if maintained and clearly distinguished from fully calibrated research domains.

## 6. Researcher-facing pages: content specifications

### `researchers/index.md` — choose your goal

Lead with three recognizable tasks: **Explore available data**, **Plan an analysis**, and **Compare assumptions**. Each should link to a supported example or a transparent “not yet supported” explanation. No generic promise that users can generate any cohort.

### `researchers/what-you-can-do.md` — current capabilities

Build a stable task-oriented matrix with columns: *Research task*, *What works today*, *Technical assistance needed*, *Current limitations*, *Verification reference*. Suggested rows:

- Study Medicare-like file structure, keys, and joins — available via fixture workflows.
- Run basic code and cohort-definition exercises — available with setup.
- Export ordinary fixture-based CSV/Parquet bundles — available through developer tooling.
- Generate a 2021 FFS diabetes–any-inpatient MVP world — limited experimental Python workflow.
- Compare multiple worlds under alternative assumptions — limited experimental Python workflow.
- Choose any disease, year, and outcome — not currently supported as calibrated product.
- Download calibrated datasets in one click from the website — not currently supported.
- Make population, causal, clinical, or policy claims — not an intended use.

Status labels must be plain English (Available / Limited prototype / Planned / Not a valid use), not promotional badges.

### `researchers/diabetes-hospitalization-example.md` — flagship demonstration

Tell the workflow as a case study:

- *Question:* “Before analyzing restricted Medicare files, how could we test code comparing hospitalization occurrence among people with and without diabetes?”
- *Cohort:* artificial, 2021 Original Medicare FFS-like population aged 65+, full-year Parts A/B under the project's simplified enrollment rule.
- *Core tables:* beneficiary demographics, enrollment, chronic-condition indicators, inpatient claims.
- *Relevant fields:* diabetes and heart failure indicators; at least one inpatient claim; not a principal diagnosis or diabetes-specific admission.
- *Public anchors:* three selected target quantities and their mismatched source years/strengths (2018 diabetes, 2022 HF, industry-based utilization). Clarify transport assumptions.
- *Illustration:* side-by-side Phase 5 worlds, e.g. 6,000 simulated beneficiaries with 404 versus 572 inpatient claim records under different uncalibrated background-risk assumptions, despite matching their chosen calibration targets. Label these as existing stored example outcomes, not universal expected counts.
- *What you can practice:* group/merge code, exposure and outcome definitions, analytic unit checks, simplistic associations, sensitivity to assumptions.
- *What you cannot infer:* real Medicare diabetes effect, model validation accuracy, realistic risk adjustment, diagnosis-specific admission, causal claims.
- *Reproduction:* link to the exact Phase 5 script, configs, reports, and developer guide; avoid presenting it as a no-code download.

### `researchers/getting-started.md` — honest access paths

Give a choice rather than forcing a Python tutorial:

- **Reading/exploration path:** open the worked example, look at illustrative field definitions and stored summary, read the interpretation guide; no installation necessary.
- **Analyst path:** use a colleague/developer to create a valid scenario export, then import CSV/Parquet into R, Stata, Python, or another tool. State the required setup and what output actually exists.
- **Developer path:** go to the installation and CLI documentation.

If a separately packaged sample dataset is later approved, update this page with the verified artifact path, source/evidence profile, supported use, and checksums. Do not write this future path as existing functionality.

### `researchers/understanding-the-data.md`

Introduce beneficiary records, enrollment, condition indicators, claims, and one-to-many relationships using a small diagram or accessible table. Explain why patient count is not claim count, why one patient may have multiple records, and why administrative indicators are not identical to clinical diagnoses. Link technical field definitions.

### `researchers/interpreting-results.md` and `limitations.md`

Separate (1) valid data structure, (2) match on selected published rates, (3) realism for methods testing, (4) real-world inference. Provide an explicit "Safe to say / Not safe to say" comparison. Distinguish simulated parameter truth from empirical Medicare truth. Be clear about the absence of realistic confounding, longitudinal behavior, and validated subgroup performance in the MVP.

### `researchers/faq.md`

Answer: “Are these real Medicare patients?”, “Do I need CMS permission or files to try the demos?”, “Can I use it without coding?”, “Does it support my disease or year?”, “Can I publish analyses of these data?”, “How realistic are admissions and diagnoses?”, “Can I use synthetic results to justify a clinical conclusion?”, “Where do I find setup and technical details?”

## 7. Developer-facing pages and canonical technical records

Move existing installation/CLI/scenario/export/technical concepts/contributor materials under `/developers/`, with updated permalinks. Preserve implementation specificity and verification commands. A dedicated `developers/calibrated-worlds.md` must close the discoverability gap for Phases 1–5 by documenting:

- generation through the current `medicare_synth.synthesis` and `medicare_synth.worlds` APIs;
- the distinction between fixture exports and research MVP world emission;
- how to reproduce the Phase 5 world summary with `uv run python scripts/phase5_emit_worlds.py`;
- how to access `WorldRelease.tables()` and weights, explaining that reports/manifests are not equivalent to exported CSV data;
- how to run the identical analysis across the worlds;
- the model's simplifying assumptions, target evidence grades, and held-out isolation;
- safe downstream export methods only if confirmed with current code and tests;
- links to source-level Phase 0–5 reports and evaluation freeze.

Keep the following canonical and technical rather than translating them into simplified marketing documents:

- Root: `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CHANGELOG.md`, `LESSONS.md`, `AGENTS.md`.
- Source-only `docs/goal.md`, `docs/harness/`, `.agents/skills/`, `docs/phase0` through `docs/phase5` and future phase records, evidence fixtures, and historical proposals.

`developers/project-documents.md` should index all current phases (the current page prominently includes only Phase 0 and Phase 1), distinguish historical proposals from verified state, and link to the canonical implementation/evaluation reports.

**Do not relocate canonical phase files just for aesthetics** if scripts, tests, agents, and links reference them. Instead exclude them consistently from Jekyll publication and make them discoverable through technical source links. This minimizes breakage.

## 8. GitHub Pages design and migration

### Homepage content order

1. Clear value proposition and explicit non-inference boundary.
2. Three supported researcher tasks illustrated by a real example.
3. Visible “What works today / What is limited / What is not intended” navigation.
4. The 2021 diabetes–hospitalization example with one clear comparison.
5. Getting-started options that distinguish reading from running locally.
6. A secondary “Building or extending the toolkit?” gateway to developer documentation.

The homepage should not begin with installation, Python dependencies, commands, metadata counts, or source-manifest terminology. Retain link access for technical users within one click.

### Layout and presentation

- Update `_layouts/default.html` so both audience tracks have clear, persistent navigation; maintain the existing GitHub link.
- Preserve the current design system where possible; do not rebuild the site solely for cosmetic novelty.
- Use practical illustrations sparingly: one minimal cohort/table relationship figure and one actual multi-world comparison can explain substantially more than a dense dashboard or stock imagery.
- Maintain responsive navigation, skip link, visible focus, `aria-current`, keyboard accessibility, contrast, readable line lengths, and descriptive link text. Avoid decorative badge saturation and nested navigation complexity.
- Use source/last-reviewed metadata only when maintainers can reliably update it.
- If multiple navigation groups are visible, prioritize the researcher path and give developers a clear link instead of mixing all guide titles in one flat list.

### Publication rules

- In `docs/_config.yml`, systematically exclude **all** source-only phase directories (including `phase2`–`phase5` and future matching phases), `goal.md`, harness materials, proposal originals, fixtures, and any internal reference not intended as published content.
- Confirm that the Jekyll build includes only curated public pages and intended assets; ensure required front matter and permalinks are present.
- Existing public paths get forwarding pages/redirects with link checks; update all internal GitHub and site links in `README.md`, navigation, 404 page, and maintained docs.
- Do not assume that merely excluding a directory from Jekyll makes its GitHub source private; these files remain public in the repository.

## 9. Documentation claims and governance

Implement a lightweight editorial review contract in `docs/developers/documentation-maintenance.md` and `AGENTS.md`, without changing scientific protocol:

1. **Every user-facing claim has an evidence anchor.** Point to source code, test, captured output, canonical status, or phase report. “Planned” claims link to the roadmap rather than an imaginary feature.
2. **Audience contract.** User docs lead with tasks, illustrations, and plain English. Dev docs lead with mechanisms, exact commands, types, API names, contracts, and reproducibility.
3. **Current vs planned.** Use stable status labels, not “coming soon” unsupported promises, and keep Phase 6 evaluation as unresolved until verified complete.
4. **Literature and calibration.** Always name source population/year, outcome definition, comparability caveat, and evidence strength when citing the example's public calibration numbers.
5. **Scientific guardrail.** Every key user entry point links to the limitations; no synthetic association or model result is represented as an empirical Medicare finding.
6. **Documentation impact in PRs.** Feature changes must review README, capability matrix, case study, docs portal, release limitations, and developer guides as applicable. The phase record remains the source for technical status.
7. **Reviewer roles.** Require both an implementation-aware reviewer (correctness) and a researcher-facing reviewer (comprehension) for top-level public claims. These can be the same person for a small project, but both review perspectives must be documented.

Suggested language substitutions:

| Instead of | Prefer on researcher pages |
| --- | --- |
| fixture compiler | tool for creating example Medicare-like datasets |
| conditional synthesizer | data generator that can control selected relationships |
| evidence-calibrated world | synthetic dataset adjusted toward specified published statistics |
| provenance-backed release | dataset accompanied by information about its sources and generation |
| schema / grain / foreign key | file structure / what one row represents / how records connect |
| estimand / IR / IPF | research quantity being calculated / structured study description / statistical adjustment |
| structural hard gate | a required check on the data's format and internal consistency |

Use a glossary for terms that need to be taught rather than simplifying them out of technical documents.

## 10. Phased implementation plan: bounded PRs

### PR 1 — Content contract and factual inventory (P0)

**Work:** Confirm current `main` implementation state; make a source-backed capabilities matrix and legacy URL map; define researcher/developer page templates; establish publication/non-claim rules. Do not change public navigation yet.

**Deliverables:** Editor checklist / claim inventory, approved proposed IA and URL map, README outline, representative example story, decided list of source-only files.

**Acceptance:** Every proposed “available now” statement has an actual code/test/report anchor. No planned capability is written in the present tense.

### PR 2 — Researcher-first README and researcher content (P0)

**Work:** Rewrite `README.md`. Add `docs/researchers/` pages, including the capabilities matrix, diabetes worked example, interpretation, limits, and FAQ. Use the current world-family summary rather than invented outputs. Update source references when possible.

**Acceptance:** Nontechnical readers can answer what it does, what is currently supported, what requires technical assistance, what is not supported, and how to interpret synthetic results. No copy/paste code is required to read the example.

### PR 3 — Developer consolidation and GitHub Pages IA (P0)

**Work:** Move/copy present guide contents to `/developers/`, add the calibrated-worlds guide, update Jekyll navigation and homepage, implement old-path forwarders, standardize publication excludes, update `404.md` and internal cross-links. Keep canonical phase records at original paths.

**Acceptance:** Both audience tracks are reachable in one click from the homepage; all old public URLs lead to a meaningful replacement; no source-only phase records surface accidentally in published navigation.

### PR 4 — Documentation integrity and editorial QA (P0/P1)

**Work:** Update `scripts/check_documentation_site.py` for new folders, mandatory front matter, duplicate permalinks, old redirect targets, local/relative links, root README links when practical, asset references, and built-site URL resolution; verify Jekyll build; inspect mobile/desktop accessibility and rendering. Update maintainer guidance and any affected AGENTS references.

**Acceptance:** Link checks, rendered-site checks, and CI checks pass; representative documentation examples/commands are independently reproduced; reviewers confirm no claims exceed the demonstrated prototype scope.

### PR 5 — Optional user-experience materials (P1, explicitly not docs-only)

**Only after separate feature verification:** create a small reproducible downloadable sample release from the existing supported MVP, with a manifest, precise data dictionary, generation script, structural/evidence limitations, and research tutorial in R or Python. An actual hosted download or simplified CLI is a product enhancement and needs tests and release review; do not add download CTAs before the asset exists. Do not create a web UI solely as part of this documentation PR series.

## 11. QA, acceptance criteria, and review exercises

### Documentation and publishing checks

- `python3 scripts/check_documentation_site.py` passes after the checker is updated.
- The Pages CI Jekyll build (`.github/workflows/pages.yml`) passes and the deployed site uses the intended `baseurl: /medicare-synth` routes.
- Every root README link, sidebar link, cross-track link, new/legacy permalink, and static asset resolves in the **rendered site**, not only the Markdown source.
- Markdown front matter, headings, title/description metadata, link accessibility, color contrast, keyboard navigation, and mobile menu behavior are checked.
- Phase-specific source-only directories are excluded consistently. No unintentional duplicate pages or duplicate canonical URLs.
- No new runtime feature or release behavior is claimed to be implemented by a docs-only change.
- Any executable snippets are run against the current installed package and exact supported API; otherwise clearly marked illustrative pseudocode.

### Researcher comprehension test

Ask approximately five people with typical clinical/health-services research backgrounds and little project knowledge to complete these tasks using only the new README and website:

1. Identify a study question currently supported as a prototype.
2. Find one research question that is **not** supported.
3. Explain what “adjusted toward published statistics” does and does not guarantee.
4. State whether an effect estimate from these synthetic data can be reported as a Medicare population finding.
5. Locate the worked example, practical access path, and developer guide without reading source code.

Proposed success criterion: at least four of five participants complete each core task without facilitator correction; **all** understand the essential non-inference boundary before the public launch. Record observed confusion, rather than optimizing for self-reported satisfaction alone.

### Suggested factual cross-checks before merge

- `README.md`, `SPEC.md`, `ROADMAP.md`, and the researcher capability matrix agree that Phase 6 is **active**, Phases 0–5 are complete, and Phase 7 is planned (until state actually changes).
- 19 tables does not imply 19 independently calibrated research domains.
- 21 fixtures includes 18 deliberately invalid test cases.
- The calibrated MVP is about any inpatient admission, not diabetes-principal hospitalization, repeat admissions, or causal effects.
- Same selected calibration targets can produce different overall admissions under different free assumptions.
- Source periods/grades are disclosed, especially the 2018/2022 prevalence targets and weaker industry utilization prior.
- The current Phase 5 script is described as a programmatic report/world generator rather than as a browser-based data-download service.
- No statement assumes all private CMS files, years, claims, or longitudinal workflows are supported.

## 12. Ownership and maintenance after launch

- **Repository maintainer:** approves scope, redirects, and truth-in-advertising decisions.
- **Domain reviewer:** checks FFS population/age/enrollment definitions, ICD/claims interpretations, limitations, and how results are presented to researchers.
- **Technical reviewer:** verifies commands, import/API paths, known outputs, Pages build, and old/new links.
- **Agent/docs implementer:** works in bounded PRs, runs checks, updates source cross-references, and reports unresolved gaps; does not silently change scientific targets or evaluation criteria.

Run the claim-consistency checklist whenever the synthesizer, evidence corpus, calibration status, world releases, or public export workflow changes. Review the site at least at each major milestone; add a dated status snapshot only when it has an active owner.

## 13. Explicit non-goals and deferred decisions

This documentation initiative **will not**:

- expand or materially alter the generator, Evidence IR, calibration, or clinical validation code;
- treat the current data as a validated substitute for restricted CMS Medicare analysis;
- introduce an automated literature-to-truth pipeline or publish revised calibration evidence without domain approval;
- claim full cohort, claims-level, longitudinal, provider, geography, or causal realism;
- build a separate web application, hosted dataset generator, no-code wizard, or downloadable calibrated data bundle unless implemented and tested in a separate product PR;
- erase technical development records or change their meaning to simplify public messaging;
- create parallel authoritative technical specifications that can drift out of sync.

**Decisions to make during PR 1:** exact user-facing nomenclature (“Medicare-like synthetic data” versus “Medicare synthetic data”), whether the researcher site includes a static table preview in the first release, choice of redirect implementation compatible with existing Pages deployment, and whether a versioned small sample-data release is a follow-on priority. These are documentation/product decisions, not reasons to delay the core restructure.

## 14. Definition of done

The work is complete when a newcomer landing on the GitHub repository or Pages site understands the research benefit **before** encountering build-system details; can identify a real supported scenario and at least one unsupported one; can explain that synthetic findings are not Medicare population estimates; and can choose a clearly labeled researcher or developer pathway. The technical detail remains intact, linkable, and verifiably current; all old URLs and Pages builds work; and the documentation change does not overstate the software's maturity.

## 15. Key source anchors

- [Root README](https://github.com/SaehwanPark/medicare-synth/blob/main/README.md)
- [Current GitHub Pages source homepage](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/index.md)
- [Current site layout/navigation](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/_layouts/default.html)
- [Site Jekyll configuration](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/_config.yml)
- [Docs checker](https://github.com/SaehwanPark/medicare-synth/blob/main/scripts/check_documentation_site.py)
- [Roadmap](https://github.com/SaehwanPark/medicare-synth/blob/main/ROADMAP.md)
- [Phase 1 generator report](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/phase1/capability-report.md)
- [Phase 3 corpus freeze](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/phase3/corpus-freeze.md)
- [Phase 5 world family](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/phase5/world-family.md)
- [Phase 5 capability report](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/phase5/capability-report.md)
- [Phase 5 example output](https://github.com/SaehwanPark/medicare-synth/blob/main/reports/phase5/world_family_summary.json)
- [Generator implementation](https://github.com/SaehwanPark/medicare-synth/blob/main/src/medicare_synth/synthesis.py)
- [Current Phase 5 emit script](https://github.com/SaehwanPark/medicare-synth/blob/main/scripts/phase5_emit_worlds.py)
