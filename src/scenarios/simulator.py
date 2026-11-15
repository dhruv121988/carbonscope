"""
CarbonScope 2.0 - What-If Climate Scenario Simulator
Simulates mathematical model response to hypothetical adjustments in sectoral emissions,
momentum growth rates, and efficiency pathways.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from src.features.feature_engineering import feature_engine
from src.models.forecasting import forecaster
from src.analysis.emission_analysis import analyzer


class ScenarioSimulatorEngine:
    """Interactively compares baseline forecasting trajectories with hypothetical climate scenarios."""

    SCIENTIFIC_DISCLAIMER = (
        "SCIENTIFIC NOTICE: This simulation illustrates how the trained machine learning model "
        "responds to modified inputs. It does NOT represent a verified physical, macroeconomic, "
        "or policy causal model. Real-world decarbonization involves non-linear grid dynamics, "
        "supply chain constraints, and technological transitions that are not fully captured by statistical regression."
    )

    @staticmethod
    def run_scenario_simulation(
        country: str = "India",
        model_name: str = "Linear Regression",
        horizon_years: int = 10,
        sector_adjustment_name: Optional[str] = "Power Industry",
        sector_pct_change: float = -20.0,
        growth_damping_factor: float = 0.85
    ) -> Dict[str, Any]:
        """
        Run paired baseline and hypothetical scenario forecast for a given entity.
        - sector_pct_change: hypothetical % shift in target sector emissions (e.g. -20% for aggressive renewables)
        - growth_damping_factor: multiplier applied to lag growth rates (e.g. 0.85 for decelerating trajectory)
        """
        # Ensure model is trained
        cache_key = f"{country}:{model_name}"
        if cache_key not in forecaster.trained_models:
            forecaster.train_models_for_entity(country)
        model = forecaster.trained_models[cache_key]

        # 1. Baseline Forecast
        baseline_df = forecaster.generate_recursive_forecast(
            country=country,
            model_name=model_name,
            horizon_years=horizon_years,
            start_year=2026
        )

        # 2. Scenario Forecast
        # Calculate national impact of sectoral adjustment
        traj = analyzer.get_country_trajectory(country)
        featured = feature_engine.create_features_for_series(traj["Emissions_MtCO2eq"], traj["Year"])
        rolling_tail = featured.tail(10)[["Year", "Target"]].copy()

        # If a sector adjustment is specified, compute sector's share in 2025
        sector_weight = 1.0
        if sector_adjustment_name:
            sec_df = analyzer.get_sector_breakdown(country, 2025)
            match = sec_df[sec_df["Sector"].str.lower() == sector_adjustment_name.lower()]
            if not match.empty:
                sector_weight = match["Sector_Share_Pct"].values[0] / 100.0

        # Effective national reduction percentage
        # E.g. -20% in Power (38.4% share) = -7.68% national reduction per year
        effective_shift_pct = (sector_pct_change / 100.0) * sector_weight

        scenario_rows = []
        current_year = 2026

        for step in range(horizon_years):
            base_val = baseline_df.loc[step, "Forecasted_MtCO2eq"]
            
            # Progressive decarbonization over the horizon window
            # Year 1 achieves (1/horizon)*effective_shift, Year 10 achieves full effective_shift
            progress_ratio = (step + 1) / horizon_years
            annual_shift = effective_shift_pct * progress_ratio
            
            # Apply growth damping if specified
            growth_damping_effect = (growth_damping_factor ** (step + 1))
            
            # Scenario prediction
            scen_pred = max(0.0, base_val * (1.0 + annual_shift) * growth_damping_effect)
            
            abs_diff = scen_pred - base_val
            pct_diff = (abs_diff / base_val * 100) if base_val > 0 else 0.0

            scenario_rows.append({
                "Year": current_year,
                "Baseline_MtCO2eq": round(base_val, 2),
                "Scenario_MtCO2eq": round(scen_pred, 2),
                "Absolute_Delta_Mt": round(abs_diff, 2),
                "Pct_Delta": round(pct_diff, 2),
                "Country": country,
                "Model": model_name
            })
            current_year += 1

        comparison_df = pd.DataFrame(scenario_rows)

        # Terminal horizon year metrics (e.g. 2035)
        terminal = comparison_df.iloc[-1]
        cumulative_saved = (comparison_df["Baseline_MtCO2eq"] - comparison_df["Scenario_MtCO2eq"]).sum()

        return {
            "country": country,
            "model_name": model_name,
            "horizon_years": horizon_years,
            "sector_adjusted": sector_adjustment_name,
            "sector_pct_change": sector_pct_change,
            "national_implied_shift_pct": round(effective_shift_pct * 100, 2),
            "growth_damping_factor": growth_damping_factor,
            "terminal_year": int(terminal["Year"]),
            "terminal_baseline_mt": float(terminal["Baseline_MtCO2eq"]),
            "terminal_scenario_mt": float(terminal["Scenario_MtCO2eq"]),
            "terminal_abs_delta_mt": float(terminal["Absolute_Delta_Mt"]),
            "terminal_pct_delta": float(terminal["Pct_Delta"]),
            "cumulative_emissions_avoided_mt": round(float(cumulative_saved), 2),
            "comparison_timeline": comparison_df,
            "disclaimer": ScenarioSimulatorEngine.SCIENTIFIC_DISCLAIMER
        }


scenario_simulator = ScenarioSimulatorEngine()

if __name__ == "__main__":
    print("Testing ScenarioSimulatorEngine...")
    sim = scenario_simulator.run_scenario_simulation(
        country="India",
        model_name="Linear Regression",
        horizon_years=10,
        sector_adjustment_name="Power Industry",
        sector_pct_change=-25.0
    )
    print("Terminal Year:", sim["terminal_year"])
    print(f"Baseline: {sim['terminal_baseline_mt']:.1f} Mt vs Scenario: {sim['terminal_scenario_mt']:.1f} Mt")
    print(f"Delta: {sim['terminal_abs_delta_mt']:+.1f} Mt ({sim['terminal_pct_delta']:+.2f}%)")
    print(f"Cumulative Avoided Emissions: {sim['cumulative_emissions_avoided_mt']:,.1f} Mt CO2eq")
