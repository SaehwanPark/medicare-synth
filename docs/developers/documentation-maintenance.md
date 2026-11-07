---
title: "Documentation maintenance"
description: "Editorial contract, claim inventory anchors, URL map, and publication rules for the researcher-first docs site."
permalink: /developers/documentation-maintenance/
---

# Documentation maintenance

Public documentation is **researcher-first, not researcher-only**. User-facing
pages summarize what works today; code, tests, and canonical state records remain
implementation truth. Do not invent hosted downloads, generalized disease
calibration, or population inference.

## Audience contract

| Track | Leads with | Avoids as the opener |
| --- | --- | --- |
| Researchers (`docs/researchers/`, root README, homepage) | Tasks, worked example, plain-language limits | Library names, IR jargon, install-first flows |
| Developers (`docs/developers/`) | Commands, APIs, schema, reproducibility | Marketing promises without anchors |
| Canonical / source-only | `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, phase reports, harness | Jekyll publication |

## Status labels

Use these plain-English labels on researcher pages:

- **Available** — demonstrated by code/tests/fixtures today
- **Limited prototype** — works for a pinned MVP context with disclosed assumptions
- **Planned** — on the roadmap; not present-tense product
- **Not a valid use** — deliberately outside project claims

“Implemented” is not “evaluated for research use.” Phase 6 owns independent
evaluation until that work is verified complete.

## Claim inventory (anchors)

Every user-facing “available now” claim must point at an anchor:

| Claim | Anchor |
| --- | --- |
| Structural fixtures / validation | `medicare_synth` scenarios; `uv run medicare-synth validate`; docs under `developers/` |
| 19 modeled domain tables | package schema / data-model guide; not 19 calibrated research domains |
| 21 catalog scenarios (3 valid, 18 intentional anomalies) | `medicare-synth catalog`; first-run guide |
| Bounded 2022 PUF beneficiary/carrier importer | `SPEC.md` / importer tests; not all years/file families |
| 2021 OM FFS diabetes → all-cause inpatient MVP | `docs/phase0/`–`docs/phase5/`; `medicare_synth.synthesis` / `worlds` |
| Selected calibration moments (diabetes ~27.7% 2018; HF ~12% 2022; ~13% IP\|diabetes industry prior) | frozen corpus + `reports/phase5/world_family_summary.json` |
| Multi-world illustration (e.g. 6,000 beneficiaries; 404 vs 572 inpatient claims) | stored Phase 5 family summary; not universal expected counts |
| Fixture CSV/Parquet export | `medicare-synth export`; export-and-release guide |
| Phase 5 emit writes reports/manifests | `scripts/phase5_emit_worlds.py`; not a one-click calibrated CSV product |
| Phases 0–5 complete; Phase 6 active | `ROADMAP.md`, `CHANGELOG.md` |
| Synthetic results ≠ Medicare findings | limitations pages; evaluation freeze non-claims |

## Legacy URL map

| Existing path | Destination |
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

Legacy paths keep human-readable forwarder pages. Do not strand public URLs.

## Publication excludes

Jekyll must exclude source-only engineering records: all `phase*` directories,
`goal.md`, `harness/`, proposal originals, and this reorganization plan when it
is not intended as published content. Exclusion does **not** hide files from the
GitHub repository.

## PR documentation impact

When a change touches synthesizer, evidence, calibration, worlds, or public
export behavior, review as applicable:

1. Root `README.md`
2. Researcher capability matrix and worked example
3. Homepage / interpretation / limitations
4. Affected developer guides
5. Phase / capability reports (canonical technical status)

Prefer an implementation-aware check (commands and anchors correct) and a
researcher-facing check (no overstated claims) before merging top-level public
copy. The same person may perform both perspectives on a small project.

## Language substitutions (researcher pages)

| Prefer | Instead of leading with |
| --- | --- |
| tool for creating example Medicare-like datasets | fixture compiler |
| data generator that can control selected relationships | conditional synthesizer |
| synthetic dataset adjusted toward specified published statistics | evidence-calibrated world |
| dataset accompanied by source/generation information | provenance-backed release |
| file structure / what one row represents / how records connect | schema / grain / foreign key |
| research quantity / structured study description / statistical adjustment | estimand / IR / IPF |

Keep technical terms on developer pages; teach them via glossary links when needed.

## Verification

```shell
python3 scripts/check_documentation_site.py
```

Also confirm the Pages workflow build and that rendered routes under
`baseurl: /medicare-synth` resolve for new and legacy permalinks.
