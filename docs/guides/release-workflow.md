---
title: "Export a release bundle"
description: "Create versioned, checksummed Medicare-Synth artifacts with validation, fidelity, and limitations reports."
permalink: /guides/release-workflow/
---

# Export a release bundle

The release exporter turns a deterministic scenario or normalized source slice
into portable artifacts. Keep the output in an ignored directory until you are
ready to publish it through your own distribution process.

## Export a scenario

```shell
uv run medicare-synth export \
  --scenario valid_baseline_cohort \
  --output-dir ./dist/release_v1 \
  --format all \
  --release-id v1.0.0-2021
```

`--format` accepts `csv`, `parquet`, or `all` (the default). The release ID is
metadata; it does not change the generated values.

## What the exporter writes

Depending on the scenario and format, the output includes:

- table files in CSV and/or Parquet;
- `release_manifest.json` with file sizes and SHA-256 checksums;
- `validation_report.json` for the exported slice;
- `fidelity_profile.json` describing supported structural claims;
- `sql_reference_schema.sql` for downstream relational inspection; and
- a separately generated `limitations_profile.json` when you run the
  `profile` command for the same release.

The manifest is the handoff point: use it to verify that a copied bundle is the
same bundle, not merely a directory with similar filenames.

## Export CI fixtures

```shell
uv run medicare-synth export-ci \
  --output-dir ./dist/ci-fixtures \
  --format parquet
```

This writes every named catalog scenario in a lightweight format. Keep these
fixtures small and interpretable; they are designed for tests, examples, and
education rather than benchmarking a production warehouse.

## Import the bounded 2022 PUF slice

The PUF path is additive and source-aware. Acquire the official files locally,
then supply the tracked manifest and evidence snapshot:

```shell
uv run medicare-synth puf \
  --source-dir ./data/cms_puf_2022 \
  --manifest ./data/manifests/cms_2022_syn_puf_manifest.json \
  --evidence ./data/rkb_snapshots/rkb-v1.1-20220701.json \
  --output-dir ./dist/puf_2022 \
  --format all
```

This command is deliberately bounded to the 2022 beneficiary and carrier
files. The default scenario and release examples remain on the 2021 synthetic
baseline.

## Release checklist

1. Confirm the source manifest and evidence snapshot are pinned and checksummed.
2. Run the valid scenario and its focused anomaly tests.
3. Generate the release bundle and inspect the validation/fidelity/limitations
   reports.
4. Verify checksums after copying or publishing artifacts.
5. State what the bundle does **not** claim in the accompanying release note.

See [Limitations &amp; scope](../reference/limitations/) for the claims boundary.
