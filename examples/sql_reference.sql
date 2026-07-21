-- Reference SQL DDL and Downstream Analytics for Medicare-Synth Releases
-- Target Compatibility: DuckDB, PostgreSQL, Snowflake, BigQuery

-- 1. Beneficiary Summary Table
CREATE TABLE IF NOT EXISTS beneficiary_summary (
    bene_id VARCHAR(15) PRIMARY KEY,
    bene_birth_dt DATE NOT NULL,
    bene_death_dt DATE,
    bene_sex_ident_cd VARCHAR(1) NOT NULL,
    bene_race_cd VARCHAR(1) NOT NULL
);

-- 2. Carrier Claims Line Item Table
CREATE TABLE IF NOT EXISTS carrier_claims (
    clm_id VARCHAR(15) NOT NULL,
    line_num INTEGER NOT NULL,
    bene_id VARCHAR(15) NOT NULL REFERENCES beneficiary_summary(bene_id),
    clm_from_dt DATE NOT NULL,
    clm_thru_dt DATE NOT NULL,
    prvdr_npi VARCHAR(10) NOT NULL,
    hcpcs_cd VARCHAR(5) NOT NULL,
    line_nch_pmt_amt DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (clm_id, line_num)
);

-- 3. Outpatient Claims Header Table
CREATE TABLE IF NOT EXISTS outpatient_claims (
    clm_id VARCHAR(15) PRIMARY KEY,
    bene_id VARCHAR(15) NOT NULL REFERENCES beneficiary_summary(bene_id),
    clm_from_dt DATE NOT NULL,
    clm_thru_dt DATE NOT NULL,
    provider_npi VARCHAR(10) NOT NULL,
    icd_diag_01 VARCHAR(7) NOT NULL,
    clm_pmt_amt DECIMAL(10, 2) NOT NULL
);

-- 4. Downstream Analytic Query: Per-Beneficiary Total Spend and Claim Frequency
SELECT 
    b.bene_id,
    b.bene_sex_ident_cd,
    COUNT(DISTINCT c.clm_id) AS total_carrier_claims,
    COALESCE(SUM(c.line_nch_pmt_amt), 0.00) AS total_carrier_spend,
    COUNT(DISTINCT o.clm_id) AS total_outpatient_claims,
    COALESCE(SUM(o.clm_pmt_amt), 0.00) AS total_outpatient_spend
FROM beneficiary_summary b
LEFT JOIN carrier_claims c ON b.bene_id = c.bene_id
LEFT JOIN outpatient_claims o ON b.bene_id = o.bene_id
GROUP BY b.bene_id, b.bene_sex_ident_cd;
