---
title: "Canonical project documents"
description: "Find the authoritative specifications, architecture notes, roadmap, history, and contributor policies behind the portal."
permalink: /reference/project-documents/
---

# Canonical project documents

The portal is an entry point, not a replacement for the repository’s source of
truth. Use this map when you need the full contract or historical context.

| Document | Use it for |
| --- | --- |
| [`README.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/README.md) | Repository-level orientation and a copy/paste quickstart. |
| [`SPEC.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/SPEC.md) | Completed, active, and planned technical specifications. |
| [`ARCHITECTURE.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/ARCHITECTURE.md) | Component boundaries, data flow, invariants, and external interfaces. |
| [`ROADMAP.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/ROADMAP.md) | Milestones, ordering, outputs, and exit criteria. |
| [`CHANGELOG.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/CHANGELOG.md) | User-visible implementation history. |
| [`LESSONS.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/LESSONS.md) | Verified recurring setup and debugging lessons. |
| [Project proposal](https://github.com/SaehwanPark/medicare-synth/blob/main/docs/medicare-synth-project-proposal_20260720.md) | Strategic motivation and intended user groups. |
| [`AGENTS.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/AGENTS.md) | Repository-wide instructions for contributors and agents. |

## Evidence and source records

Source manifests and RKB evidence snapshots live under `data/` and are tracked
without raw CMS data. The [release workflow](../guides/release-workflow/)
explains how to acquire, verify, normalize, and export a bounded slice.

## Current versus historical context

The specification and architecture describe current project state. The proposal
and changelog preserve decisions and motivation, but older entries should not be
treated as current behavior when code or newer canonical documents disagree.
