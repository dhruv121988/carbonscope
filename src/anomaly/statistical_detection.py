"""
CarbonScope 2.0 - Statistical Z-Score Anomaly Detection Engine
Detects structural disruptions, sharp annual swings, and atypical patterns
relative to historical rolling baselines.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from src.analysis.emission_analysis import analyzer


class StatisticalAnomalyDetector:
    """Z-Score and rolling dispersion outlier detector for climate time series."""

    @staticmethod
    def detect_trajectory_anomalies(
        country: str = "India",
        z_threshold: float = 2.0,
        baseline_window: int = 5
    ) -> pd.DataFrame:
        """
        Detect anomalies in country emission trajectory against a rolling baseline.
        Computes deviation, Z-score, anomaly flag, and scientific rationale.
        """
        traj = analyzer.get_country_trajectory(country)
        if traj.empty:
            return pd.DataFrame()

        df = traj.copy()

        # Rolling historical baseline (excluding current year via shift)
        lagged = df["Emissions_MtCO2eq"].shift(1)
        rolling_mean = lagged.rolling(window=baseline_window, min_periods=2).mean()
        rolling_std = lagged.rolling(window=baseline_window, min_periods=2).std().replace(0, np.nan)

        # Baseline: fallback to first valid mean for the earliest years
        df["Historical_Baseline"] = rolling_mean.bfill()
        df["Baseline_Std"] = rolling_std.bfill().fillna(df["Emissions_MtCO2eq"].std())

        # Difference and percentage deviation
        df["Absolute_Diff_Mt"] = df["Emissions_MtCO2eq"] - df["Historical_Baseline"]
        df["Pct_Deviation"] = (df["Absolute_Diff_Mt"] / df["Historical_Baseline"] * 100).round(2)

        # Z-Score computation
        df["Z_Score"] = ((df["Emissions_MtCO2eq"] - df["Historical_Baseline"]) / df["Baseline_Std"]).round(3)
        df["Is_Anomaly"] = df["Z_Score"].abs() >= z_threshold

        # Anomaly classification and rationale
        rationales = []
        for _, row in df.iterrows():
            if not row["Is_Anomaly"]:
                rationales.append("Normal variation within historical statistical envelope.")
            else:
                z = row["Z_Score"]
                pct = row["Pct_Deviation"]
                yr = int(row["Year"])
                diff = row["Absolute_Diff_Mt"]

                direction = "abrupt upward surge" if diff > 0 else "unusual contraction"
                historical_context = ""
                if yr == 2020:
                    historical_context = " (matches the global COVID-19 pandemic economic lockdown deflection)"
                elif yr in [2008, 2009]:
                    historical_context = " (aligns with the 2008 Global Financial Crisis industrial slowdown)"
                elif yr in [1991, 1992, 1993]:
                    historical_context = " (aligns with post-Soviet structural realignments and geopolitical changes)"

                rationales.append(
                    f"Z-score of {z:+.2f} ({pct:+.1f}% vs {baseline_window}yr baseline of {row['Historical_Baseline']:.1f} Mt). "
                    f"Represents an {direction}{historical_context}. Requires technical investigation."
                )

        df["Explanation"] = rationales
        df["Detection_Method"] = "Statistical Z-Score"

        return df[[
            "Year", "Country", "Emissions_MtCO2eq", "Historical_Baseline",
            "Absolute_Diff_Mt", "Pct_Deviation", "Z_Score", "Is_Anomaly",
            "Explanation", "Detection_Method"
        ]]


statistical_detector = StatisticalAnomalyDetector()

if __name__ == "__main__":
    print("Testing StatisticalAnomalyDetector...")
    anom = statistical_detector.detect_trajectory_anomalies("India", z_threshold=2.0)
    flagged = anom[anom["Is_Anomaly"]]
    print(f"Flagged anomalies for India ({len(flagged)}):")
    print(flagged[["Year", "Emissions_MtCO2eq", "Z_Score", "Pct_Deviation", "Explanation"]])

