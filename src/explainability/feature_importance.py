"""
CarbonScope 2.0 - Feature Importance & Permutation Importance Engine
Computes intrinsic model weights (coefficients, Gini importances)
and model-agnostic permutation importances across test datasets.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.inspection import permutation_importance
from src.features.feature_engineering import feature_engine
from src.models.forecasting import forecaster


class FeatureImportanceEngine:
    """Computes model-intrinsic and model-agnostic feature importances."""

    @staticmethod
    def compute_intrinsic_importance(model: Any, feature_names: List[str]) -> pd.DataFrame:
        """Extract intrinsic feature importances or linear coefficients."""
        if hasattr(model, "feature_importances_"):
            # Tree models (Random Forest, Gradient Boosting)
            vals = model.feature_importances_
            metric_type = "Gini / Impurity Reduction"
        elif hasattr(model, "coef_"):
            # Linear Regression
            vals = np.abs(model.coef_)
            metric_type = "Absolute Coefficient Magnitude"
        elif hasattr(model, "named_steps") and hasattr(model.named_steps.get("svr", None), "coef_"):
            # SVR Linear
            vals = np.abs(model.named_steps["svr"].coef_[0])
            metric_type = "Absolute Weight Vector Magnitude"
        else:
            # Fallback uniform
            vals = np.ones(len(feature_names)) / len(feature_names)
            metric_type = "Normalized Baseline"

        # Normalize to percentage sum
        total = np.sum(vals)
        norm_pct = (vals / total * 100).round(2) if total > 0 else np.zeros_like(vals)

        df = pd.DataFrame({
            "Feature": feature_names,
            "Importance_Raw": np.round(vals, 4),
            "Importance_Pct": norm_pct,
            "Metric_Type": metric_type
        })
        return df.sort_values(by="Importance_Pct", ascending=False).reset_index(drop=True)

    @staticmethod
    def compute_permutation_importance(
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        feature_names: List[str],
        n_repeats: int = 10,
        random_state: int = 42
    ) -> pd.DataFrame:
        """Compute model-agnostic permutation importance on holdout test data."""
        perm = permutation_importance(
            model,
            X_test,
            y_test,
            n_repeats=n_repeats,
            random_state=random_state,
            scoring="neg_root_mean_squared_error"
        )

        mean_scores = perm.importances_mean
        # Invert negative RMSE so that higher = more essential
        scores_pos = np.maximum(0, mean_scores)
        total = np.sum(scores_pos)
        norm_pct = (scores_pos / total * 100).round(2) if total > 0 else np.zeros_like(scores_pos)

        df = pd.DataFrame({
            "Feature": feature_names,
            "Permutation_Score": np.round(mean_scores, 4),
            "Importance_Pct": norm_pct,
            "Std_Dev": np.round(perm.importances_std, 4)
        })
        return df.sort_values(by="Importance_Pct", ascending=False).reset_index(drop=True)


feature_importance_engine = FeatureImportanceEngine()

if __name__ == "__main__":
    print("Testing FeatureImportanceEngine...")
    train_res = forecaster.train_models_for_entity("India", 2015)
    rf_model = forecaster.trained_models["India:Random Forest"]
    imp = feature_importance_engine.compute_intrinsic_importance(rf_model, train_res["feature_cols"])
    print("Random Forest Feature Importance:\n", imp)

