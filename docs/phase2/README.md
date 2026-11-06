# Phase 2 — Evidence IR and executable study language

**Status:** Complete (2026-11-06)

## Outputs

| Artifact | Path |
| --- | --- |
| Schema notes | [evidence-ir-schema.md](evidence-ir-schema.md) |
| LIT-03 formalization | [lit03-formalization.md](lit03-formalization.md) |
| Capability / exit report | [capability-report.md](capability-report.md) |
| Fixtures | [fixtures/](fixtures/) |
| Comparison JSON | [`reports/phase2/lit03_comparison.json`](../../reports/phase2/lit03_comparison.json) |

## Runtime

Package: `medicare_synth.evidence_ir`

- `load_finding` / `parse_finding` / `validate_finding`
- `compile_finding` → eligibility, derivation, estimator, compatibility
- `execute_finding` → reproducible comparison report
- `draft_finding_from_fields` → always `review_status=draft`

Primary reviewed finding: Andes et al. MMWR 2019 diabetes prevalence 31.6%
(2015 Medicare FFS ≥68), inventory **LIT-03**, role **diagnostic**.
