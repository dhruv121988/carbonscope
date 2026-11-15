"""
CarbonScope 2.0 - Feature Engineering Engine for Emission Forecasting
Constructs leak-free chronological features (lags, momentum, rolling windows)
for supervised regression modeling on EDGAR time series.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler
from src.analysis.emission_analysis import analyzer


class FeatureEngineeringEngine:
    """Extracts leak-free econometric and time-series features for climate forecasting."""

    FEATURE_COLS = [
        "Lag_1",
        "Lag_2",
        "Lag_3",
        "Lag_5",
        "Rolling_Mean_3",
        "Rolling_Mean_5",
        "Rolling_Std_5",
        "Growth_1yr",
        "Growth_3yr",
        "Year_Index"
    ]

    def __init__(self):
        self.scaler = StandardScaler()

    def create_features_for_series(self, series: pd.Series, years: pd.Series) -> pd.DataFrame:
        """
        Builds sequential features strictly from historical preceding observations.
        At index t, all rolling and lag features are computed from t-1 and earlier,
        ensuring 0% temporal data leakage.
        """
        df = pd.DataFrame({
            "Year": years.values,
            "Target": series.values
        })

        # Lag features
        df["Lag_1"] = df["Target"].shift(1)
        df["Lag_2"] = df["Target"].shift(2)
        df["Lag_3"] = df["Target"].shift(3)
        df["Lag_5"] = df["Target"].shift(5)

        # Rolling statistics on lagged values
        # Shifting by 1 ensures the current target is never part of the window
        lagged_s = df["Target"].shift(1)
        df["Rolling_Mean_3"] = lagged_s.rolling(window=3).mean()
        df["Rolling_Mean_5"] = lagged_s.rolling(window=5).mean()
        df["Rolling_Std_5"] = lagged_s.rolling(window=5).std().fillna(0.0)

        # Growth rates
        df["Growth_1yr"] = (df["Lag_1"] - df["Lag_2"]) / df["Lag_2"].replace(0, np.nan)
        df["Growth_3yr"] = (df["Lag_1"] - df["Lag_4"] if "Lag_4" in df else (df["Lag_1"] - df["Lag_3"]) / df["Lag_3"].replace(0, np.nan))
        df["Growth_1yr"] = df["Growth_1yr"].fillna(0.0).clip(-1.0, 3.0)
        df["Growth_3yr"] = df["Growth_3yr"].fillna(0.0).clip(-1.0, 5.0)

        # Time trends
        df["Year_Index"] = df["Year"] - 1970
        df["Decade"] = (df["Year"] // 10) * 10

        # Drop rows where lag_5 is NaN (first 5 years: 1970-1974)
        df_clean = df.dropna(subset=["Lag_5"]).reset_index(drop=True)
        return df_clean

    def prepare_country_dataset(
        self,
        country: str = "India",
        train_cutoff_year: int = 2015
    ) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
        """
        Prepare train and test splits chronologically for a specific country.
        Train: 1975 to train_cutoff_year (e.g. 2015)
        Test: (train_cutoff_year + 1) to 2025
        """
        traj = analyzer.get_country_trajectory(country)
        if traj.empty:
            raise ValueError(f"No trajectory data found for country '{country}'")

        featured = self.create_features_for_series(
            series=traj["Emissions_MtCO2eq"],
            years=traj["Year"]
        )

        train_df = featured[featured["Year"] <= train_cutoff_year].copy().reset_index(drop=True)
        test_df = featured[featured["Year"] > train_cutoff_year].copy().reset_index(drop=True)

        return train_df, test_df, self.FEATURE_COLS

    def prepare_sector_dataset(
        self,
        country: str = "India",
        sector: str = "Power Industry",
        train_cutoff_year: int = 2015
    ) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
        """Prepare train and test splits for a country-sector combination."""
        s = analyzer.sectors_df
        sub = s[(s["Country"].str.lower() == country.lower()) & (s["Sector"].str.lower() == sector.lower())]
        if sub.empty:
            raise ValueError(f"No data for country '{country}' in sector '{sector}'")

        sec_annual = sub.groupby("Year")["Emissions_MtCO2eq"].sum().reset_index().sort_values(by="Year")
        featured = self.create_features_for_series(
            series=sec_annual["Emissions_MtCO2eq"],
            years=sec_annual["Year"]
        )

        train_df = featured[featured["Year"] <= train_cutoff_year].copy().reset_index(drop=True)
        test_df = featured[featured["Year"] > train_cutoff_year].copy().reset_index(drop=True)

        return train_df, test_df, self.FEATURE_COLS

    def construct_future_input_row(self, historical_tail: pd.DataFrame, future_year: int) -> pd.DataFrame:
        """
        Construct a single feature row for recursive multi-step forecasting.
        Uses the most recent observations/predictions in historical_tail.
        """
        # Tail must have at least 5 previous Target values
        targets = historical_tail["Target"].values
        l1 = targets[-1]
        l2 = targets[-2]
        l3 = targets[-3]
        l5 = targets[-5]

        last_5 = targets[-5:]
        rm3 = float(np.mean(targets[-3:]))
        rm5 = float(np.mean(last_5))
        rstd5 = float(np.std(last_5))

        g1 = (l1 - l2) / l2 if l2 != 0 else 0.0
        g3 = (l1 - targets[-4]) / targets[-4] if targets[-4] != 0 else 0.0

        row = pd.DataFrame([{
            "Lag_1": l1,
            "Lag_2": l2,
            "Lag_3": l3,
            "Lag_5": l5,
            "Rolling_Mean_3": rm3,
            "Rolling_Mean_5": rm5,
            "Rolling_Std_5": rstd5,
            "Growth_1yr": float(np.clip(g1, -1.0, 3.0)),
            "Growth_3yr": float(np.clip(g3, -1.0, 5.0)),
            "Year_Index": future_year - 1970
        }])
        return row[self.FEATURE_COLS]


feature_engine = FeatureEngineeringEngine()

if __name__ == "__main__":
    print("Testing FeatureEngineeringEngine...")
    train, test, cols = feature_engine.prepare_country_dataset("India", 2015)
    print("Features extracted:", cols)
    print(f"Train split (1975-2015): {len(train)} rows. Sample row:\n", train[cols].head(1))
    print(f"Test split (2016-2025): {len(test)} rows. Years:", test["Year"].tolist())

