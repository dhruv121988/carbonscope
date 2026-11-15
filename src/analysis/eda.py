"""
CarbonScope 2.0 - Exploratory Data Analysis (EDA) Automation
Generates exploratory statistical summaries, decadal compound growth rates,
and analytical metrics for the Emission Explorer module.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.analysis.emission_analysis import analyzer

REPORTS_DIR = os.path.join(BASE_DIR, "reports", "evaluation")


class EDAManager:
    """Computes academic-grade exploratory statistics on EDGAR climate observations."""

    def __init__(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def compute_country_summary(self, country: str = "India") -> Dict[str, Any]:
        """Compute key statistical moments and milestone indicators for a country."""
        traj = analyzer.get_country_trajectory(country)
        if traj.empty:
            return {}

        e = traj["Emissions_MtCO2eq"]
        y1970 = traj[traj["Year"] == 1970]["Emissions_MtCO2eq"].values[0]
        y1990 = traj[traj["Year"] == 1990]["Emissions_MtCO2eq"].values[0]
        y2000 = traj[traj["Year"] == 2000]["Emissions_MtCO2eq"].values[0]
        y2010 = traj[traj["Year"] == 2010]["Emissions_MtCO2eq"].values[0]
        y2020 = traj[traj["Year"] == 2020]["Emissions_MtCO2eq"].values[0]
        y2025 = traj[traj["Year"] == 2025]["Emissions_MtCO2eq"].values[0]

        # CAGR calculations
        cagr_1970_2025 = ((y2025 / y1970) ** (1 / (2025 - 1970)) - 1) * 100 if y1970 > 0 else 0
        cagr_1990_2025 = ((y2025 / y1990) ** (1 / (2025 - 1990)) - 1) * 100 if y1990 > 0 else 0

        # Maximum surge year and maximum dip year
        valid_yoy = traj["YoY_Growth_Pct"].dropna()
        max_surge_idx = valid_yoy.idxmax()
        max_dip_idx = valid_yoy.idxmin()

        max_surge_year = int(traj.loc[max_surge_idx, "Year"])
        max_surge_val = float(traj.loc[max_surge_idx, "YoY_Growth_Pct"])

        max_dip_year = int(traj.loc[max_dip_idx, "Year"])
        max_dip_val = float(traj.loc[max_dip_idx, "YoY_Growth_Pct"])

        return {
            "country": country,
            "observations_count": len(traj),
            "start_year": 1970,
            "end_year": 2025,
            "1970_emissions_mt": round(y1970, 2),
            "1990_emissions_mt": round(y1990, 2),
            "2000_emissions_mt": round(y2000, 2),
            "2010_emissions_mt": round(y2010, 2),
            "2020_emissions_mt": round(y2020, 2),
            "2025_emissions_mt": round(y2025, 2),
            "cagr_1970_2025_pct": round(cagr_1970_2025, 2),
            "cagr_1990_2025_pct": round(cagr_1990_2025, 2),
            "mean_annual_emissions_mt": round(float(e.mean()), 2),
            "std_dev_mt": round(float(e.std()), 2),
            "min_emissions_mt": round(float(e.min()), 2),
            "max_emissions_mt": round(float(e.max()), 2),
            "peak_growth_year": max_surge_year,
            "peak_growth_pct": round(max_surge_val, 2),
            "sharpest_decline_year": max_dip_year,
            "sharpest_decline_pct": round(max_dip_val, 2)
        }

    def compute_global_inequality_gini(self, year: int = 2025) -> float:
        """
        Compute Gini coefficient of global emissions distribution across countries.
        Quantifies planetary emission concentration.
        """
        m = analyzer.master_df
        sub = m[(~m["Is_Aggregate"]) & (m["Year"] == year)]["Emissions_MtCO2eq"].dropna().values
        if len(sub) == 0:
            return 0.0

        sub = np.sort(sub)
        n = len(sub)
        index = np.arange(1, n + 1)
        gini = ((2 * np.sum(index * sub)) / (n * np.sum(sub))) - ((n + 1) / n)
        return round(float(gini), 4)


eda = EDAManager()

if __name__ == "__main__":
    print("Testing EDAManager...")
    ind_eda = eda.compute_country_summary("India")
    print("India EDA Summary:\n", ind_eda)
    gini = eda.compute_global_inequality_gini(2025)
    print("Global Emissions Gini Coefficient (2025):", gini)

