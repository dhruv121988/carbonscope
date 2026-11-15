"""
CarbonScope 2.0 - Data Cleaner & Normalization Engine
Transforms raw EDGAR wide matrices (1970-2025) into clean, tidy analytical panels.
Maintains separate raw and processed storage without destructive in-place modification.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from src.data_acquisition.data_loader import loader
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

AGGREGATE_ENTITIES = [
    "GLOBAL TOTAL",
    "EU27",
    "International Aviation",
    "International Shipping"
]

SUBSTANCE_MAP = {
    "CO2": "Fossil CO2",
    "GWP_100_AR5_CH4": "Methane (CH4, AR5 CO2eq)",
    "GWP_100_AR5_N2O": "Nitrous Oxide (N2O, AR5 CO2eq)",
    "GWP_100_AR5_F-gases": "Fluorinated Gases (F-gases, AR5 CO2eq)"
}


class DataCleaner:
    """Orchestrates standardizing, reshaping, and archiving EDGAR climate datasets."""

    def __init__(self):
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        self.transformation_log: List[Dict[str, Any]] = []

    def _log_transformation(self, step: str, details: str, records_affected: int = 0):
        self.transformation_log.append({
            "step": step,
            "details": details,
            "records_affected": records_affected
        })

    def clean_ghg_totals(self) -> pd.DataFrame:
        """
        Clean and reshape GHG totals by country from wide to long/tidy format.
        Preserves original country names, tags aggregate regions, and standardizes columns.
        """
        df_raw = loader.load_ghg_totals()
        init_rows = len(df_raw)

        # 1. Remove completely blank rows
        df = df_raw.dropna(how="all").copy()
        dropped_blank = init_rows - len(df)
        self._log_transformation("Drop Blank Rows", "Removed fully null separator rows", dropped_blank)

        # 2. Filter out rows where Country is missing
        df = df[df["Country"].notnull()].copy()

        # 3. Identify identifier vs year columns
        year_cols = [c for c in df.columns if str(c).isdigit()]
        id_cols = [c for c in df.columns if c not in year_cols]

        # 4. Melt wide to tidy long format
        df_tidy = pd.melt(
            df,
            id_vars=id_cols,
            value_vars=year_cols,
            var_name="Year",
            value_name="Emissions_MtCO2eq"
        )

        # 5. Type casting and sanitization
        df_tidy["Year"] = df_tidy["Year"].astype(int)
        df_tidy["Emissions_MtCO2eq"] = pd.to_numeric(df_tidy["Emissions_MtCO2eq"], errors="coerce")
        df_tidy["Country_Raw"] = df_tidy["Country"].astype(str)
        df_tidy["Country"] = df_tidy["Country"].astype(str).str.strip()
        df_tidy["EDGAR_Code"] = df_tidy["EDGAR Country Code"].astype(str).str.strip()

        # 6. Flag aggregate entities
        df_tidy["Is_Aggregate"] = df_tidy["Country"].isin(AGGREGATE_ENTITIES)
        df_tidy["Unit"] = "Mt CO2eq/yr"

        # Select and reorder columns
        final_cols = ["Country", "Country_Raw", "EDGAR_Code", "Year", "Emissions_MtCO2eq", "Unit", "Is_Aggregate"]
        df_tidy = df_tidy[final_cols].sort_values(by=["Country", "Year"]).reset_index(drop=True)

        self._log_transformation(
            "Melt Totals Panel",
            f"Converted wide matrix ({len(df)} countries x {len(year_cols)} years) into long format",
            len(df_tidy)
        )

        # Save to processed directory
        df_tidy.to_parquet(os.path.join(PROCESSED_DIR, "ghg_totals_tidy.parquet"), index=False)
        df_tidy.to_csv(os.path.join(PROCESSED_DIR, "ghg_totals_tidy.csv"), index=False)

        return df_tidy

    def clean_ghg_sectors(self) -> pd.DataFrame:
        """
        Clean and reshape GHG emissions by sector, country, and substance.
        """
        df_raw = loader.load_ghg_sectors()
        df = df_raw.dropna(how="all").copy()
        df = df[df["Country"].notnull() & df["Sector"].notnull()].copy()

        year_cols = [c for c in df.columns if str(c).isdigit()]
        id_cols = [c for c in df.columns if c not in year_cols]

        df_tidy = pd.melt(
            df,
            id_vars=id_cols,
            value_vars=year_cols,
            var_name="Year",
            value_name="Emissions_MtCO2eq"
        )

        df_tidy["Year"] = df_tidy["Year"].astype(int)
        df_tidy["Emissions_MtCO2eq"] = pd.to_numeric(df_tidy["Emissions_MtCO2eq"], errors="coerce").fillna(0.0)
        df_tidy["Country_Raw"] = df_tidy["Country"].astype(str)
        df_tidy["Country"] = df_tidy["Country"].astype(str).str.strip()
        df_tidy["EDGAR_Code"] = df_tidy["EDGAR Country Code"].astype(str).str.strip()
        df_tidy["Sector_Raw"] = df_tidy["Sector"].astype(str)
        df_tidy["Sector"] = df_tidy["Sector"].astype(str).str.strip()
        df_tidy["Substance_Raw"] = df_tidy["Substance"].astype(str)
        df_tidy["Substance"] = df_tidy["Substance_Raw"].map(lambda x: SUBSTANCE_MAP.get(x, x))

        df_tidy["Is_Aggregate"] = df_tidy["Country"].isin(AGGREGATE_ENTITIES)
        df_tidy["Unit"] = "Mt CO2eq/yr"

        final_cols = [
            "Country", "Country_Raw", "EDGAR_Code", "Sector", "Sector_Raw",
            "Substance", "Substance_Raw", "Year", "Emissions_MtCO2eq", "Unit", "Is_Aggregate"
        ]
        df_tidy = df_tidy[final_cols].sort_values(by=["Country", "Sector", "Substance", "Year"]).reset_index(drop=True)

        self._log_transformation(
            "Melt Sectoral Panel",
            f"Processed {df_tidy['Country'].nunique()} entities across {df_tidy['Sector'].nunique()} sectors",
            len(df_tidy)
        )

        df_tidy.to_parquet(os.path.join(PROCESSED_DIR, "ghg_sectors_tidy.parquet"), index=False)
        df_tidy.to_csv(os.path.join(PROCESSED_DIR, "ghg_sectors_tidy.csv"), index=False)

        return df_tidy

    def clean_ghg_per_capita(self) -> pd.DataFrame:
        """Clean and reshape per-capita emissions (t CO2eq/cap/yr)."""
        df_raw = loader.load_ghg_per_capita()
        df = df_raw.dropna(how="all").copy()
        df = df[df["Country"].notnull()].copy()

        year_cols = [c for c in df.columns if str(c).isdigit()]
        id_cols = [c for c in df.columns if c not in year_cols]

        df_tidy = pd.melt(
            df,
            id_vars=id_cols,
            value_vars=year_cols,
            var_name="Year",
            value_name="Emissions_Per_Capita_tCO2eq"
        )

        df_tidy["Year"] = df_tidy["Year"].astype(int)
        df_tidy["Emissions_Per_Capita_tCO2eq"] = pd.to_numeric(df_tidy["Emissions_Per_Capita_tCO2eq"], errors="coerce")
        df_tidy["Country"] = df_tidy["Country"].astype(str).str.strip()
        df_tidy["EDGAR_Code"] = df_tidy["EDGAR Country Code"].astype(str).str.strip()
        df_tidy["Is_Aggregate"] = df_tidy["Country"].isin(AGGREGATE_ENTITIES)
        df_tidy["Unit"] = "t CO2eq/cap/yr"

        final_cols = ["Country", "EDGAR_Code", "Year", "Emissions_Per_Capita_tCO2eq", "Unit", "Is_Aggregate"]
        df_tidy = df_tidy[final_cols].sort_values(by=["Country", "Year"]).reset_index(drop=True)

        df_tidy.to_parquet(os.path.join(PROCESSED_DIR, "ghg_per_capita_tidy.parquet"), index=False)
        return df_tidy

    def clean_ghg_per_gdp(self) -> pd.DataFrame:
        """Clean and reshape emission intensity per GDP (t CO2eq/kUSD/yr)."""
        df_raw = loader.load_ghg_per_gdp()
        df = df_raw.dropna(how="all").copy()
        df = df[df["Country"].notnull()].copy()

        year_cols = [c for c in df.columns if str(c).isdigit()]
        id_cols = [c for c in df.columns if c not in year_cols]

        df_tidy = pd.melt(
            df,
            id_vars=id_cols,
            value_vars=year_cols,
            var_name="Year",
            value_name="Emissions_Per_GDP_tCO2eq_per_kUSD"
        )

        df_tidy["Year"] = df_tidy["Year"].astype(int)
        df_tidy["Emissions_Per_GDP_tCO2eq_per_kUSD"] = pd.to_numeric(df_tidy["Emissions_Per_GDP_tCO2eq_per_kUSD"], errors="coerce")
        df_tidy["Country"] = df_tidy["Country"].astype(str).str.strip()
        df_tidy["EDGAR_Code"] = df_tidy["EDGAR Country Code"].astype(str).str.strip()
        df_tidy["Is_Aggregate"] = df_tidy["Country"].isin(AGGREGATE_ENTITIES)
        df_tidy["Unit"] = "t CO2eq/kUSD/yr"

        final_cols = ["Country", "EDGAR_Code", "Year", "Emissions_Per_GDP_tCO2eq_per_kUSD", "Unit", "Is_Aggregate"]
        df_tidy = df_tidy[final_cols].sort_values(by=["Country", "Year"]).reset_index(drop=True)

        df_tidy.to_parquet(os.path.join(PROCESSED_DIR, "ghg_per_gdp_tidy.parquet"), index=False)
        return df_tidy

    def clean_fossil_co2_totals(self) -> pd.DataFrame:
        """Clean and reshape fossil CO2 totals."""
        df_raw = loader.load_fossil_co2_totals()
        df = df_raw.dropna(how="all").copy()
        df = df[df["Country"].notnull()].copy()

        year_cols = [c for c in df.columns if str(c).isdigit()]
        id_cols = [c for c in df.columns if c not in year_cols]

        df_tidy = pd.melt(
            df,
            id_vars=id_cols,
            value_vars=year_cols,
            var_name="Year",
            value_name="Fossil_CO2_Mt"
        )

        df_tidy["Year"] = df_tidy["Year"].astype(int)
        df_tidy["Fossil_CO2_Mt"] = pd.to_numeric(df_tidy["Fossil_CO2_Mt"], errors="coerce")
        df_tidy["Country"] = df_tidy["Country"].astype(str).str.strip()
        df_tidy["EDGAR_Code"] = df_tidy["EDGAR Country Code"].astype(str).str.strip()
        df_tidy["Is_Aggregate"] = df_tidy["Country"].isin(AGGREGATE_ENTITIES)
        df_tidy["Unit"] = "Mt CO2/yr"

        final_cols = ["Country", "EDGAR_Code", "Year", "Fossil_CO2_Mt", "Unit", "Is_Aggregate"]
        df_tidy = df_tidy[final_cols].sort_values(by=["Country", "Year"]).reset_index(drop=True)

        df_tidy.to_parquet(os.path.join(PROCESSED_DIR, "fossil_co2_totals_tidy.parquet"), index=False)
        return df_tidy

    def build_master_panel(self) -> pd.DataFrame:
        """
        Merge totals, per capita, per GDP, and fossil CO2 onto a unified panel.
        Creates data/processed/master_emissions_panel.parquet.
        """
        totals = self.clean_ghg_totals()
        fossil = self.clean_fossil_co2_totals()
        per_cap = self.clean_ghg_per_capita()
        per_gdp = self.clean_ghg_per_gdp()

        # Join on Country and Year
        master = totals.merge(
            fossil[["Country", "Year", "Fossil_CO2_Mt"]],
            on=["Country", "Year"],
            how="left"
        )

        master = master.merge(
            per_cap[["Country", "Year", "Emissions_Per_Capita_tCO2eq"]],
            on=["Country", "Year"],
            how="left"
        )

        master = master.merge(
            per_gdp[["Country", "Year", "Emissions_Per_GDP_tCO2eq_per_kUSD"]],
            on=["Country", "Year"],
            how="left"
        )

        # Compute non-CO2 share where available
        master["Non_CO2_GHG_MtCO2eq"] = master["Emissions_MtCO2eq"] - master["Fossil_CO2_Mt"]
        master["Non_CO2_Share_Pct"] = (master["Non_CO2_GHG_MtCO2eq"] / master["Emissions_MtCO2eq"] * 100).clip(lower=0, upper=100)

        master.to_parquet(os.path.join(PROCESSED_DIR, "master_emissions_panel.parquet"), index=False)
        master.to_csv(os.path.join(PROCESSED_DIR, "master_emissions_panel.csv"), index=False)

        self._log_transformation(
            "Assemble Master Panel",
            f"Merged totals, fossil CO2, per-capita, and per-GDP indicators into unified {len(master):,} record panel",
            len(master)
        )
        return master

    def run_all(self) -> Dict[str, Any]:
        """Execute full cleaning and transformation pipeline."""
        t = self.clean_ghg_totals()
        s = self.clean_ghg_sectors()
        pc = self.clean_ghg_per_capita()
        pg = self.clean_ghg_per_gdp()
        fc = self.clean_fossil_co2_totals()
        m = self.build_master_panel()

        return {
            "totals_records": len(t),
            "sectors_records": len(s),
            "per_capita_records": len(pc),
            "per_gdp_records": len(pg),
            "fossil_totals_records": len(fc),
            "master_panel_records": len(m),
            "transformations": self.transformation_log
        }


cleaner = DataCleaner()

if __name__ == "__main__":
    print("Executing full data cleaning pipeline...")
    res = cleaner.run_all()
    print("Cleaned datasets generated successfully!")
    print("Master panel rows:", res["master_panel_records"])
    print("Sector panel rows:", res["sectors_records"])
