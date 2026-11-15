"""
CarbonScope 2.0 - Machine Learning Forecasting Engine
Trains, validates, compares, and produces multi-step recursive forecasts
using Linear Regression, Support Vector Regression, Random Forest, and Gradient Boosting.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from src.features.feature_engineering import feature_engine
from src.models.evaluation import evaluator

MODELS_DIR = os.path.join(BASE_DIR, "models", "trained_models")
os.makedirs(MODELS_DIR, exist_ok=True)


class EmissionForecastingEngine:
    """Supervised regression modeling suite for national and global emission trajectories."""

    AVAILABLE_MODELS = {
        "Linear Regression": lambda: LinearRegression(),
        "Support Vector Regression": lambda: Pipeline([
            ("scaler", StandardScaler()),
            ("svr", SVR(kernel="rbf", C=100.0, epsilon=5.0))
        ]),
        "Random Forest": lambda: RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            min_samples_split=3,
            random_state=42
        ),
        "Gradient Boosting": lambda: GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=4,
            random_state=42
        )
    }

    def __init__(self):
        self.trained_models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}

    def train_models_for_entity(
        self,
        country: str = "India",
        train_cutoff_year: int = 2015
    ) -> Dict[str, Any]:
        """
        Train all 4 regression models chronologically on historical observations.
        Evaluates on out-of-sample future test observations (e.g. 2016-2025).
        """
        train_df, test_df, feature_cols = feature_engine.prepare_country_dataset(country, train_cutoff_year)

        X_train = train_df[feature_cols].values
        y_train = train_df["Target"].values
        train_years = train_df["Year"].values

        X_test = test_df[feature_cols].values
        y_test = test_df["Target"].values
        test_years = test_df["Year"].values

        results = {}
        best_model_name = None
        lowest_test_rmse = float("inf")

        for name, model_factory in self.AVAILABLE_MODELS.items():
            model = model_factory()
            model.fit(X_train, y_train)

            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)

            train_metrics = evaluator.calculate_metrics(y_train, train_pred)
            test_metrics = evaluator.calculate_metrics(y_test, test_pred)
            residuals_df = evaluator.compute_residuals(y_test, test_pred, test_years)

            if test_metrics["RMSE"] < lowest_test_rmse:
                lowest_test_rmse = test_metrics["RMSE"]
                best_model_name = name

            results[name] = {
                "model_name": name,
                "train_metrics": train_metrics,
                "test_metrics": test_metrics,
                "residuals": residuals_df,
                "test_predictions": test_pred.tolist(),
                "test_actuals": y_test.tolist(),
                "test_years": test_years.tolist()
            }

            # Cache in memory
            cache_key = f"{country}:{name}"
            self.trained_models[cache_key] = model

            # Save model to disk
            model_file = os.path.join(MODELS_DIR, f"{country.replace(' ', '_')}_{name.replace(' ', '_')}.pkl")
            with open(model_file, "wb") as f:
                pickle.dump(model, f)

        # Full historical curve (train + test)
        all_years = np.concatenate([train_years, test_years])
        all_actuals = np.concatenate([y_train, y_test])

        return {
            "country": country,
            "train_cutoff_year": train_cutoff_year,
            "best_model_name": best_model_name,
            "best_test_rmse": lowest_test_rmse,
            "models": results,
            "historical_data": {
                "years": all_years.tolist(),
                "actuals": all_actuals.tolist()
            },
            "feature_cols": feature_cols
        }

    def generate_recursive_forecast(
        self,
        country: str = "India",
        model_name: str = "Random Forest",
        horizon_years: int = 10,
        start_year: int = 2026
    ) -> pd.DataFrame:
        """
        Generate recursive multi-step forecasting beyond the latest EDGAR observation.
        Uses model's own predictions as future lag inputs.
        Computes 95% confidence intervals (approx +/- 1.96 * Test_RMSE).
        """
        # Ensure model is trained
        cache_key = f"{country}:{model_name}"
        if cache_key not in self.trained_models:
            train_res = self.train_models_for_entity(country)
            model = self.trained_models[cache_key]
            test_rmse = train_res["models"][model_name]["test_metrics"]["RMSE"]
        else:
            model = self.trained_models[cache_key]
            # Retrieve test RMSE
            test_rmse = 45.0  # fallback conservative value

        # Retrieve full trajectory up to 2025
        from src.analysis.emission_analysis import analyzer
        traj = analyzer.get_country_trajectory(country)
        featured = feature_engine.create_features_for_series(traj["Emissions_MtCO2eq"], traj["Year"])

        rolling_tail = featured.tail(10)[["Year", "Target"]].copy()

        forecast_rows = []
        current_year = start_year

        for step in range(horizon_years):
            input_row = feature_engine.construct_future_input_row(rolling_tail, current_year)
            pred = float(model.predict(input_row.values)[0])

            # Scientific plausibility guardrail: emissions cannot be negative
            pred = max(0.0, pred)

            lower_bound = max(0.0, pred - 1.96 * test_rmse * np.sqrt(1 + step * 0.1))
            upper_bound = pred + 1.96 * test_rmse * np.sqrt(1 + step * 0.1)

            forecast_rows.append({
                "Year": current_year,
                "Forecasted_MtCO2eq": round(pred, 2),
                "Confidence_Lower_95": round(lower_bound, 2),
                "Confidence_Upper_95": round(upper_bound, 2),
                "Model": model_name,
                "Country": country,
                "Is_Forecast": True
            })

            # Append to rolling tail for next recursive step
            new_tail_entry = pd.DataFrame([{"Year": current_year, "Target": pred}])
            rolling_tail = pd.concat([rolling_tail, new_tail_entry], ignore_index=True)
            current_year += 1

        return pd.DataFrame(forecast_rows)


forecaster = EmissionForecastingEngine()

if __name__ == "__main__":
    print("Testing EmissionForecastingEngine...")
    res = forecaster.train_models_for_entity("India", 2015)
    print("Best performing model for India:", res["best_model_name"], "Test RMSE:", res["best_test_rmse"])
    for m_name, m_data in res["models"].items():
        print(f"[{m_name}] Train R2: {m_data['train_metrics']['R2']} | Test R2: {m_data['test_metrics']['R2']} | Test RMSE: {m_data['test_metrics']['RMSE']}")
    print("\nGenerating 10-year recursive forecast (2026-2035)...")
    fc = forecaster.generate_recursive_forecast("India", res["best_model_name"], 10)
    print(fc[["Year", "Forecasted_MtCO2eq", "Confidence_Lower_95", "Confidence_Upper_95"]])

