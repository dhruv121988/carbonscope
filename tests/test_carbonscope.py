"""
CarbonScope 2.0 - Comprehensive Unit & Integration Test Suite
Validates the entire machine learning lifecycle:
1. Data Acquisition & Integrity
2. Preprocessing & Quality Audit
3. Feature Engineering & Leakage Prevention
4. Model Training & Chronological Validation
5. Anomaly Detection & Attribution
6. Explainable AI (SHAP & Permutation)
7. What-If Scenario Simulation
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import numpy as np
import pandas as pd


class TestCarbonScopeLifecycle(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensure clean processed datasets exist prior to tests."""
        from src.preprocessing.cleaner import cleaner
        cleaner.run_all()

    # 1. Data Acquisition Tests
    def test_01_loader_totals_non_empty(self):
        from src.data_acquisition.data_loader import loader
        df = loader.load_ghg_totals()
        self.assertFalse(df.empty, "GHG totals dataframe should not be empty")
        self.assertIn("Country", df.columns)
        self.assertIn("EDGAR Country Code", df.columns)
        self.assertTrue(any("India" in str(c) for c in df["Country"].dropna()))

    def test_02_loader_sectors_non_empty(self):
        from src.data_acquisition.data_loader import loader
        df = loader.load_ghg_sectors()
        self.assertFalse(df.empty)
        self.assertIn("Sector", df.columns)
        self.assertIn("Substance", df.columns)

    def test_03_pdf_report_metadata(self):
        from src.data_acquisition.data_loader import loader
        pdf_info = loader.load_pdf_report_metadata()
        self.assertTrue(pdf_info["available"])
        self.assertGreater(pdf_info["page_count"], 250, "EDGAR 2026 report PDF should have ~300 pages")

    # 2. Preprocessing & Validation Tests
    def test_04_validator_totals_schema(self):
        from src.data_acquisition.data_loader import loader
        from src.preprocessing.validator import validator
        raw_t = loader.load_ghg_totals()
        is_valid, issues = validator.validate_totals_schema(raw_t)
        self.assertTrue(is_valid, f"Validation issues found: {issues}")

    def test_05_cleaner_master_panel(self):
        master_path = os.path.join(BASE_DIR, "data", "processed", "master_emissions_panel.parquet")
        self.assertTrue(os.path.exists(master_path), "Master panel parquet file must exist")
        df = pd.read_parquet(master_path)
        self.assertIn("Country", df.columns)
        self.assertIn("Year", df.columns)
        self.assertIn("Emissions_MtCO2eq", df.columns)
        self.assertIn("Is_Aggregate", df.columns)

        # Check aggregate separation
        ind = df[df["Country"] == "India"]
        self.assertFalse(ind.iloc[0]["Is_Aggregate"], "India should not be marked as aggregate")
        glob = df[df["Country"] == "GLOBAL TOTAL"]
        self.assertTrue(glob.iloc[0]["Is_Aggregate"], "GLOBAL TOTAL should be marked as aggregate")

    def test_06_data_quality_audit(self):
        from src.preprocessing.quality_audit import auditor
        audit_rep = auditor.generate_full_audit()
        self.assertIn("integrity_verification", audit_rep)
        self.assertGreaterEqual(audit_rep["integrity_verification"]["overall_health_score_pct"], 99.0)
        self.assertEqual(audit_rep["datasets"]["master_panel"]["duplicate_records"], 0, "There should be zero duplicates")

    # 3. Feature Engineering Tests
    def test_07_feature_engineering_zero_leakage(self):
        from src.features.feature_engineering import feature_engine
        train_df, test_df, f_cols = feature_engine.prepare_country_dataset("India", train_cutoff_year=2015)

        self.assertEqual(train_df["Year"].max(), 2015, "Training set should stop strictly at cutoff year 2015")
        self.assertEqual(test_df["Year"].min(), 2016, "Testing set should start strictly at cutoff year + 1 (2016)")
        self.assertEqual(test_df["Year"].max(), 2025, "Testing set should end at latest observation 2025")

        # Verify all feature columns are present and non-empty
        for col in f_cols:
            self.assertIn(col, train_df.columns)
            self.assertFalse(train_df[col].isnull().any(), f"Feature column '{col}' should not have NaNs in train set")

    # 4. Model Training & Validation Tests
    def test_08_forecasting_models_training(self):
        from src.models.forecasting import forecaster
        res = forecaster.train_models_for_entity("India", train_cutoff_year=2015)
        self.assertIn("best_model_name", res)
        self.assertIn("Linear Regression", res["models"])
        self.assertIn("Random Forest", res["models"])

        # Linear regression should achieve positive test R2
        lr_test_r2 = res["models"]["Linear Regression"]["test_metrics"]["R2"]
        self.assertGreater(lr_test_r2, 0.5, "Linear regression should generalize well on test window")

    def test_09_recursive_forecasting(self):
        from src.models.forecasting import forecaster
        fc = forecaster.generate_recursive_forecast("India", "Linear Regression", horizon_years=10, start_year=2026)
        self.assertEqual(len(fc), 10, "Should generate exactly 10 future years")
        self.assertEqual(fc.iloc[0]["Year"], 2026)
        self.assertEqual(fc.iloc[-1]["Year"], 2035)

        # Confidence bounds check
        for _, row in fc.iterrows():
            self.assertLessEqual(row["Confidence_Lower_95"], row["Forecasted_MtCO2eq"])
            self.assertGreaterEqual(row["Confidence_Upper_95"], row["Forecasted_MtCO2eq"])

    # 5. Anomaly Detection Tests
    def test_10_statistical_anomaly_detection(self):
        from src.anomaly.statistical_detection import statistical_detector
        anom = statistical_detector.detect_trajectory_anomalies("India", z_threshold=2.0)
        self.assertIn("Is_Anomaly", anom.columns)
        self.assertIn("Explanation", anom.columns)

        # 2020 COVID shock check
        covid = anom[anom["Year"] == 2020]
        self.assertFalse(covid.empty)

    def test_11_isolation_forest_detection(self):
        from src.anomaly.isolation_forest import iso_detector
        iso_res = iso_detector.detect_anomalies("India", contamination=0.08)
        self.assertIn("Anomaly_Score", iso_res.columns)
        self.assertTrue(any(iso_res["Is_Anomaly"]), "Isolation Forest should identify at least one anomaly")

    # 6. Explainable AI Tests
    def test_12_shap_global_and_waterfall(self):
        from src.explainability.shap_analysis import shap_engine
        g_res = shap_engine.compute_global_shap("India", "Random Forest")
        self.assertIn("global_importance_table", g_res)
        self.assertGreater(len(g_res["global_importance_table"]), 5)

        wf = shap_engine.compute_individual_waterfall("India", "Random Forest", 2025)
        self.assertIn("waterfall_table", wf)
        self.assertIn("base_value_mt", wf)
        self.assertIn("prediction_mt", wf)

    # 7. Scenario Simulator Tests
    def test_13_scenario_simulation_divergence(self):
        from src.scenarios.simulator import scenario_simulator
        sim = scenario_simulator.run_scenario_simulation(
            country="India",
            model_name="Linear Regression",
            horizon_years=10,
            sector_adjustment_name="Power Industry",
            sector_pct_change=-25.0
        )
        self.assertEqual(sim["terminal_year"], 2035)
        # Reduction should cause scenario value to be lower than baseline
        self.assertLess(sim["terminal_scenario_mt"], sim["terminal_baseline_mt"], "Negative sector shift should reduce terminal emissions")
        self.assertGreater(sim["cumulative_emissions_avoided_mt"], 0, "Cumulative avoided emissions should be positive for reduction scenario")


if __name__ == "__main__":
    unittest.main()

