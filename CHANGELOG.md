# CHANGELOG

## Unreleased

### Added

- Added `--summary-check` parameter to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `summary_check` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to enable aggregated dataset summary matrix verification across all 19 Medicare synthetic data tables before staging and committing.
- Extended unit test suites in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `summary_check` verification logic and CLI flag parsing.

- Added `--benchmark-check` parameter to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `benchmark_check` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to enable synthetic data throughput performance benchmarking before staging and committing.
- Extended unit test suites in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `benchmark_check` verification logic and CLI flag parsing.

- Added `--provenance-check` parameter to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `provenance_check` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to enable field-level dataset provenance taxonomy verification prior to staging and committing.
- Extended unit test suites in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `provenance_check` verification logic and CLI flag parsing.

- Added `--expansion-check` and `--checkout-main` parameters to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `expansion_check` and `checkout_main` parameters to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to enable dataset expansion verification and post-merge main branch sync.
- Extended unit test suites in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `expansion_check` and `checkout_main` verification logic and CLI flag parsing.

- Added `--catalog-check`, `--diff-check`, and `--profile-check` parameters to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `catalog_check` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to enable scenario catalog indexing verification and complete CLI flag registration.
- Extended unit test suites in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `catalog_check`, `diff_check`, `profile_check`, and `all_checks` verification logic and CLI flag parsing.

- Added `--all-checks` and `--export-check` parameters to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `all_checks` and `export_check` parameters to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to enable composite verification checks and release export verification prior to staging/committing.
- Extended unit test suite in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `all_checks` and `export_check` verification logic and CLI flag parsing.

- Added `--validation-check` parameter to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `validation_check` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to verify dataset relational validation integrity before staging and committing.
- Extended unit test suite in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `validation_check` status verification logic and CLI flag parsing.
- Added `--audit-check` parameter to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `audit_check` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to verify dataset privacy and relational join audit status before staging and committing.
- Extended unit test suite in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `audit_check` status verification logic and CLI flag parsing.
- Added `--html-report` parameter to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `html_report_path` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to generate HTML summary execution reports.
- Extended unit test suite in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `html_report_path` report generation and CLI flag parsing.
- Added `--git-clean-check` parameter to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `git_clean_check` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to verify git working tree status during automated workflow execution.
- Extended unit test suite in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `git_clean_check` status verification logic and CLI flag parsing.
- Added `--md-report` parameter to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `md_report_path` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to generate clean Markdown summary reports of workflow execution status.
- Extended unit test coverage in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to verify Markdown report generation and CLI flag parsing.
- Added `--changelog-check` parameter to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `changelog_check` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to verify `CHANGELOG.md` updates before committing and pushing.
- Extended unit test suite in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to cover `changelog_check` verification logic and CLI flag parsing.
- Added `--json-report` parameter to `auto-workflow` subcommand in `src/medicare_synth/cli.py` and `json_report_path` parameter to `run_autonomous_workflow` in `src/medicare_synth/workflow.py` to write structured execution summaries.
- Extended unit test coverage in `tests/test_autonomous_workflow.py` and `tests/test_cli.py` to verify JSON report output generation.
- Added `auto-workflow` subcommand to `medicare-synth` CLI in `src/medicare_synth/cli.py` and reusable workflow execution core in `src/medicare_synth/workflow.py`.
- Refactored `scripts/autonomous_workflow.py` to leverage `src/medicare_synth/workflow.py` engine.
- Exported `run_autonomous_workflow` in package entrypoint `src/medicare_synth/__init__.py`.
- Added unit test coverage for `auto-workflow` CLI subcommand in `tests/test_cli.py`.
- Created `scripts/autonomous_workflow.py` to automate repository validation checks, staging, committing, pushing, and autonomous pull request merge.
- Created `tests/test_autonomous_workflow.py` to cover mock execution pathways and dry-run safety gates.
- Extended `AuditEngine` and `AuditReport` in `src/medicare_synth/audit.py` to calculate k-anonymity privacy scores for all 19 tables in the dataset, covering all remaining Master Beneficiary Summary File (MBSF) segments (`mbsf_cu`, `mbsf_d`, `mbsf_base`, `mbsf_ndi`, `mbsf_ra`, `mbsf_c`, `mbsf_ffs`, `mbsf_pde_util`).
- Extended test coverage in `tests/test_audit.py` to assert correct k-anonymity score calculations and quasi-identifiers for all 19 tables.
- Extended `AuditEngine` and `AuditReport` in `src/medicare_synth/audit.py` to calculate k-anonymity privacy scores for additional clinical tables (`outpatient`, `snf`, `hha`, `dme`, `hospice`) and MBSF segments (`mbsf_cc`, `mbsf_oc`).
- Added optional `--output-dir` parameter to the `validate` subcommand parser in `src/medicare_synth/cli.py` to write the validation report to a JSON file.
- Added `pyrightconfig.json` to configure basedpyright type-checking rules for clean static analysis.

- Implemented `MBSFPartDPDEUtilizationRecord` domain model in `src/medicare_synth/models.py`.
- Added Master Beneficiary Summary File (MBSF) Part D PDE Cost & Utilization Segment file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`PDE_TOT_FILL_CNT`, `PDE_BRAND_FILL_CNT`, `PDE_GENERIC_FILL_CNT`, `PDE_TOT_CST_AMT`, `PDE_PTNT_PAY_AMT`, `PDE_LIS_PAY_AMT`, `VAL_MBSF_PDE_UTIL_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_mbsf_pde_util_field_constraints` and updated `validate_slice` to validate MBSF Part D PDE Utilization foreign key integrity and count/amount non-negativity (`FLD-015`).
- Updated `ScenarioCompiler` to compile MBSF Part D PDE Utilization data frames across all scenarios and added `invalid_mbsf_pde_utilization_count` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle MBSF Part D PDE Utilization Segment.
- Added comprehensive unit test suite in `tests/test_mbsf_pde_util.py` (144 total passing unit tests).

- Implemented `MBSFFFSUtilizationRecord` domain model in `src/medicare_synth/models.py`.
- Added Master Beneficiary Summary File (MBSF) Fee-For-Service (FFS) Utilization Segment file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`IP_ADM_CNT`, `OP_VIST_CNT`, `SNF_STAY_CNT`, `CAR_SRVC_CNT`, `HHA_VIST_CNT`, `HOSP_STAY_CNT`, `DME_SRVC_CNT`, `VAL_MBSF_FFS_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_mbsf_ffs_field_constraints` and updated `validate_slice` to validate MBSF FFS Utilization foreign key integrity and count non-negativity (`FLD-014`).
- Updated `ScenarioCompiler` to compile MBSF FFS Utilization data frames across all scenarios and added `invalid_mbsf_ffs_utilization_count` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle MBSF FFS Utilization Segment.
- Added comprehensive unit test suite in `tests/test_mbsf_ffs.py` (139 total passing unit tests).

- Implemented `MBSFPartCRecord` domain model in `src/medicare_synth/models.py`.
- Added Master Beneficiary Summary File (MBSF) Part C / Medicare Advantage Segment file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`PTC_CNTRCT_ID_01`, `PTC_PBP_ID_01`, `PTC_PLAN_TYPE_CD_01`, `BENE_MA_CVRAGE_TOT_MONS`, `VAL_MBSF_C_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_mbsf_c_field_constraints` and updated `validate_slice` to validate MBSF Part C foreign key integrity and coverage month bounds (`FLD-013`).
- Updated `ScenarioCompiler` to compile MBSF Part C data frames across all scenarios and added `invalid_mbsf_part_c_contract` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle MBSF Part C Segment.
- Added comprehensive unit test suite in `tests/test_mbsf_c.py` (134 total passing unit tests).


- Implemented `MBSFRiskAdjustmentRecord` domain model in `src/medicare_synth/models.py`.
- Added Master Beneficiary Summary File (MBSF) Risk Adjustment Segment file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`CMS_HCC_RISK_SCORE`, `RXHCC_RISK_SCORE`, `PAYMENT_COUNT`, `VAL_MBSF_RA_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_mbsf_ra_field_constraints` and updated `validate_slice` to validate MBSF Risk Adjustment foreign key integrity and risk score field constraints (`FLD-012`).
- Updated `ScenarioCompiler` to compile MBSF Risk Adjustment data frames across all scenarios and added `invalid_mbsf_risk_adjustment_score` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle MBSF Risk Adjustment Segment.
- Added comprehensive unit test suite in `tests/test_mbsf_ra.py` (129 total passing unit tests).

- Implemented `MBSFNDIRecord` domain model in `src/medicare_synth/models.py`.
- Added Master Beneficiary Summary File (MBSF) National Death Index (NDI) Segment file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`NDI_MATCH_IND`, `NDI_DIUSE_CD`, `VAL_MBSF_NDI_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_mbsf_ndi_field_constraints` and updated `validate_slice` to validate MBSF NDI foreign key integrity and match indicator constraints (`FLD-011`).
- Updated `ScenarioCompiler` to compile MBSF NDI data frames across all scenarios and added `invalid_mbsf_ndi_match_indicator` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle MBSF NDI Segment.
- Added comprehensive unit test suite in `tests/test_mbsf_ndi.py` (124 total passing unit tests).

- Implemented `MBSFOtherChronicConditionsRecord` domain model in `src/medicare_synth/models.py`.

- Added Master Beneficiary Summary File (MBSF) Other Chronic Conditions Segment file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`SP_ARTHGLAU`, `SP_ASTHMA`, `SP_ATRIALF`, `SP_HYPERL`, `SP_HYPERT`, `SP_HYPOT`, `SP_OSTEOP`, `VAL_MBSF_OC_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_mbsf_oc_field_constraints` and updated `validate_slice` to validate MBSF Other Chronic Conditions foreign key integrity and condition indicator constraints (`FLD-010`).
- Updated `ScenarioCompiler` to compile MBSF Other Chronic Conditions data frames across all scenarios and added `invalid_mbsf_other_chronic_condition_indicator` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle MBSF Other Chronic Conditions Segment.
- Added comprehensive unit test suite in `tests/test_mbsf_oc.py` (118 total passing unit tests).


- Implemented `MBSFBaseEnrollmentRecord` domain model in `src/medicare_synth/models.py`.
- Added Master Beneficiary Summary File (MBSF) Base / Enrollment Segment file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`BENE_HI_CVRAGE_TOT_MONS`, `BENE_SMI_CVRAGE_TOT_MONS`, `BENE_HMO_CVRAGE_TOT_MONS`, `BENE_PTD_CVRAGE_TOT_MONS`, `MDCR_ENTLMT_BUYIN_IND_01`, `DUAL_STUS_CD_01`, `VAL_MBSF_BASE_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_mbsf_base_field_constraints` and updated `validate_slice` to validate MBSF Base Enrollment foreign key integrity and coverage month bounds (`FLD-009`).
- Updated `ScenarioCompiler` to compile MBSF Base Enrollment data frames across all scenarios and added `invalid_mbsf_base_coverage_months` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle MBSF Base / Enrollment Segment.
- Added comprehensive unit test suite in `tests/test_mbsf_base.py` (112 total passing unit tests).

- Implemented `MBSFPartDRecord` domain model in `src/medicare_synth/models.py`.

- Added Master Beneficiary Summary File (MBSF) Part D Characteristics Segment file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`PTD_CNTRCT_ID_01`, `PTD_PBP_ID_01`, `PTD_SGNT_CD_01`, `RDS_IND_01`, `LI_COST_SHRH_GRP_CD_01`, `BENE_PTD_TRCC_AMT`, `BENE_PTD_MOOP_AMT`, `VAL_MBSF_D_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_mbsf_d_field_constraints` and updated `validate_slice` to validate MBSF Part D foreign key integrity and drug cost field constraints (`FLD-008`).
- Updated `ScenarioCompiler` to compile MBSF Part D data frames across all scenarios and added `invalid_mbsf_part_d_contract` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle MBSF Part D Segment.
- Added comprehensive unit test suite in `tests/test_mbsf_d.py` (106 total passing unit tests).

- Implemented `MBSFCostAndUseRecord` domain model in `src/medicare_synth/models.py`.
- Added Master Beneficiary Summary File (MBSF) Cost & Use Segment file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`BENE_MDCR_PAY_AMT`, `BENE_TOT_PAY_AMT`, `BENE_IP_DDCTBL_AMT`, `BENE_CVRD_DYS_CNT`, `VAL_MBSF_CU_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_mbsf_cu_field_constraints` and updated `validate_slice` to validate MBSF Cost & Use foreign key integrity and payment field constraints (`FLD-007`).
- Updated `ScenarioCompiler` to compile MBSF Cost & Use data frames across all scenarios and added `invalid_mbsf_cost_use_payment` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle MBSF Cost & Use Segment.
- Added comprehensive unit test suite in `tests/test_mbsf_cu.py` (99 total passing unit tests).

- Implemented `MBSFChronicConditionsRecord` domain model in `src/medicare_synth/models.py`.
- Added Master Beneficiary Summary File (MBSF) Chronic Conditions Segment file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`SP_ALZHMD`, `SP_CHF`, `SP_CHRNKIDN`, `SP_CNCR`, `SP_DIABETES`, `SP_ISCHDMT`, `SP_STRKETIA`, `VAL_MBSF_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_mbsf_cc_field_constraints` and updated `validate_slice` to validate MBSF Chronic Conditions foreign key integrity and field constraints (`FLD-006`).
- Updated `ScenarioCompiler` to compile MBSF Chronic Condition data frames across all scenarios and added `invalid_mbsf_chronic_condition_indicator` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle MBSF Chronic Conditions.
- Added comprehensive unit test suite in `tests/test_mbsf.py` (92 total passing unit tests).
- Implemented `HospiceClaimHeaderRecord` domain model in `src/medicare_synth/models.py`.
- Added Hospice Claims file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`HOSPICE_TERMINAL_DIAG_CD`, `VAL_HOSPICE_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_hospice_field_constraints` and updated `validate_slice` to validate Hospice foreign key integrity, admission temporal ordering, and field constraints (`FLD-005`).
- Updated `ScenarioCompiler` to compile Hospice claim data frames across all scenarios and added `invalid_hospice_utilization_days` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle Hospice Claims.
- Added comprehensive unit test suite in `tests/test_hospice.py` (85 total passing unit tests).
- Implemented `DurableMedicalEquipmentClaimRecord` domain model in `src/medicare_synth/models.py`.
- Added Durable Medical Equipment (DME) Claims file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`DME_LINE_ITEM_COUNT`, `LINE_CMS_TYPE_SRVC_CD`, `VAL_DME_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_dme_field_constraints` and updated `validate_slice` to validate DME foreign key integrity, temporal ordering, and field constraints (`FLD-004`).
- Updated `ScenarioCompiler` to compile DME claim data frames across all scenarios and added `invalid_dme_line_item_count` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle DME Claims.
- Added comprehensive unit test suite in `tests/test_dme.py` (77 total passing unit tests).
- Implemented `HomeHealthAgencyClaimRecord` domain model in `src/medicare_synth/models.py`.
- Added Home Health Agency (HHA) Claims file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`CLM_ADMSN_DT`, `NCH_BENE_DSCHRG_DT`, `CLM_UTLZTN_DAY_CNT`, `CLM_HHA_LUPA_IND`, `VAL_HHA_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_hha_field_constraints` and updated `validate_slice` to validate HHA foreign key integrity, admission temporal order, and field constraints (`FLD-003`).
- Updated `ScenarioCompiler` to compile HHA claim data frames across all scenarios and added `invalid_hha_utilization_days` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle HHA Claims.
- Added comprehensive unit test suite in `tests/test_hha.py` (69 total passing unit tests).
- Implemented `SkilledNursingFacilityClaimRecord` domain model in `src/medicare_synth/models.py`.
- Added Skilled Nursing Facility (SNF) Claims file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`CLM_ADMSN_DT`, `NCH_BENE_DSCHRG_DT`, `CLM_UTLZTN_DAY_CNT`, `NCVD_DAYS_CNT`, `CLM_PMT_AMT`, `VAL_SNF_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_snf_field_constraints` and updated `validate_slice` to validate SNF foreign key integrity, admission temporal order, and field constraints (`FLD-002`).
- Updated `ScenarioCompiler` to compile SNF claim data frames across all scenarios and added `invalid_snf_utilization_days` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`, `catalog`, `export-ci`) to handle SNF Claims.
- Added comprehensive unit test suite in `tests/test_snf.py` (61 total passing unit tests).
- Implemented `PrescriptionDrugEventRecord` domain model in `src/medicare_synth/models.py`.

- Added Part D Prescription Drug Event file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`PDE_ID`, `SRVC_DT`, `PROD_SRVC_ID`, `QTY_DSPNSD_NUM`, `DAYS_SUPLY_NUM`, `PTNT_PAY_AMT`, `TOT_RX_CST_AMT`, `VAL_NUM_01`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_pde_field_constraints` and updated `validate_slice` to validate PDE foreign key integrity and field constraints (`FLD-001`).
- Updated `ScenarioCompiler` to compile PDE data frames across all scenarios and added `invalid_pde_days_supply` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`) to handle Part D Prescription Drug Events.
- Added comprehensive unit test suite in `tests/test_pde.py` (56 total passing unit tests).
- Implemented `InpatientClaimHeaderRecord` domain model in `src/medicare_synth/models.py`.

- Added Inpatient Claims file entry to `data/manifests/cms_2021_syn_claims_manifest.json` and variable/constraint contracts (`CLM_ADMSN_DT`, `NCH_BENE_DSCHRG_DT`, `CLM_PMT_AMT`, `CLM_UTLZTN_DAY_CNT`, `CLM_DRG_CD`, `VAL_TEMP_02`) to `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Extended `RelationalValidator` with `check_admission_temporal_inversions` and updated `validate_slice` to validate inpatient claim relational integrity and admission temporal order (`TMP-002`).
- Updated `ScenarioCompiler` to compile inpatient claims data frames across all scenarios and added `invalid_inpatient_admission` anomaly scenario fixture.
- Updated `BaselineNormalizer`, `ReleaseExporter`, `VerticalExpander`, `HorizontalExpander`, `ScenarioCatalog`, `AuditEngine`, and `CLI` subcommands (`validate`, `scenario`, `export`, `expand`, `audit`) to handle Inpatient Claims.
- Added comprehensive unit test suite in `tests/test_inpatient.py` (49 total passing unit tests).
- Implemented `AuditEngine` and `AuditReport` in `src/medicare_synth/audit.py` providing relational join coverage, k-anonymity privacy scoring, and column nullity/uniqueness metrics.
- Exposed `audit` subcommand in `src/medicare_synth/cli.py` (`medicare-synth audit --scenario <name> --output-dir <path>`).
- Added unit test suite in `tests/test_audit.py` (44 total passing unit tests).
- Configured explicit `[build-system]` with `hatchling` backend and `tool.uv.package = true` in `pyproject.toml`.
- Strongly typed `ScenarioCatalog._CATALOG` with `ScenarioEntry` instances, achieving 0 Pyright static type errors.
- Cleaned unused imports across source and test files (`diff.py`, `profile.py`, `test_catalog.py`, `test_diff.py`).

- Contributor-first README and repository-wide agent guidance.
- Portable Medicare foundation-slice harness with deterministic local handoffs
  and bounded domain review.
- Lightweight specification, architecture, roadmap, changelog, and lessons
  documents for project bookkeeping.
- Pinned CMS 2021 Synthetic Claims collection (`CMS-2021-SYN-CLAIMS`) as canonical baseline and 2021 CCW layout as target schema year.
- Defined 8-tag provenance status taxonomy for field-level lineage tracking.
- Established immutable RKB evidence bundle snapshot contract (`data/rkb_snapshots/`).
- Selected Pydantic v2 and Polars / PyArrow as canonical hybrid schema and validation runtime stack.
- Added `pydantic`, `polars`, and `pyarrow` core dependencies to `pyproject.toml`.
- Formalized 5-category minimum validation constraint set (Field, Record, Relational, Temporal, Administrative).
- Specified initial 5 deterministic scenarios (3 valid baseline fixtures, 2 intentional anomaly fixtures).
- Established Apache-2.0 open-source license, manifest-based raw data acquisition rules, and release artifact publication paths.
- Completed Milestone 1 (Foundation Decisions) across all 6 core deliverables.
- Created CMS 2021 Synthetic Claims baseline source manifest `data/manifests/cms_2021_syn_claims_manifest.json`.
- Created versioned RKB evidence snapshot contract `data/rkb_snapshots/rkb-v1.0-20211231.json`.
- Initialized core Python package `src/medicare_synth/` (`manifest.py`, `evidence.py`, `models.py`) with Pydantic v2 models.
- Added unit test suite under `tests/` with 10 passing tests for manifest verification, evidence snapshot lookups, and domain record constraints.
- Added `pytest` dev dependency to `pyproject.toml` and configured `pythonpath = ["src"]`.
- Completed Milestone 2 (Baseline and Evidence) across all deliverables.
- Implemented core validation framework in `src/medicare_synth/validation.py` (`Severity`, `FindingCategory`, `Finding`, `ValidationReport`).
- Added Polars-backed `RelationalValidator` supporting foreign key integrity (`CLM_ID` -> `BENE_ID`), temporal order (`CLM_FROM_DT` <= `CLM_THRU_DT`), and record uniqueness (`REC-001`).
- Added 4 unit tests in `tests/test_validation.py` covering normal validation and anomaly scenarios (`invalid_orphaned_claim`, `invalid_temporal_inversion`).
- Implemented `ProvenanceStatus` enum in `src/medicare_synth/models.py` tracking 8 field-level lineage categories.
- Created `ScenarioCompiler` in `src/medicare_synth/scenarios.py` compiling 5 named deterministic scenario fixtures into Polars DataFrames.
- Created `BaselineNormalizer` in `src/medicare_synth/normalizer.py` for type-casting raw records to Polars DataFrames with provenance annotations.
- Created unified `medicare-synth` CLI in `src/medicare_synth/cli.py` supporting `validate`, `scenario`, and `manifest` subcommands.
- Registered `[project.scripts] medicare-synth = "medicare_synth.cli:main"` in `pyproject.toml`.
- Added 12 new unit tests across `tests/test_scenarios.py`, `tests/test_normalizer.py`, and `tests/test_cli.py` (26 total passing tests).
- Completed Milestone 3 (Executable Model and Validation) across all deliverables.
- Implemented `ReleaseExporter`, `ReleaseManifest`, `FileReleaseEntry`, and `FidelityProfile` in `src/medicare_synth/release.py`.
- Supported multi-format export of dataset tables to CSV and Parquet formats with automatic SHA256 checksum calculation.
- Automated release bundle metadata generation (`release_manifest.json`, `validation_report.json`, `fidelity_profile.json`, `sql_reference_schema.sql`).
- Exposed `export` subcommand in `medicare-synth` CLI (`src/medicare_synth/cli.py`).
- Added package top-level exports in `src/medicare_synth/__init__.py`.
- Added unit test suite in `tests/test_release.py` (29 total passing unit tests).
- Completed Milestone 4 (Validation-First Release) across all deliverables.
- Implemented `TabDatSynthAdapter` and `VerticalExpander` in `src/medicare_synth/expansion.py` providing evidence-graded vertical feature synthesis.
- Implemented `HorizontalExpander` in `src/medicare_synth/expansion.py` providing connected-subgraph scaling with deterministic re-keying.
- Exposed `expand` subcommand in `medicare-synth` CLI (`src/medicare_synth/cli.py`).
- Added unit test suite in `tests/test_expansion.py` (33 total passing unit tests).
- Resolved linter warnings (`ruff`) and static type-checking issues (`pyright`).
- Completed Milestone 5 (Expansion and Scenarios) across all deliverables.
- Implemented `ScenarioCatalog` and `export_ci_fixtures` in `src/medicare_synth/catalog.py` for structured metadata and lightweight CI test fixtures.
- Implemented `SchemaDiffer` and `DiffReport` in `src/medicare_synth/diff.py` for annual snapshot schema diffing.
- Implemented `LimitationsProfile` and `LimitationsProfiler` in `src/medicare_synth/profile.py` for explicit 6-category limitations disclosure.
- Exposed `catalog`, `diff`, `profile`, and `export-ci` subcommands in `src/medicare_synth/cli.py`.
- Added executable cross-language reference examples in `examples/python_reference.py` and `examples/sql_reference.sql`.
- Added unit test suites in `tests/test_catalog.py`, `tests/test_diff.py`, and `tests/test_profile.py` (40 total passing unit tests).
- Completed Milestone 6 (Adoption and Maintenance) across all deliverables.




### Changed

- Replaced placeholder package metadata with the project description.
