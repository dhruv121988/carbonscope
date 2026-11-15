# CarbonScope 2.0 Official Data Quality & Integrity Audit
**Audited on:** `2026-11-13 10:34:49 UTC` | **Authority:** European Commission Joint Research Centre (EDGAR 2026)

## 1. Quality & Integrity Health Score

- **Overall Health Score:** **`99.88%`**
- **Duplicate Records:** `0` (Zero duplicates verified across all tables)
- **Temporal Continuity:** 56 Continuous Annual Intervals (`1970` to `2025`)
- **Physical Realism:** Gross emissions strictly non-negative (>= 0 Mt CO2eq)
- **Aggregate Isolation:** Sovereign nations segregated from composite entities (`EU27`, `GLOBAL TOTAL`)

## 2. Decadal Completeness Matrix

| Decade | Year Span | Total Observations | Valid Records | Completeness (%) |
|---|---|---|---|---|
| 1970-1979 (Decade 1) | 1970-1979 | 2,120 | 2,120 | **100.0%** |
| 1980-1989 (Decade 2) | 1980-1989 | 2,120 | 2,120 | **100.0%** |
| 1990-1999 (Decade 3) | 1990-1999 | 2,120 | 2,120 | **100.0%** |
| 2000-2009 (Decade 4) | 2000-2009 | 2,120 | 2,120 | **100.0%** |
| 2010-2019 (Decade 5) | 2010-2019 | 2,120 | 2,120 | **100.0%** |
| 2020-2025 (Decade 6) | 2020-2025 | 1,272 | 1,272 | **100.0%** |

## 3. Master Dataset Structural Statistics

- **Total Ingested Observations:** `11,872` records
- **Total Analytical Features:** `12` features
- **Total Null Values:** `4,784` (3.36% of cells, attributable to optional per-GDP series starting in 1990)

## 4. Transformations & Normalization Operations Performed

| Step | Transformation Performed | Records Affected |
|---|---|---|
| Drop Blank Rows | Removed fully null separator rows | 2 |
| Melt Totals Panel | Converted wide matrix (212 countries x 56 years) into long format | 11,872 |
| Melt Sectoral Panel | Processed 212 entities across 8 sectors | 271,936 |
| Drop Blank Rows | Removed fully null separator rows | 2 |
| Melt Totals Panel | Converted wide matrix (212 countries x 56 years) into long format | 11,872 |
| Assemble Master Panel | Merged totals, fossil CO2, per-capita, and per-GDP indicators into unified 11,872 record panel | 11,872 |

> [!NOTE]
> Raw source workbooks in `data/raw/` remain untouched. All cleaned panels are housed strictly in `data/processed/` with Parquet and CSV mirrors.
