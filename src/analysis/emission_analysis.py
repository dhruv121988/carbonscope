"""
CarbonScope 2.0 - Exploratory Data Analysis & Emission Analytics Engine
Computes global benchmarks, national comparisons, sectoral distributions,
gas breakdowns, and macroeconomic emission intensities.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


class EmissionAnalyzer:
    """Analytical engine for computing climate intelligence metrics across EDGAR 2026 data."""

    def __init__(self):
        self.master_path = os.path.join(PROCESSED_DIR, "master_emissions_panel.parquet")
        self.sectors_path = os.path.join(PROCESSED_DIR, "ghg_sectors_tidy.parquet")
        self._master_df: Optional[pd.DataFrame] = None
        self._sectors_df: Optional[pd.DataFrame] = None

    @property
    def master_df(self) -> pd.DataFrame:
        if self._master_df is None:
            if not os.path.exists(self.master_path):
                from src.preprocessing.cleaner import cleaner
                cleaner.run_all()
            self._master_df = pd.read_parquet(self.master_path)
        return self._master_df

    @property
    def sectors_df(self) -> pd.DataFrame:
        if self._sectors_df is None:
            if not os.path.exists(self.sectors_path):
                from src.preprocessing.cleaner import cleaner
                cleaner.run_all()
            self._sectors_df = pd.read_parquet(self.sectors_path)
        return self._sectors_df

    def get_global_overview_metrics(self, year: int = 2025) -> Dict[str, Any]:
        """Compute headline overview metrics for a given calendar year."""
        m = self.master_df

        # Global total
        glob = m[(m["Country"] == "GLOBAL TOTAL") & (m["Year"] == year)]
        glob_prev = m[(m["Country"] == "GLOBAL TOTAL") & (m["Year"] == year - 1)]

        glob_val = float(glob["Emissions_MtCO2eq"].values[0]) if len(glob) > 0 else 0.0
        glob_prev_val = float(glob_prev["Emissions_MtCO2eq"].values[0]) if len(glob_prev) > 0 else 0.0
        glob_yoy = ((glob_val - glob_prev_val) / glob_prev_val * 100) if glob_prev_val > 0 else 0.0

        # India metrics
        ind = m[(m["Country"] == "India") & (m["Year"] == year)]
        ind_prev = m[(m["Country"] == "India") & (m["Year"] == year - 1)]

        ind_val = float(ind["Emissions_MtCO2eq"].values[0]) if len(ind) > 0 else 0.0
        ind_prev_val = float(ind_prev["Emissions_MtCO2eq"].values[0]) if len(ind_prev) > 0 else 0.0
        ind_yoy = ((ind_val - ind_prev_val) / ind_prev_val * 100) if ind_prev_val > 0 else 0.0
        ind_share = (ind_val / glob_val * 100) if glob_val > 0 else 0.0

        ind_cap = float(ind["Emissions_Per_Capita_tCO2eq"].values[0]) if len(ind) > 0 and pd.notnull(ind["Emissions_Per_Capita_tCO2eq"].values[0]) else None
        ind_gdp = float(ind["Emissions_Per_GDP_tCO2eq_per_kUSD"].values[0]) if len(ind) > 0 and pd.notnull(ind["Emissions_Per_GDP_tCO2eq_per_kUSD"].values[0]) else None

        # Sovereign nations count
        sovereign_count = m[(~m["Is_Aggregate"]) & (m["Year"] == year)]["Country"].nunique()

        return {
            "year": year,
            "global_total_mt": round(glob_val, 2),
            "global_total_gt": round(glob_val / 1000.0, 2),
            "global_yoy_pct": round(glob_yoy, 2),
            "india_total_mt": round(ind_val, 2),
            "india_total_gt": round(ind_val / 1000.0, 2),
            "india_yoy_pct": round(ind_yoy, 2),
            "india_global_share_pct": round(ind_share, 2),
            "india_per_capita": round(ind_cap, 2) if ind_cap else None,
            "india_per_gdp": round(ind_gdp, 3) if ind_gdp else None,
            "monitored_countries": sovereign_count,
            "historical_timespan": "1970 - 2025 (56 Years)"
        }

    def get_top_emitting_countries(self, year: int = 2025, top_n: int = 10) -> pd.DataFrame:
        """Return the top N sovereign emitting nations for a specific year."""
        m = self.master_df
        sub = m[(~m["Is_Aggregate"]) & (m["Year"] == year)].copy()
        sub = sub.sort_values(by="Emissions_MtCO2eq", ascending=False).head(top_n)

        glob = m[(m["Country"] == "GLOBAL TOTAL") & (m["Year"] == year)]["Emissions_MtCO2eq"].values[0]
        sub["Global_Share_Pct"] = (sub["Emissions_MtCO2eq"] / glob * 100).round(2)
        sub["Rank"] = range(1, len(sub) + 1)
        return sub[["Rank", "Country", "EDGAR_Code", "Emissions_MtCO2eq", "Global_Share_Pct", "Emissions_Per_Capita_tCO2eq", "Emissions_Per_GDP_tCO2eq_per_kUSD"]]

    def get_country_trajectory(self, country: str) -> pd.DataFrame:
        """Return historical trajectory (1970-2025) for a selected country or aggregate."""
        m = self.master_df
        sub = m[m["Country"].str.lower() == country.lower()].sort_values(by="Year").copy()
        if sub.empty:
            return pd.DataFrame()

        sub["YoY_Growth_Pct"] = sub["Emissions_MtCO2eq"].pct_change() * 100
        sub["YoY_Absolute_Mt"] = sub["Emissions_MtCO2eq"].diff()
        sub["Cumulative_MtCO2eq"] = sub["Emissions_MtCO2eq"].cumsum()
        return sub

    def get_sector_breakdown(self, country: str = "GLOBAL TOTAL", year: int = 2025) -> pd.DataFrame:
        """Return sectoral emissions and percentage contribution for a country and year."""
        s = self.sectors_df
        sub = s[(s["Country"].str.lower() == country.lower()) & (s["Year"] == year)]
        if sub.empty:
            return pd.DataFrame()

        sec_sum = sub.groupby("Sector")["Emissions_MtCO2eq"].sum().reset_index()
        total_sec = sec_sum["Emissions_MtCO2eq"].sum()
        sec_sum["Sector_Share_Pct"] = (sec_sum["Emissions_MtCO2eq"] / total_sec * 100).round(2) if total_sec > 0 else 0
        return sec_sum.sort_values(by="Emissions_MtCO2eq", ascending=False).reset_index(drop=True)

    def get_sector_timeline(self, country: str = "India") -> pd.DataFrame:
        """Return sector-wise time series (1970-2025) for stacked area / line visualizations."""
        s = self.sectors_df
        sub = s[s["Country"].str.lower() == country.lower()]
        pivot = sub.pivot_table(
            index="Year",
            columns="Sector",
            values="Emissions_MtCO2eq",
            aggfunc="sum"
        ).fillna(0.0).reset_index()
        return pivot

    def get_substance_breakdown(self, country: str = "India", year: int = 2025) -> pd.DataFrame:
        """Return greenhouse gas substance breakdown (CO2, CH4, N2O, F-gases) in AR5 CO2eq."""
        s = self.sectors_df
        sub = s[(s["Country"].str.lower() == country.lower()) & (s["Year"] == year)]
        if sub.empty:
            return pd.DataFrame()

        sub_sum = sub.groupby("Substance")["Emissions_MtCO2eq"].sum().reset_index()
        total_gas = sub_sum["Emissions_MtCO2eq"].sum()
        sub_sum["Substance_Share_Pct"] = (sub_sum["Emissions_MtCO2eq"] / total_gas * 100).round(2) if total_gas > 0 else 0
        return sub_sum.sort_values(by="Emissions_MtCO2eq", ascending=False).reset_index(drop=True)

    def compare_countries(self, countries: List[str], metric: str = "Emissions_MtCO2eq") -> pd.DataFrame:
        """Multi-country comparative matrix across 1970-2025."""
        m = self.master_df
        target_countries = [c.lower() for c in countries]
        sub = m[m["Country"].str.lower().isin(target_countries)].copy()
        if sub.empty or metric not in sub.columns:
            return pd.DataFrame()

        pivot = sub.pivot_table(index="Year", columns="Country", values=metric).reset_index()
        return pivot

    def get_available_countries(self) -> List[str]:
        """Return sorted list of all countries available for analysis."""
        return sorted(self.master_df["Country"].unique().tolist())

    def get_available_sectors(self) -> List[str]:
        """Return list of distinct economic sectors."""
        return sorted(self.sectors_df["Sector"].unique().tolist())

    def get_available_substances(self) -> List[str]:
        """Return list of greenhouse gas substances."""
        return sorted(self.sectors_df["Substance"].unique().tolist())


analyzer = EmissionAnalyzer()

if __name__ == "__main__":
    print("Testing EmissionAnalyzer...")
    ov = analyzer.get_global_overview_metrics(2025)
    print("Overview 2025:", ov)
    top = analyzer.get_top_emitting_countries(2025, 5)
    print("Top 5 Emitters:\n", top[["Rank", "Country", "Emissions_MtCO2eq", "Global_Share_Pct"]])
    ind_sec = analyzer.get_sector_breakdown("India", 2025)
    print("India Sectors 2025:\n", ind_sec)

