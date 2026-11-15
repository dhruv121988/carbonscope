"""
CarbonScope 2.0 - Module 7: What-If Climate Scenario Simulator
Interactive simulation environment comparing baseline ML predictions
against hypothetical sectoral decarbonization and efficiency interventions.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any

from dashboard.ui_components import (
    COLORS,
    get_current_palette,
    get_plotly_layout,
    render_metric_card,
    render_page_header,
    render_disclaimer_card,
    render_html
)
from src.scenarios.simulator import scenario_simulator
from src.analysis.emission_analysis import analyzer


def render_scenario_simulator():
    """Render Module 7: What-If Scenario Simulator."""
    c = get_current_palette()

    render_page_header(
        title="What-If Climate Scenario Simulator",
        subtitle="Simulate mathematical trajectory divergence under hypothetical sectoral decarbonization and efficiency targets.",
        badge="SCENARIO MODELLING"
    )

    # Mandatory Scientific Disclaimer
    render_disclaimer_card(
        text="SCIENTIFIC DISCLAIMER: Scenario outputs are model-based hypotheticals derived from empirical historical correlations, not guaranteed real-world policy outcomes. Sliders reflect hypothetical trajectory adjustments and do not imply causal mechanisms unsupported by the underlying statistical model.",
        title="Scientific Simulation Notice"
    )

    # Interactive Policy Controls Card
    render_html(f"""
    <div style="font-size: 1.05rem; font-weight: 700; color: {c['text_dark']}; margin-bottom: 12px;">
        Policy Intervention Parameters & Sensitivity Controls
    </div>
    """)

    ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([1.5, 1.5, 1.5])
    all_c = analyzer.get_available_countries()
    with ctrl_c1:
        country = st.selectbox("Simulation Entity", all_c, index=all_c.index("India") if "India" in all_c else 0, key="sim_country")
        model_name = st.selectbox("Underlying Regression Model", ["Linear Regression", "Random Forest", "Gradient Boosting"], index=0)

    sectors = analyzer.get_available_sectors()
    with ctrl_c2:
        target_sector = st.selectbox("Target Sector to Intervene", ["All Sectors (National)"] + sectors, index=1 if len(sectors) > 0 else 0)
        sec_param = None if target_sector == "All Sectors (National)" else target_sector
        sector_shift = st.slider("Target Emission Adjustment (%)", min_value=-50, max_value=30, value=-20, step=5, help="Hypothetical reduction or expansion in target sector emissions.")

    with ctrl_c3:
        growth_damping = st.slider("Growth Damping Multiplier", min_value=0.70, max_value=1.00, value=0.90, step=0.05, help="Deceleration applied to annual trajectory momentum.")
        sim_horizon = st.slider("Simulation Horizon (Years)", min_value=5, max_value=15, value=10, step=1)

    # Execute simulation
    sim_res = scenario_simulator.run_scenario_simulation(
        country=country,
        model_name=model_name,
        horizon_years=sim_horizon,
        sector_adjustment_name=sec_param,
        sector_pct_change=float(sector_shift),
        growth_damping_factor=float(growth_damping)
    )

    term_yr = sim_res["terminal_year"]
    base_val = sim_res["terminal_baseline_mt"]
    scen_val = sim_res["terminal_scenario_mt"]
    abs_delta = sim_res["terminal_abs_delta_mt"]
    pct_delta = sim_res["terminal_pct_delta"]
    cum_avoided = sim_res["cumulative_emissions_avoided_mt"]

    # 1. Headline Impact Cards: BASELINE vs HYPOTHETICAL SCENARIO
    render_html(f"""
    <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: {c['muted']}; margin-top: 20px; margin-bottom: 8px;">
        BASELINE VS HYPOTHETICAL SCENARIO COMPARISON (TERMINAL YEAR {term_yr})
    </div>
    """)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            title=f"Baseline Pred ({term_yr})",
            value=f"{base_val:,.1f}",
            unit="Mt CO₂eq",
            delta_text=f"Model: {model_name}",
            is_reduction_positive=False,
            badge="REFERENCE BASELINE"
        )
    with c2:
        render_metric_card(
            title=f"Scenario Pred ({term_yr})",
            value=f"{scen_val:,.1f}",
            unit="Mt CO₂eq",
            delta_text=f"Shift: {sim_res['national_implied_shift_pct']:+.1f}% Nat'l",
            is_reduction_positive=True,
            badge="HYPOTHETICAL"
        )
    with c3:
        render_metric_card(
            title="Terminal Year Delta",
            value=f"{abs_delta:+,.1f}",
            unit="Mt CO₂eq",
            delta_text=f"{pct_delta:+.2f}% Divergence",
            is_reduction_positive=True,
            badge=f"YEAR {term_yr}"
        )
    with c4:
        render_metric_card(
            title="Cumulative Avoided Carbon",
            value=f"{cum_avoided:,.1f}",
            unit="Mt CO₂eq",
            delta_text=f"{sim_horizon}-Year Cumulative",
            is_reduction_positive=True,
            badge="AVOIDED WEDGE"
        )

    render_html("<div style='height: 16px;'></div>")

    # 2. Main Comparative Trajectory Chart
    render_html(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
            {country}: Baseline Reference vs Hypothetical Policy Pathway (2026 – {term_yr})
        </span>
        <span class="pill-mint">AVOIDED CARBON WEDGE</span>
    </div>
    """)

    comp_df = sim_res["comparison_timeline"]
    traj_hist = analyzer.get_country_trajectory(country)
    hist_tail = traj_hist.tail(15)

    fig_sim = go.Figure()

    # Historical segment (2010 to 2025)
    fig_sim.add_trace(go.Scatter(
        x=hist_tail["Year"],
        y=hist_tail["Emissions_MtCO2eq"],
        mode="lines+markers",
        name="Historical Observations",
        line=dict(color="#093326", width=2),
        marker=dict(size=4),
        hovertemplate="<b>Historical %{x}</b><br>%{y:,.1f} Mt CO₂eq<extra></extra>"
    ))

    # Baseline forecast
    fig_sim.add_trace(go.Scatter(
        x=comp_df["Year"],
        y=comp_df["Baseline_MtCO2eq"],
        mode="lines+markers",
        name=f"Baseline Reference ({model_name})",
        line=dict(color="#0284C7", width=2.5, dash="dash"),
        marker=dict(size=5),
        hovertemplate="<b>Baseline %{x}</b><br>%{y:,.1f} Mt CO₂eq<extra></extra>"
    ))

    # Hypothetical scenario
    fig_sim.add_trace(go.Scatter(
        x=comp_df["Year"],
        y=comp_df["Scenario_MtCO2eq"],
        mode="lines+markers",
        name="Hypothetical Policy Pathway",
        line=dict(color="#059669", width=3),
        marker=dict(size=6),
        hovertemplate="<b>Scenario %{x}</b><br>%{y:,.1f} Mt CO₂eq<extra></extra>"
    ))

    # Shaded corridor between baseline and scenario
    fig_sim.add_trace(go.Scatter(
        x=comp_df["Year"].tolist() + comp_df["Year"].tolist()[::-1],
        y=comp_df["Baseline_MtCO2eq"].tolist() + comp_df["Scenario_MtCO2eq"].tolist()[::-1],
        fill="toself",
        fillcolor="rgba(16, 185, 129, 0.16)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name="Avoided Carbon Wedge"
    ))

    layout_sim = get_plotly_layout(height=420)
    layout_sim.yaxis.title = "Emissions (Mt CO₂eq)"
    layout_sim.xaxis.title = "Projection Year"
    fig_sim.update_layout(layout_sim)
    st.plotly_chart(fig_sim, use_container_width=True)

    # 3. Granular Comparison Schedule Table
    render_html(f"""
    <div style="margin-top: 24px; margin-bottom: 12px;">
        <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
            Paired Annual Trajectory Comparison Schedule (2026 – {term_yr})
        </span>
        <p style="font-size: 0.88rem; color: {c['muted']}; margin-top: 4px; margin-bottom: 16px;">
            Year-by-year baseline vs scenario figures, absolute avoided carbon, and percentage delta.
        </p>
    </div>
    """)

    st.dataframe(comp_df, use_container_width=True)
