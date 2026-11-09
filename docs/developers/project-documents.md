---
title: "Canonical project documents"
description: "Find the authoritative specifications, architecture notes, roadmap, phase records, history, and contributor policies behind the portal."
permalink: /developers/project-documents/
---

# Canonical project documents

The portal is an entry point, not a replacement for the repository’s source of
truth. Use this map when you need the full contract or historical context.

| Document | Use it for |
| --- | --- |
| [`README.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/README.md) | Public/researcher-first orientation. |
| [`SPEC.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/SPEC.md) | Completed, active, and planned technical specifications. |
| [`ARCHITECTURE.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/ARCHITECTURE.md) | Component boundaries, data flow, invariants, and external interfaces. |
| [`ROADMAP.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/ROADMAP.md) | Milestones, ordering, outputs, and exit criteria. |
| [`CHANGELOG.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/CHANGELOG.md) | User-visible implementation history. |
| [`LESSONS.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/LESSONS.md) | Verified recurring setup and debugging lessons. |
| [`docs/goal.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/goal.md) | Active agent/contributor goal prompt (source-only). |
| [`AGENTS.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/AGENTS.md) | Repository-wide instructions for contributors and agents. |
| [Documentation maintenance](../documentation-maintenance/) | Editorial contract, claim anchors, URL map, publication rules. |

## Phase records (source-only; not Jekyll-published)

| Path | Status (see ROADMAP) |
| --- | --- |
| [`docs/phase0/`](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/phase0/) | Complete — feasibility, cohort/fields, evidence inventory |
| [`docs/phase1/`](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/phase1/) | Complete — synthesizer contract and capability report |
| [`docs/phase2/`](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/phase2/) | Complete — Evidence IR |
| [`docs/phase3/`](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/phase3/) | Complete — evidence corpus freeze |
| [`docs/phase4/`](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/phase4/) | Complete — calibration engine |
| [`docs/phase5/`](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/phase5/) | Complete — MVP calibrated multi-world family |
| Phase 6 | **Active** — independent evaluation; correctness hardening gates affirmative release claims |
| Phase 7A–7F | **Planned** — correctness, inferential IR, joint synthesis, continual calibration, base/world separation, scaling (see ROADMAP) |

Implementation walkthrough for the MVP worlds:
[Calibrated worlds](../calibrated-worlds/).

## Realignment and planned direction

The [November 8 audit](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/audits/audit-for-project-realignement-20261108.md)
is planning input, not a test or evaluation report. The canonical documents
adopt a planned shared, versioned Medicare-like population model whose outputs
are reproducible datasets and derived research worlds. The current product
remains the limited MVP; adjusted inferential calibration and general continual
model updates are not available yet. See `SPEC.md` and `ROADMAP.md` for audit
caveats, the bounded joint + adjusted-logistic experiment and acceptance gates.

## Historical proposals

| Document | Role |
| --- | --- |
| [Evidence-calibrated playground proposal](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/medicare_synth_evidence_calibrated_playground_proposal.md) | November 6 design history; November 8 canonical realignment supersedes conflicting strategy/ordering |
| [Original project proposal](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/medicare-synth-project-proposal_20260720.md) | Earlier product motivation |
| [Documentation reorganization plan](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/medicare_synth_documentation_reorganization_plan.md) | IA plan for this researcher-first docs site |

Older proposals preserve decisions and motivation; they are not current behavior
when code or newer canonical documents disagree.

## Evidence and source records

Source manifests and RKB evidence snapshots live under `data/` and are tracked
without raw CMS data. The [export and release](../export-and-release/) guide
explains how to acquire, verify, normalize, and export a bounded slice.
