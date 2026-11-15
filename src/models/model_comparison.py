"""
CarbonScope 2.0 - Model Comparison & Benchmark Suite
Generates comparative scorecards across models, tracks training vs testing metrics,
and exports formal evaluation reports.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import json
import pandas as pd
from typing import Dict, Any, List
from src.models.forecasting import forecaster

REPORTS_DIR = os.path.join(BASE_DIR, "reports", "evaluation")
os.makedirs(REPORTS_DIR, exist_ok=True)


class ModelComparisonSuite:
    """Orchestrates comprehensive multi-model benchmarking and evaluation logging."""

    @staticmethod
    def get_comparison_table(eval_result: Dict[str, Any]) -> pd.DataFrame:
        """Format model evaluation dictionary into a clean comparison DataFrame."""
        rows = []
        for name, data in eval_result["models"].items():
            tr = data["train_metrics"]
            te = data["test_metrics"]
            rows.append({
                "Model Architecture": name,
                "Train MAE (Mt)": tr["MAE"],
                "Train RMSE (Mt)": tr["RMSE"],
                "Train R²": tr["R2"],
                "Test MAE (Mt)": te["MAE"],
                "Test MSE (Mt²)": te["MSE"],
                "Test RMSE (Mt)": te["RMSE"],
                "Test MAPE (%)": te["MAPE_pct"],
                "Test R²": te["R2"],
                "Is_Best": name == eval_result["best_model_name"]
            })
        df = pd.DataFrame(rows)
        return df.sort_values(by="Test RMSE (Mt)").reset_index(drop=True)

    @staticmethod
    def export_evaluation_report(eval_result: Dict[str, Any], filename: str = "model_comparison") -> str:
        """Export evaluation summary to JSON and Markdown reports."""
        json_path = os.path.join(REPORTS_DIR, f"{filename}.json")
        md_path = os.path.join(REPORTS_DIR, f"{filename}.md")

        # Serialized dictionary (exclude raw dataframes)
        clean_dict = {
            "country": eval_result["country"],
            "train_cutoff_year": eval_result["train_cutoff_year"],
            "best_model": eval_result["best_model_name"],
            "best_test_rmse": eval_result["best_test_rmse"],
            "models": {}
        }
        for name, data in eval_result["models"].items():
            clean_dict["models"][name] = {
                "train_metrics": data["train_metrics"],
                "test_metrics": data["test_metrics"]
            }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(clean_dict, f, indent=2)

        # Markdown report
        table_df = ModelComparisonSuite.get_comparison_table(eval_result)
        lines = [
            f"# CarbonScope 2.0 - ML Forecasting Evaluation Report: {eval_result['country']}\n\n",
            f"- **Validation Strategy:** Chronological Holdout Split\n",
            f"- **Training Period:** 1975 – {eval_result['train_cutoff_year']} (41 Years)\n",
            f"- **Testing Period:** {eval_result['train_cutoff_year'] + 1} – 2025 (10 Out-of-Sample Years)\n",
            f"- **Best Performing Model:** **`{eval_result['best_model_name']}`** (Test RMSE: `{eval_result['best_test_rmse']} Mt CO2eq`)\n\n",
            "## Model Benchmark Summary\n\n",
            table_df.to_markdown(index=False),
            "\n\n> [!NOTE]\n",
            "> Models were evaluated strictly on out-of-sample future years (2016-2025). High training scores are displayed alongside testing scores to verify absence of overfitting.\n"
        ]

        with open(md_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return md_path


model_comparator = ModelComparisonSuite()

if __name__ == "__main__":
    print("Testing ModelComparisonSuite...")
    res = forecaster.train_models_for_entity("India", 2015)
    tbl = model_comparator.get_comparison_table(res)
    print("Benchmark Table:\n", tbl)
    rep = model_comparator.export_evaluation_report(res, "india_benchmark")
    print("Report exported to:", rep)

