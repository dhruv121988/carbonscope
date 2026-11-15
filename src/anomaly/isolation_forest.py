"""
CarbonScope 2.0 - Machine Learning Isolation Forest Anomaly Detection
Unsupervised multi-attribute anomaly detection engine identifying non-linear
disruptions in national and sectoral emission trajectories.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.ensemble import IsolationForest
from src.analysis.emission_analysis import analyzer


class IsolationForestDetector:
    """Multivariate Isolation Forest outlier detector for greenhouse gas trajectories."""

    @staticmethod
    def detect_anomalies(
        country: str = "India",
        contamination: float = 0.08,
        random_state: int = 42
    ) -> pd.DataFrame:
        """
        Fit Isolation Forest on emissions, annual deltas, growth rates, and baseline deviations.
        """
        traj = analyzer.get_country_trajectory(country)
        if traj.empty:
            return pd.DataFrame()

        df = traj.copy()

        # Compute feature dimensions
        df["Delta_Mt"] = df["Emissions_MtCO2eq"].diff().fillna(0.0)
        df["Pct_Change"] = (df["Emissions_MtCO2eq"].pct_change() * 100).fillna(0.0)

        rolling_5 = df["Emissions_MtCO2eq"].shift(1).rolling(5, min_periods=2).mean().bfill()
        df["Baseline_5yr"] = rolling_5
        df["Deviation_Mt"] = df["Emissions_MtCO2eq"] - rolling_5
        df["Pct_Deviation"] = (df["Deviation_Mt"] / rolling_5 * 100).round(2)

        # Feature matrix for Isolation Forest
        feature_cols = ["Emissions_MtCO2eq", "Delta_Mt", "Pct_Change", "Deviation_Mt"]
        X = df[feature_cols].values

        iso = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=150
        )
        preds = iso.fit_predict(X)  # -1 for anomaly, 1 for normal
        scores = iso.decision_function(X)  # lower = more anomalous

        df["Is_Anomaly"] = preds == -1
        # Normalize anomaly score from 0 (very normal) to 100 (most anomalous)
        # decision_function is centered roughly around 0; negative is anomaly
        min_s, max_s = scores.min(), scores.max()
        if max_s > min_s:
            norm_scores = (1 - (scores - min_s) / (max_s - min_s)) * 100
        else:
            norm_scores = np.zeros_like(scores)

        df["Anomaly_Score"] = np.round(norm_scores, 1)

        # Construct scientific explanation
        explanations = []
        for _, r in df.iterrows():
            if not r["Is_Anomaly"]:
                explanations.append("Consistent with multi-attribute historical trajectory envelope.")
            else:
                yr = int(r["Year"])
                diff = r["Deviation_Mt"]
                pct = r["Pct_Deviation"]
                score = r["Anomaly_Score"]
                yoy = r["Pct_Change"]

                context = ""
                if yr == 2020:
                    context = " Reflects global COVID-19 pandemic industrial slowdown."
                elif yr in [2008, 2009]:
                    context = " Reflects economic disruption from the 2008 global financial crisis."
                elif yr in [1990, 1991]:
                    context = " Reflects macroeconomic transition phase."

                explanations.append(
                    f"Multivariate Isolation Forest flagged Year {yr} (Score: {score:.1f}/100). "
                    f"Annual YoY shift: {yoy:+.1f}%, baseline deviation: {diff:+.1f} Mt ({pct:+.1f}%).{context}"
                )

        df["Explanation"] = explanations
        df["Detection_Method"] = "Isolation Forest (Unsupervised ML)"

        return df[[
            "Year", "Country", "Emissions_MtCO2eq", "Baseline_5yr",
            "Deviation_Mt", "Pct_Deviation", "Anomaly_Score",
            "Is_Anomaly", "Explanation", "Detection_Method"
        ]]


iso_detector = IsolationForestDetector()

if __name__ == "__main__":
    print("Testing IsolationForestDetector...")
    iso_res = iso_detector.detect_anomalies("India", contamination=0.08)
    flagged = iso_res[iso_res["Is_Anomaly"]]
    print(f"Isolation Forest flagged {len(flagged)} years for India:")
    print(flagged[["Year", "Emissions_MtCO2eq", "Anomaly_Score", "Pct_Deviation", "Explanation"]])

