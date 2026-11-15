"""
CarbonScope 2.0 - SHAP Explainability Engine (XAI Investigator)
Implements TreeSHAP and KernelSHAP for global feature attributions,
beeswarm summaries, and individual prediction waterfall decompositions.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import numpy as np
import pandas as pd
import shap
from typing import Dict, Any, List, Tuple, Optional
from src.features.feature_engineering import feature_engine
from src.models.forecasting import forecaster


class ShapAnalysisEngine:
    """Rigorous explainable AI engine for interpreting climate regression predictions."""

    def __init__(self):
        self._explainer_cache: Dict[str, Any] = {}

    def get_explainer(self, country: str, model_name: str = "Random Forest") -> Tuple[Any, np.ndarray, np.ndarray, List[str], List[int]]:
        """Get or initialize SHAP explainer for a trained model."""
        cache_key = f"{country}:{model_name}"
        if cache_key not in forecaster.trained_models:
            forecaster.train_models_for_entity(country)

        model = forecaster.trained_models[cache_key]
        train_df, test_df, feature_cols = feature_engine.prepare_country_dataset(country)

        X_train = train_df[feature_cols].values
        X_test = test_df[feature_cols].values
        test_years = test_df["Year"].tolist()

        if model_name in ["Random Forest", "Gradient Boosting"]:
            explainer = shap.TreeExplainer(model)
        elif model_name == "Linear Regression":
            explainer = shap.LinearExplainer(model, X_train)
        else:
            # SVR or fallback: use sample background
            explainer = shap.KernelExplainer(model.predict, shap.sample(X_train, 25))

        return explainer, X_train, X_test, feature_cols, test_years

    def compute_global_shap(
        self,
        country: str = "India",
        model_name: str = "Random Forest"
    ) -> Dict[str, Any]:
        """Compute global SHAP feature importance across the test set."""
        explainer, X_train, X_test, feature_cols, test_years = self.get_explainer(country, model_name)
        shap_values = explainer.shap_values(X_test)

        # Handle different SHAP output formats
        if isinstance(shap_values, list):
            sv = shap_values[0]
        else:
            sv = shap_values

        mean_abs_shap = np.mean(np.abs(sv), axis=0)
        total_shap = np.sum(mean_abs_shap)
        pct_impact = (mean_abs_shap / total_shap * 100).round(2) if total_shap > 0 else np.zeros_like(mean_abs_shap)

        global_df = pd.DataFrame({
            "Feature": feature_cols,
            "Mean_Abs_SHAP": np.round(mean_abs_shap, 2),
            "Impact_Share_Pct": pct_impact
        }).sort_values(by="Mean_Abs_SHAP", ascending=False).reset_index(drop=True)

        # Base value (expected value E[f(X)])
        ev = explainer.expected_value
        base_val = float(ev[0]) if isinstance(ev, (list, np.ndarray)) else float(ev)

        return {
            "country": country,
            "model_name": model_name,
            "base_value_mt": round(base_val, 2),
            "global_importance_table": global_df,
            "feature_names": feature_cols,
            "shap_matrix": sv.tolist(),
            "feature_matrix": X_test.tolist(),
            "test_years": test_years
        }

    def compute_individual_waterfall(
        self,
        country: str = "India",
        model_name: str = "Random Forest",
        target_year: int = 2025
    ) -> Dict[str, Any]:
        """
        Decompose an individual annual prediction into its constituent SHAP forces.
        f(x) = E[f(X)] + sum(phi_i)
        """
        global_res = self.compute_global_shap(country, model_name)
        years = global_res["test_years"]

        if target_year not in years:
            target_year = years[-1]  # fallback to latest test year

        row_idx = years.index(target_year)
        shap_row = np.array(global_res["shap_matrix"][row_idx])
        feat_row = np.array(global_res["feature_matrix"][row_idx])
        feature_names = global_res["feature_names"]
        base_val = global_res["base_value_mt"]

        pred_val = base_val + np.sum(shap_row)

        breakdown = []
        for name, val, phi in zip(feature_names, feat_row, shap_row):
            direction = "Pushing Higher (+)" if phi >= 0 else "Pushing Lower (-)"
            breakdown.append({
                "Feature": name,
                "Observed_Value": round(val, 2),
                "SHAP_Impact_Mt": round(phi, 2),
                "Abs_Impact_Mt": round(abs(phi), 2),
                "Direction": direction
            })

        breakdown_df = pd.DataFrame(breakdown).sort_values(by="Abs_Impact_Mt", ascending=False).reset_index(drop=True)

        return {
            "country": country,
            "model_name": model_name,
            "target_year": target_year,
            "base_value_mt": round(base_val, 2),
            "prediction_mt": round(pred_val, 2),
            "waterfall_table": breakdown_df,
            "sum_shap_forces_mt": round(float(np.sum(shap_row)), 2)
        }


shap_engine = ShapAnalysisEngine()

if __name__ == "__main__":
    print("Testing ShapAnalysisEngine...")
    g_res = shap_engine.compute_global_shap("India", "Random Forest")
    print("Global Mean Absolute SHAP:\n", g_res["global_importance_table"])
    wf = shap_engine.compute_individual_waterfall("India", "Random Forest", 2025)
    print(f"\nWaterfall for {wf['target_year']} (Base: {wf['base_value_mt']} Mt -> Pred: {wf['prediction_mt']} Mt):")
    print(wf["waterfall_table"].head(5))

