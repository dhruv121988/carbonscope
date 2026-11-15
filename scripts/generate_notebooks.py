"""
CarbonScope 2.0 - Notebook Generator
Generates reproducible, Google Colab-ready Jupyter notebooks for all ML lifecycle stages.
"""

import os
import json

NOTEBOOKS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "notebooks"))
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)


def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


def md_cell(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().split("\n")]
    }


def code_cell(code):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.strip().split("\n")]
    }


# 1. 01_data_exploration.ipynb
nb1 = make_notebook([
    md_cell("# CarbonScope 2.0 — Notebook 01: Exploratory Data Analysis\n**Authoritative Source:** European Commission JRC - EDGAR 2026\n\nThis notebook inspects the raw greenhouse gas datasets, verifies units, explores global trajectories, and performs an in-depth exploration of India's historical emissions."),
    code_cell("""# Environment Setup for Colab / Local
import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# If running on Colab, clone repo or upload data
print("Pandas version:", pd.__version__)"""),
    code_cell("""# Load GHG Totals and Sectoral Data
DATA_PATH = "../data/raw/EDGAR_2026_GHG_booklet_2026.xlsx"
df_totals = pd.read_excel(DATA_PATH, sheet_name="GHG_totals_by_country")
print("GHG Totals shape:", df_totals.shape)
df_totals.head(5)"""),
    code_cell("""# Global Trajectory Analysis (1970 - 2025)
year_cols = [c for c in df_totals.columns if str(c).isdigit()]
global_row = df_totals[df_totals['Country'] == 'GLOBAL TOTAL']
global_series = global_row[year_cols].values.flatten()

plt.figure(figsize=(10, 4))
plt.plot(year_cols, global_series / 1000.0, color="#14B8A6", linewidth=2.5)
plt.title("Global GHG Emissions (1970-2025) in Gt CO2eq", fontsize=12, fontweight='bold')
plt.xlabel("Year")
plt.ylabel("Emissions (Gt CO2eq)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.show()"""),
    code_cell("""# India Emissions Trajectory and Sectoral Analysis
india_row = df_totals[df_totals['Country'] == 'India']
india_series = india_row[year_cols].values.flatten()
print(f"India 1970: {india_series[0]:.1f} Mt | India 2025: {india_series[-1]:.1f} Mt")
print(f"55-Year Annualized Growth (CAGR): {((india_series[-1]/india_series[0])**(1/55)-1)*100:.2f}%")""")
])

# 2. 02_data_preprocessing.ipynb
nb2 = make_notebook([
    md_cell("# CarbonScope 2.0 — Notebook 02: Data Cleaning & Preprocessing Pipeline\n\nReshapes raw wide EDGAR tables into tidy longitudinal panels, handles aggregate tags, and conducts automated quality audits."),
    code_cell("""import os, sys
sys.path.insert(0, "..")
from src.preprocessing.cleaner import cleaner
from src.preprocessing.quality_audit import auditor

# Execute deterministic cleaning pipeline
res = cleaner.run_all()
print("Cleaned records summary:", res)"""),
    code_cell("""# Run quality audit and inspect health score
audit = auditor.generate_full_audit()
print("Data Integrity Health Score:", audit["integrity_verification"]["overall_health_score_pct"], "%")
print("Decadal completeness:\n", pd.DataFrame(audit["decadal_completeness"]).T)""")
])

# 3. 03_feature_engineering.ipynb
nb3 = make_notebook([
    md_cell("# CarbonScope 2.0 — Notebook 03: Feature Engineering\n\nConstructs leak-free chronological features including sequential lags, rolling means, and historical momentum growth rates."),
    code_cell("""import os, sys
sys.path.insert(0, "..")
from src.features.feature_engineering import feature_engine

train_df, test_df, feature_cols = feature_engine.prepare_country_dataset("India", train_cutoff_year=2015)
print("Engineered feature set:", feature_cols)
print(f"Train split: {len(train_df)} rows | Test split: {len(test_df)} rows")
test_df.head()""")
])

# 4. 04_model_training.ipynb
nb4 = make_notebook([
    md_cell("# CarbonScope 2.0 — Notebook 04: ML Forecasting Engine\n\nTrains and compares Linear Regression, SVR, Random Forest, and Gradient Boosting on chronological holdout splits."),
    code_cell("""import os, sys
sys.path.insert(0, "..")
from src.models.forecasting import forecaster
from src.models.model_comparison import model_comparator

eval_res = forecaster.train_models_for_entity("India", train_cutoff_year=2015)
table_df = model_comparator.get_comparison_table(eval_res)
print("Model Comparison Benchmark:")
table_df"""),
    code_cell("""# Multi-step recursive forecast into 2026-2035
fc_df = forecaster.generate_recursive_forecast("India", eval_res["best_model_name"], horizon_years=10)
fc_df.head(10)""")
])

# 5. 05_anomaly_detection.ipynb
nb5 = make_notebook([
    md_cell("# CarbonScope 2.0 — Notebook 05: Anomaly Radar & Detection\n\nImplements Unsupervised Isolation Forest and Statistical Z-Score detectors with automated root-cause explanations."),
    code_cell("""import os, sys
sys.path.insert(0, "..")
from src.anomaly.statistical_detection import statistical_detector
from src.anomaly.isolation_forest import iso_detector

anom_z = statistical_detector.detect_trajectory_anomalies("India", z_threshold=2.0)
print(f"Z-Score Anomalies ({len(anom_z[anom_z['Is_Anomaly']])}):")
anom_z[anom_z['Is_Anomaly']][["Year", "Emissions_MtCO2eq", "Z_Score", "Explanation"]]"""),
    code_cell("""iso_anom = iso_detector.detect_anomalies("India", contamination=0.08)
print(f"Isolation Forest Anomalies ({len(iso_anom[iso_anom['Is_Anomaly']])}):")
iso_anom[iso_anom['Is_Anomaly']][["Year", "Emissions_MtCO2eq", "Anomaly_Score", "Explanation"]]""")
])

# 6. 06_shap_analysis.ipynb
nb6 = make_notebook([
    md_cell("# CarbonScope 2.0 — Notebook 06: Explainable AI with SHAP\n\nComputes TreeSHAP feature attributions, beeswarm metrics, and individual prediction waterfall decompositions."),
    code_cell("""import os, sys
sys.path.insert(0, "..")
from src.explainability.shap_analysis import shap_engine

# Global SHAP
global_res = shap_engine.compute_global_shap("India", "Random Forest")
print("Global Feature Importance Ranking:")
global_res["global_importance_table"]"""),
    code_cell("""# Individual waterfall decomposition for 2025
wf = shap_engine.compute_individual_waterfall("India", "Random Forest", 2025)
print(f"Base E[f(X)]: {wf['base_value_mt']} Mt -> Pred: {wf['prediction_mt']} Mt")
wf["waterfall_table"]""")
])

# Save all notebooks
notebooks = {
    "01_data_exploration.ipynb": nb1,
    "02_data_preprocessing.ipynb": nb2,
    "03_feature_engineering.ipynb": nb3,
    "04_model_training.ipynb": nb4,
    "05_anomaly_detection.ipynb": nb5,
    "06_shap_analysis.ipynb": nb6
}

for name, nb in notebooks.items():
    path = os.path.join(NOTEBOOKS_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print(f"Saved: {path}")

print("All 6 Jupyter notebooks generated successfully!")

