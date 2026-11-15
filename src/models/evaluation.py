"""
CarbonScope 2.0 - Model Evaluation Engine
Computes scientific regression metrics (MAE, MSE, RMSE, R2, MAPE),
residuals, and comparative scorecards across models.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class ModelEvaluator:
    """Scientific evaluation and diagnostic toolkit for climate regression models."""

    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Compute standard regression performance metrics."""
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)

        mae = float(mean_absolute_error(y_true, y_pred))
        mse = float(mean_squared_error(y_true, y_pred))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_true, y_pred))

        # Mean Absolute Percentage Error (MAPE)
        # Avoid division by zero
        non_zero = y_true != 0
        if np.any(non_zero):
            mape = float(np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100)
        else:
            mape = 0.0

        return {
            "MAE": round(mae, 2),
            "MSE": round(mse, 2),
            "RMSE": round(rmse, 2),
            "R2": round(r2, 4),
            "MAPE_pct": round(mape, 2)
        }

    @staticmethod
    def compute_residuals(y_true: np.ndarray, y_pred: np.ndarray, years: np.ndarray) -> pd.DataFrame:
        """Compute point-by-point prediction residuals and errors."""
        residuals = np.array(y_true) - np.array(y_pred)
        pct_err = (residuals / np.array(y_true)) * 100

        return pd.DataFrame({
            "Year": years,
            "Actual": np.round(y_true, 2),
            "Predicted": np.round(y_pred, 2),
            "Residual": np.round(residuals, 2),
            "Abs_Error": np.round(np.abs(residuals), 2),
            "Pct_Error": np.round(pct_err, 2)
        })


evaluator = ModelEvaluator()

