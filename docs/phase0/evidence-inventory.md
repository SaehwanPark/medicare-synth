# Phase 0 — Initial evidence inventory

**Status:** Scouting inventory (2026-11-06); **not** a frozen Phase 3 corpus
**MVP hook:** 2021 OM FFS, age 65+, diabetes (± HF) → all-cause IP hospitalization
**Persistence copy:** `~/data/medicare-synth/phase0/evidence-inventory.json`

Items below are candidates for later Evidence IR formalization. Inclusion here
does **not** approve them as calibration targets. Values cited from public
summaries are for scouting orientation; re-extract from primary sources with
anchors before Phase 3 freeze.

## 1. Screening criteria (Phase 0)

Prefer, in order:

1. Official CMS / CCW / HHS aggregate products with clear Medicare FFS
   denominators.
2. Medicare-only published analyses (FFS or explicit FFS subgroup) with
   stated years, eligibility, and estimands.
3. Reject or quarantine mixed all-payer, MA-only, or non-Medicare populations
   unless a transport rule is explicit.

Grade each item: **A** (near-compatible), **B** (usable with documented
approximation), **C** (diagnostic / conflict / year-skewed), **X** (ineligible).

## 2. Official CMS / HHS aggregates

| ID | Source | What it offers | Year / pop | MVP use | Grade | Comparability notes |
| --- | --- | --- | --- | --- | --- | --- |
| **CMS-AGG-01** | [Medicare Beneficiaries at a Glance DY2021](https://data.cms.gov/sites/default/files/2023-09/Medicare%20Beneficiaries%20at%20a%20Glance%20DY2021.pdf) | National chronic-condition prevalence ranks; diabetes and heart failure among top conditions; FFS vs MA enrollment split | 2021; FFS footnote for chronic prevalence | Context for prevalence order of magnitude; enrollment mix | **B** | Chart-level; exact diabetes/HF percentages need careful PDF extraction; prevalence based on FFS beneficiaries per footnote |
| **CMS-AGG-02** | [Mapping Medicare Disparities (MMD) Tool](https://data.cms.gov/mmd-population/map.html) + [technical documentation](https://www.cms.gov/about-cms/agency-information/omh/downloads/mapping-technical-documentation.pdf) | County/state **prevalence** and condition-specific **hospitalization rates** for diabetes/HF etc.; FFS vs MA views; age/sex/race/dual stratifiers | Multi-year; 2021+ uses updated CCW 30-condition algorithms; FFS excludes any MA enrollment during year | **Prevalence:** primary official source (grade A). **Condition hospitalization:** DX-based — **not** an O1 (all-cause) target | **A** (prevalence) / **B–diagnostic** (condition hosp) | Condition-hosp rates need IP ICD (O4); quarantine for MVP O1. Denominator includes under-65 unless filtered; geography needed for county targets; download CSV for pinned extracts |
| **CMS-AGG-03** | CMS OMH [Diabetes disparities data highlight (2021)](https://www.cms.gov/files/document/diabetes-disparities-data-highlight-2021.pdf) | Medicare FFS diabetes prevalence trends (~27.7% in 2018 cited); disparities; ED/IP utilization for diabetes complications | Mostly **2017** CCW FFS; ages 18–75 subsets for some measures | Train candidate for prevalence disparities; utilization needs algorithm match | **B** | Year ≠ 2021; HEDIS-ish diabetes defs for some measures; SDOH neighborhood covariates out of MVP schema |
| **CMS-AGG-04** | CMS OMH [Heart Failure disparities snapshot](https://www.cms.gov/About-CMS/Agency-Information/OMH/Downloads/Data-Snapshot-Heart-Failure.pdf) (Jan 2024) | HF prevalence ~12% among Medicare FFS (2022 MMD, preliminary); hospitalization rate variation by demographics | **2022** FFS (preliminary in source) | HF prevalence / hosp rate orientation | **B** | Year ≠ 2021; preliminary flag; age-standardized for some strata |
| **CMS-AGG-05** | [CCW 27→30 condition transition impact](https://www2.ccwdata.org/documents/10280/19002256/ccw-condition-categories-impact-of-transition-from-27-to-30.pdf) | Documents algorithm break: e.g. heart failure 14.4% (27-CCW) vs 12.1% (30-CCW) in **2017**; diabetes unchanged at 28.0% | 2017 FFS | **Mandatory comparability control** when mixing pre/post algorithm evidence | **A** (meta) | Not a calibration target; required when interpreting HF time series |
| **CMS-AGG-06** | [CCW technical guidance: population statistics](https://www2.ccwdata.org/documents/10280/19002248/ccw-technical-guidance-calculating-medicare-population-statistics.pdf) | Official rules for prevalence denominators, FFS restrictions, lookbacks | Method | Cohort rule reference | **A** (method) | Align MVP Option B default and Option C upgrade language to this guidance where possible |
| **CMS-AGG-07** | Medicare Geographic Variation / Chronic Conditions public aggregates (CMS Research Statistics) | State/county spending, utilization, chronic condition prevalence for FFS | Multi-year (verify file vintage) | Secondary national/state marginals | **B** | Confirm exact 2021 file URL and dictionary before pinning; site paths change |
| **CMS-AGG-08** | CMS Market Saturation & Utilization (referenced by MMD docs) | Provider density vs FFS beneficiaries | Recent releases | Out of MVP core | **C** | Provider-side; not needed for first estimand |

### Suggested first official calibration triad (not frozen)

1. **National FFS diabetes prevalence, age 65+** (MMD or Chronic Conditions
   extract for 2021, age-filtered) — population/condition.
2. **National FFS all-cause IP admission risk/rate among diabetes+**, age 65+
   — utilization; prefer a source whose estimand matches **O1** (or document
   transport). Do **not** substitute MMD diabetes-condition hospitalization
   rates for O1 without an IP ICD path.
3. **National FFS heart-failure prevalence, age 65+** (MMD 2021) — secondary
   condition marginal.

Hold out a disjoint demographic stratum or adjacent year for Phase 3/6 — do
**not** pick the holdout numerically during Phase 0 beyond naming the intent.

## 3. Medicare-only research findings (sample)

| ID | Citation | Estimand sketch | Population | MVP use | Grade | Issues |
| --- | --- | --- | --- | --- | --- | --- |
| **LIT-01** | CMS/AHRQ Data Points: [*Use of and access to health care by Medicare beneficiaries with diabetes… 2007–2011*](https://www.ncbi.nlm.nih.gov/books/NBK202115/) | Diabetes prevalence ~25% (2011); hospitalization rates per 100 beneficiaries by diabetes type/insulin (e.g. 43–111) | Medicare FFS, age ≥65, full-year A+B, no MA | Prototype rate-by-subgroup estimand; shows need for insulin/type detail we lack | **B** | Years old; type/insulin strata need PDE + DX we may not have |
| **LIT-02** | Drye et al., *Med Care* — [Risk-standardized acute admission rates… diabetes and HF](https://pmc.ncbi.nlm.nih.gov/articles/PMC5356461/) | Crude national acute **unplanned** admission rate **41.4 per 100 person-years** (diabetes cohort, 2012); HF cohort parallel | Medicare FFS ≥65 with diabetes or HF; ACO context | Related person-time admission-rate prior for formalization; **not** equivalent to MVP O1 (all-cause claim presence) | **B** | 2012; year transport; planned-admission exclusions (~12% of stays) absent from O1; ACO framing |
| **LIT-03** | CDC MMWR: [Diabetes prevalence and incidence among Medicare beneficiaries, 2001–2015](https://www.cdc.gov/mmwr/volumes/68/wr/mm6843a2.htm) | FFS diabetes prevalence trajectory to ~31.6% (2015); incidence | FFS A+B continuous enrollment; age ≥68 end of index year | Prevalence trend prior; age-68+ lookback rule differs from MVP 65+ | **B** | Age cutoff and 60-month enrollment window; year ≤2015 |
| **LIT-04** | Schneider et al., *Health Qual Life Outcomes* 2009 — multiple chronic conditions in Medicare | Diabetes ~24.3%; HF ~18%; inpatient days by condition (2005) | Medicare FFS | Historical multi-morbidity context | **C** | Old year; HF def pre-algorithm shifts |
| **LIT-05** | McBean et al., *Diabetes Care* 2004 — racial/ethnic diabetes prevalence/incidence/mortality | Prevalence per 1,000 by race among FFS ≥67 | FFS 5% sample | Disparity pattern prior | **C** | Very old; race coding changes |
| **LIT-06** | Jencks et al., *NEJM* 2009 — rehospitalizations among Medicare FFS | Rehospitalization rates; HF among high-readmission conditions | Medicare FFS | Classic utilization; **readmission** estimand (episode logic) | **C** for MVP v0 | Needs 30-day episode construction beyond first-admission O1 |
| **LIT-07** | Avalere white paper: [Comparing Detection, Treatment, Outcomes… MA vs FFS diabetes](https://advisory.avalerehealth.com/wp-content/uploads/2023/01/Diabetes-Progression-Whitepaper.pdf) | FFS chronic diabetes post-index IP ~13%; diabetes-principal IP rare (~0.6%) | Matched MA/FFS | Warns diabetes-principal admissions are rare; supports all-cause O1 over O4 for MVP | **B** (diagnostic) | Industry report; MA comparison; not peer-reviewed CMS |

## 4. Expressible MVP analysis (ties inventory → schema)

**Candidate executable finding (Phase 2 target, not yet formalized):**

> Among Medicare FFS beneficiaries aged ≥65 with CCW/MBSF diabetes indicator
> present, diabetes prevalence in FFS elderly populations is on the order of
> ~25–32% depending on year and algorithm (CMS-AGG / LIT-01 / LIT-03). A
> related—but not identical—person-time acute unplanned admission rate among
> diabetes cohorts is on the order of tens per 100 person-years (LIT-02,
> 2012; requires transport and planned-admission gap notes vs MVP O1).

Implementation path on Medicare-Synth tables: cohort filters in
[mvp-cohort-and-fields.md](mvp-cohort-and-fields.md) + outcome **O1** or
person-time rate from claim counts. No IP principal diagnosis required for O1.

## 5. Known comparability hazards (must not ignore)

| Hazard | Why it matters | Mitigation |
| --- | --- | --- |
| **CCW 27 vs 30 algorithms** | HF prevalence shifts ~2+ points; other conditions move more; diabetes stable in 2017 CCW study | Pin algorithm family on every evidence record; prefer post-transition sources for HF |
| **Year ≠ 2021** | Care patterns and coding (ICD-9→10) drift | Prefer 2019–2021 aggregates; label older literature as transport-required |
| **Age cutoffs** | 65+ vs 67+ vs 68+ vs 18–75 | Filter MMD/CCW extracts; reject silent pooling |
| **MA exclusion rules** | Any MA month vs full-year FFS vs hybrid | Align to CMS-AGG-06 / MMD docs; record Option A/B/C |
| **Denominator (beneficiaries vs person-years)** | Rates not interchangeable with binary annual risks | Separate estimand types in IR |
| **All-cause vs condition-specific admissions** | Schema lacks IP DX; literature often mixes | MVP uses all-cause; quarantine DX-specific until fields exist |
| **Overlapping source populations** | MMD, Chronic Conditions dashboard, and many papers draw from CCW 100% FFS | Treat as dependent evidence; do not assume independent likelihoods in calibration |
| **Preliminary MMD years** | HF snapshot flags 2022 preliminary | Prefer finalized extracts; note provisional status |
| **Synthetic baseline ≠ evidence** | CMS Syn Claims fixtures are not calibration targets | Never fit to scenario fixture marginals as if Medicare |

No hazard above is treated as silently fatal to the all-cause diabetes→IP MVP.
A **fatal** issue would be: no way to define FFS-like eligibility, no chronic
flag, and no hospitalization signal — which is not the case.

## 6. Conflicts and overlaps to retain (do not delete)

- Diabetes prevalence “~25%” (LIT-01, 2011) vs “~28%” (CCW 2017) vs
  “~31.6%” (MMWR 2015, age ≥68 continuous) vs At-a-Glance chart ranks
  (CMS-AGG-01) — expect band, not a single truth.
- HF “~18%” (LIT-04, 2005) vs “~12–14%” (CCW 27/30, 2017) vs “~12%”
  (CMS-AGG-04, 2022) — algorithm + year dominate.
- Admission “per 100 beneficiaries” (LIT-01) vs “per 100 person-years”
  (LIT-02) — different estimands.

## 7. Proposed roles (preview for Phase 3; not frozen)

| Role | Candidate |
| --- | --- |
| Training / calibration | CMS-AGG-02 diabetes prevalence 65+ (2021); optional LIT-02-scale rate only with explicit estimand/transport notes — **not** MMD condition-hospitalization as O1 |
| Held-out | Demographic stratum (e.g. sex-specific diabetes prevalence) or adjacent-year MMD **prevalence** slice — **choose at Phase 3 freeze** |
| Diagnostic-only | CMS-AGG-05 algorithm impact; MMD condition-hospitalization; LIT-07 DX-specific rarity; LIT-06 readmissions |

## 8. Acquisition notes for `~/data/medicare-synth/phase0/`

Persist downloaded CSVs/PDFs and the JSON inventory sidecar **outside git**
under the home data directory with retrieval date and URL. This markdown file
is the in-repo inventory; do not commit CMS bulk extracts to the repository.
