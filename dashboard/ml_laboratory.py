"""
CarbonScope 2.0 - Module 4: Machine Learning Laboratory
Emission forecasting engine implementing Linear Regression, SVR,
Random Forest, and Gradient Boosting with chronological holdout validation.
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
from src.models.forecasting import forecaster
from src.models.model_comparison import model_comparator
from src.analysis.emission_analysis import analyzer


def render_ml_laboratory():
    """Render Module 4: Machine Learning Laboratory."""
    c = get_current_palette()

    render_page_header(
        title="Machine Learning Laboratory: Emission Forecasting",
        subtitle="Chronologically validated regression architectures, residual diagnostics, and recursive decadal projections.",
        badge="SUPERVISED ML ENGINE"
    )

    # Top Configuration Panel
    with st.container():
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.5, 1.5])
        all_c = analyzer.get_available_countries()
        with ctrl_col1:
            country = st.selectbox(
                "Forecasting Target Entity",
                all_c,
                index=all_c.index("India") if "India" in all_c else 0,
                help="Sovereign nation or aggregate whose greenhouse gas trajectory will be modeled."
            )
        with ctrl_col2:
            train_cutoff = st.slider(
                "Chronological Train Cutoff Year",
                min_value=2005,
                max_value=2020,
                value=2015,
                step=1,
                help="Strict temporal holdout boundary. Models train strictly on years <= Cutoff and are tested on unseen years (Cutoff+1 to 2025)."
            )
        with ctrl_col3:
            horizon = st.slider(
                "Forecast Horizon (Years ahead)",
                min_value=5,
                max_value=15,
                value=10,
                step=1,
                help="Number of future years to forecast recursively (up to 2035+)."
            )

    # Execute training and evaluation
    with st.spinner(f"Training chronological forecasting architectures for {country}..."):
        eval_res = forecaster.train_models_for_entity(country, train_cutoff_year=train_cutoff)

    best_model_name = eval_res["best_model_name"]
    best_test_rmse = eval_res["best_test_rmse"]
    best_model_data = eval_res["models"][best_model_name]
    te_m = best_model_data["test_metrics"]

    # 1. Headline Model Performance Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            title="Best Model Architecture",
            value=best_model_name,
            unit="",
            delta_text=f"RMSE: {best_test_rmse:.2f} Mt",
            is_reduction_positive=True,
            badge="LEADER"
        )
    with c2:
        render_metric_card(
            title=f"Test MAE ({best_model_name})",
            value=f"{te_m['MAE']:.2f}",
            unit="Mt CO₂eq",
            delta_text="Mean Absolute Error",
            is_reduction_positive=True,
            badge=f"TEST: {train_cutoff+1}–2025"
        )
    with c3:
        render_metric_card(
            title="Test RMSE Score",
            value=f"{te_m['RMSE']:.2f}",
            unit="Mt CO₂eq",
            delta_text=f"MSE: {te_m['MSE']:,.0f} (Mt)²",
            is_reduction_positive=True,
            badge="QUADRATIC PENALTY"
        )
    with c4:
        r2_val = te_m["R2"]
        render_metric_card(
            title="Out-of-Sample R² Fit",
            value=f"{r2_val:.4f}",
            unit="",
            delta_text=f"MAPE: {te_m['MAPE_pct']:.2f}%",
            is_reduction_positive=False,
            badge="DETERMINATION"
        )

    render_html("<div style='height: 16px;'></div>")

    tab1, tab2, tab3 = st.tabs([
        "🔮 Forecast Trajectory & Confidence Corridor",
        "⚖️ Multi-Model Benchmark & Overfitting Check",
        "🔬 Residual Diagnostics & Error Breakdown"
    ])

    # Tab 1: Trajectory & Forecast
    with tab1:
        model_to_plot = st.selectbox(
            "Select Architecture to Visualize",
            list(forecaster.AVAILABLE_MODELS.keys()),
            index=list(forecaster.AVAILABLE_MODELS.keys()).index(best_model_name)
        )

        render_html(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
                {country}: Historical Observations vs {model_to_plot} Forecast ({train_cutoff+1} – {2025+horizon})
            </span>
            <span class="pill-forest">95% CONFIDENCE CORRIDOR</span>
        </div>
        """)

        # Generate future forecast
        fc_df = forecaster.generate_recursive_forecast(
            country=country,
            model_name=model_to_plot,
            horizon_years=horizon,
            start_year=2026
        )

        hist_years = eval_res["historical_data"]["years"]
        hist_actuals = eval_res["historical_data"]["actuals"]

        fig_fc = go.Figure()

        # 1. Historical Actuals (1975 to 2025)
        fig_fc.add_trace(go.Scatter(
            x=hist_years,
            y=hist_actuals,
            mode="lines+markers",
            name="EDGAR Historical Actuals (1975–2025)",
            line=dict(color="#093326", width=2.5),
            marker=dict(size=4, color="#093326"),
            hovertemplate="<b>Actual Year %{x}</b><br>%{y:,.1f} Mt CO₂eq<extra></extra>"
        ))

        # 2. Test Predictions (Validation Window)
        m_res = eval_res["models"][model_to_plot]
        fig_fc.add_trace(go.Scatter(
            x=m_res["test_years"],
            y=m_res["test_predictions"],
            mode="lines+markers",
            name=f"{model_to_plot} Test Validation ({train_cutoff+1}–2025)",
            line=dict(color="#0284C7", width=2.5, dash="dash"),
            marker=dict(size=6, symbol="diamond"),
            hovertemplate="<b>Val Pred Year %{x}</b><br>%{y:,.1f} Mt CO₂eq<extra></extra>"
        ))

        # 3. Future Projections (2026 to 2025+horizon)
        fig_fc.add_trace(go.Scatter(
            x=fc_df["Year"],
            y=fc_df["Forecasted_MtCO2eq"],
            mode="lines+markers",
            name=f"{model_to_plot} Future Projections (2026–{2025+horizon})",
            line=dict(color="#059669", width=3),
            marker=dict(size=6),
            hovertemplate="<b>Future Year %{x}</b><br>Forecast: %{y:,.1f} Mt CO₂eq<extra></extra>"
        ))

        # 4. Confidence Corridor (Upper & Lower 95%)
        fig_fc.add_trace(go.Scatter(
            x=fc_df["Year"].tolist() + fc_df["Year"].tolist()[::-1],
            y=fc_df["Confidence_Upper_95"].tolist() + fc_df["Confidence_Lower_95"].tolist()[::-1],
            fill="toself",
            fillcolor="rgba(16, 185, 129, 0.12)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            name="95% Uncertainty Corridor"
        ))

        layout_fc = get_plotly_layout(height=420)
        layout_fc.yaxis.title = "Emissions (Mt CO₂eq)"
        layout_fc.xaxis.title = "Year"
        fig_fc.update_layout(layout_fc)
        st.plotly_chart(fig_fc, use_container_width=True)

        render_disclaimer_card(
            text=f"Historical training observations end at year {train_cutoff}. Observations between {train_cutoff+1} and 2025 serve as unseen out-of-sample test data. Future forecasts (2026+) are generated recursively using the model's own predictions as lag inputs.",
            title="Chronological Holdout Split Protocol"
        )

    # Tab 2: Model Benchmark Table
    with tab2:
        render_html(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
                Comparative Scorecard: Chronological Holdout Evaluation
            </span>
            <span class="pill-forest">TRAIN VS TEST INTEGRITY</span>
        </div>
        <p style="font-size: 0.88rem; color: {c['muted']}; margin-bottom: 16px;">
            Directly contrasts in-sample training metrics with unseen out-of-sample testing metrics to detect overfitting transparently.
        </p>
        """)

        bench_df = model_comparator.get_comparison_table(eval_res)
        st.dataframe(bench_df, use_container_width=True)

        render_html(f"""
        <div style="background: {c['surface_subtle']}; border: 1px solid {c['border']}; border-left: 4px solid #059669; border-radius: 12px; padding: 16px 20px; margin-top: 16px;">
            <div style="font-weight: 700; font-size: 0.88rem; color: {c['text_dark']};">
                ACADEMIC DEFENSE NOTE: Time-Series Extrapolation Mechanics
            </div>
            <p style="font-size: 0.84rem; color: {c['muted']}; margin-top: 6px; line-height: 1.5;">
                In non-stationary time series characterized by strong macroeconomic growth (such as India's emissions expanding from 3,100 Mt in 2015 to 4,508 Mt in 2025), tree ensembles (Random Forest, Gradient Boosting) cannot predict values outside the range of their training targets. Consequently, linear models equipped with lagged momentum and growth rate features often extrapolate secular trends with superior test fidelity.
            </p>
        </div>
        """)

    # Tab 3: Residuals
    with tab3:
        render_html(f"""
        <div style="margin-bottom: 14px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
                Residual Diagnostics for {model_to_plot} (Validation Window {train_cutoff+1}–2025)
            </span>
            <p style="font-size: 0.88rem; color: {c['muted']}; margin-top: 4px; margin-bottom: 16px;">
                Residuals = Actual Observed Emissions - Predicted Model Emissions.
            </p>
        </div>
        """)

        res_df = m_res["residuals"]

        fig_res = go.Figure()
        fig_res.add_trace(go.Bar(
            x=res_df["Year"],
            y=res_df["Residual"],
            marker=dict(
                color=["#DC2626" if r > 0 else "#059669" for r in res_df["Residual"]],
                line=dict(color=c["surface"], width=1)
            ),
            text=res_df["Residual"].apply(lambda v: f"{v:+.1f} Mt"),
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color=c["text"]),
            hovertemplate="<b>Year %{x}</b><br>Actual: %{customdata[0]:,.1f} Mt<br>Pred: %{customdata[1]:,.1f} Mt<br>Residual: %{y:+.1f} Mt<extra></extra>",
            customdata=res_df[["Actual", "Predicted"]]
        ))

        # Zero reference line
        fig_res.add_hline(y=0, line_dash="solid", line_color=c["muted"], line_width=1.5)

        layout_res = get_plotly_layout(height=340)
        layout_res.yaxis.title = "Residual (Mt CO₂eq)"
        layout_res.xaxis.title = "Validation Year"
        fig_res.update_layout(layout_res)
        st.plotly_chart(fig_res, use_container_width=True)

        st.dataframe(res_df, use_container_width=True)
