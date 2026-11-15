# CarbonScope 2.0: Official Data Dictionary & Dataset Audit (Phase 1)
**Data Source:** European Commission Joint Research Centre (JRC) - EDGAR 2026
**Citation:** Crippa, M., Guizzardi, D., Pagani, F., Banja, M., Ciarlantini, S. et al., *GHG emissions of all world countries - 2026 Report*, Publications Office of the European Union, Luxembourg, 2026, doi:10.2760/7717504, JRC147815.
**Official Portal:** [https://edgar.jrc.ec.europa.eu/report_2026](https://edgar.jrc.ec.europa.eu/report_2026)

## 1. Primary Dataset: EDGAR_2026_GHG_booklet_2026.xlsx
### Sheet: `GHG_totals_by_country`
- **Dimensions:** 214 rows x 58 columns
- **ID Columns:** `EDGAR Country Code`, `Country`
- **Temporal Range:** 1970 - 2025 (56 continuous years)
- **Missing Value Count:** 116 cells
- **Separator / Blank Rows:** 2 (Row indices: [210, 212])

  - **Geographic Entities:** 212 (includes sovereign nations, territories, and composite aggregations)
### Sheet: `GHG_by_sector_and_country`
- **Dimensions:** 4858 rows x 60 columns
- **ID Columns:** `Substance`, `Sector`, `EDGAR Country Code`, `Country`
- **Temporal Range:** 1970 - 2025 (56 continuous years)
- **Missing Value Count:** 5509 cells
- **Separator / Blank Rows:** 2 (Row indices: [4806, 4832])

  - **Substances Covered:** CO2, GWP_100_AR5_CH4, GWP_100_AR5_F-gases, GWP_100_AR5_N2O
  - **Sectors Covered:** Agriculture, Buildings, Fuel Production, Industrial Combustion, Power Industry, Processes, Transport, Waste
  - **Geographic Entities:** 212 (includes sovereign nations, territories, and composite aggregations)
### Sheet: `GHG_per_GDP_by_country`
- **Dimensions:** 212 rows x 38 columns
- **ID Columns:** `EDGAR Country Code`, `Country`
- **Temporal Range:** 1990 - 2025 (36 continuous years)
- **Missing Value Count:** 436 cells
- **Separator / Blank Rows:** 2 (Row indices: [208, 210])

  - **Geographic Entities:** 210 (includes sovereign nations, territories, and composite aggregations)
### Sheet: `GHG_per_capita_by_country`
- **Dimensions:** 212 rows x 58 columns
- **ID Columns:** `EDGAR Country Code`, `Country`
- **Temporal Range:** 1970 - 2025 (56 continuous years)
- **Missing Value Count:** 116 cells
- **Separator / Blank Rows:** 2 (Row indices: [208, 210])

  - **Geographic Entities:** 210 (includes sovereign nations, territories, and composite aggregations)
### Sheet: `LULUCF_macroregions`
- **Dimensions:** 98 rows x 39 columns
- **ID Columns:** `Substance`, `Sector`, `Macro-region`
- **Temporal Range:** 1990 - 2025 (36 continuous years)
- **Missing Value Count:** 117 cells
- **Separator / Blank Rows:** 3 (Row indices: [69, 80, 89])

  - **Substances Covered:** CO2, GWP_100_AR5_CH4, GWP_100_AR5_N2O, GWP_100_AR5_GHG
  - **Sectors Covered:** Deforestation, Fires, Forest Land, Organic Soil, Other Land, Africa, Australia, Japan, New Zealand, Eastern Asia, Eastern Europe and Central Asia, Europe, Latin America and Caribbean, Middle East, North America, South-East Asia and Pacific, Southern Asia, Net
### Sheet: `LULUCF_countries`
- **Dimensions:** 1291 rows x 41 columns
- **ID Columns:** `Substance`, `Sector`, `EDGAR Country Code`, `Country`, `Macro-region`
- **Temporal Range:** 1990 - 2025 (36 continuous years)
- **Missing Value Count:** 3547 cells
- **Separator / Blank Rows:** 3 (Row indices: [1069, 1273, 1282])

  - **Substances Covered:** CO2, GWP_100_AR5_CH4, GWP_100_AR5_N2O, GWP_100_AR5_GHG
  - **Sectors Covered:** Deforestation, Fires, Forest Land, Organic Soil, Other Land, Net
  - **Geographic Entities:** 203 (includes sovereign nations, territories, and composite aggregations)

## 2. Global Baseline & Top Emitting Nations (2025 Observation)

**Total Global GHG Emissions (2025):** **`54,149.17 Mt CO2eq`** (~54.15 Gt CO2eq)

| Rank | Country | EDGAR Code | 2025 Emissions (Mt CO2eq) | Global Share (%) |
|---|---|---|---|---|
| 1 | China | `CHN` | 15,980.97 | 29.51% |
| 2 | United States | `USA` | 6,018.30 | 11.11% |
| 3 | India | `IND` | 4,508.01 | 8.33% |
| 4 | Russia | `RUS` | 2,574.39 | 4.75% |
| 5 | Indonesia | `IDN` | 1,358.91 | 2.51% |
| 6 | Brazil | `BRA` | 1,306.59 | 2.41% |
| 7 | Iran | `IRN` | 1,119.32 | 2.07% |
| 8 | Japan | `JPN` | 1,063.13 | 1.96% |
| 9 | Saudi Arabia | `SAU` | 844.96 | 1.56% |
| 10 | Canada | `CAN` | 764.52 | 1.41% |

## 3. India's Historical GHG Trajectory

- **1970 Emissions:** `702.40 Mt CO2eq`
- **1990 Emissions:** `1,319.81 Mt CO2eq`
- **2000 Emissions:** `1,805.93 Mt CO2eq`
- **2010 Emissions:** `2,709.07 Mt CO2eq`
- **2020 Emissions:** `3,463.07 Mt CO2eq` (Lockdown dip)
- **2025 Emissions:** `4,508.01 Mt CO2eq`
- **55-Year Annualized Growth Rate (CAGR):** `+3.44%`
- **Current Global Contribution (2025):** `8.33%`

### India Sectoral Distribution (2025 Snapshot)

| Sector | 2025 Emissions (Mt CO2eq) | National Sector Share (%) |
|---|---|---|
| Power Industry | 1,571.65 | 34.86% |
| Agriculture | 834.17 | 18.50% |
| Industrial Combustion | 681.77 | 15.12% |
| Processes | 411.03 | 9.12% |
| Transport | 381.70 | 8.47% |
| Buildings | 250.30 | 5.55% |
| Fuel Production | 218.71 | 4.85% |
| Waste | 158.68 | 3.52% |

## 4. Secondary Dataset: EDGAR_2026_GHG_booklet_2026_fossilCO2only.xlsx

**Sheets Included:** `info`, `Citations and references`, `fossil_CO2_totals_by_country`, `fossil_CO2_by_sector_country_su`, `fossil_CO2_per_GDP_by_country`, `fossil_CO2_per_capita_by_countr`

> [!IMPORTANT]
> **Scientific Distinction:** The GHG booklet includes all Kyoto gases aggregated via GWP-100 AR5 (`CO2`, `CH4`, `N2O`, `F-gases`), whereas the Fossil CO2 booklet isolates strictly fossil-fuel combustion and industrial carbonate decomposition CO2. Neither represents atmospheric concentrations (ppm), but rather annual mass flows (`Mt CO2eq/yr`).

## 5. Official Report PDF: `GHG_emissions_of_all_world_countries_booklet_2026report.pdf`

- **Total Document Pages:** 301
- **Publisher:** Publications Office of the European Union, Luxembourg, JRC147815
- **GWP Standards:** IPCC AR5 (Fourth Assessment Report GWP-100 values: CO2=1, CH4=28, N2O=265)
- **Report Purpose:** Authoritative global benchmark utilized for UNFCCC COP compliance, national decarbonization verification, and international climate pledges.

## 6. Supported vs Unsupported Analyses Assessment

### Supported Analyses (Genuinely backed by EDGAR 2026 observations):
1. **Continuous 56-Year Historical Trajectories (1970 - 2025):** 208 sovereign nations and territories.
2. **Granular Sector Decomposition:** 8 primary economic sectors (Power, Transport, Industrial Combustion, Agriculture, Processes, Buildings, Fuel Production, Waste).
3. **Multi-Gas Substance Breakdown:** CO2, CH4, N2O, and Fluorinated Gases (F-gases) in IPCC AR5 CO2-equivalent metrics.
4. **Macroeconomic Emission Intensity:** Emissions per GDP (PPP) from 1990 to 2025 (`t CO2eq/kUSD/yr`).
5. **Per Capita Footprint:** Emissions per person from 1970 to 2025 (`t CO2eq/cap/yr`).
6. **LULUCF Separate Accounting:** Forest land, organic soils, deforestation, and wildfires from 1990 to 2025.
7. **India Focused Deep-Dive:** Complete historical sector, gas, per-capita, and per-GDP data.
8. **Supervised Regression Forecasting:** Chronological sequence forecasting (1970-2015 train, 2016-2025 test) using lag features, rolling statistics, momentum, and growth trends.
9. **Anomaly Detection:** Outlier detection using Isolation Forest and Statistical Z-Scores on historical emissions, annual delta swings, and structural shocks (e.g. 1991 Soviet collapse, 2008 global financial crisis, 2020 COVID-19 pandemic deflection).
10. **Explainable AI:** SHAP tree/kernel explainer to decode model weights and feature importances for future predictions.
11. **Hypothetical What-If Scenario Simulations:** Simulating adjustments to sector emission inputs, growth rates, and efficiency pathways to predict trajectory divergence.

### Unsupported Analyses (Do NOT fabricate or attempt):
1. **Atmospheric Concentrations:** EDGAR measures emission flux (emissions generated at source, Mt CO2eq/yr), NOT ambient atmospheric concentration (ppm) measured at Mauna Loa or by satellites.
2. **Monthly / Daily Real-Time Sensor Telemetry:** EDGAR is an annual national inventory with robust international accounting; daily/monthly data does not exist in this database.
3. **Scope 1 / Scope 2 / Scope 3 Corporate Disclosures:** EDGAR is a geographical territorial inventory, not a corporate GHG Protocol disclosure for individual private companies.
4. **Post-2025 Real Observations:** The latest recorded historical observation in the EDGAR 2026 release is 2025. All post-2025 values MUST be generated strictly by our ML forecasting models and clearly labeled as forecasts.
