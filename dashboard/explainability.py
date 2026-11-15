"""
CarbonScope 2.0 - Module 6: Explainability Centre
XAI Investigator implementing SHAP (TreeSHAP/KernelSHAP) and Permutation Importance
to decode global feature importance and individual prediction waterfalls.
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
from src.explainability.shap_analysis import shap_engine
from src.explainability.feature_importance import feature_importance_engine
from src.models.forecasting import forecaster
from src.analysis.emission_analysis import analyzer


def render_explainability():
    """Render Module 6: Explainability Centre."""
    c = get_current_palette()

    render_page_header(
        title="Explainability Centre (XAI Investigator)",
        subtitle="SHAP feature attributions, local prediction waterfalls, and model interpretability diagnostics.",
        badge="SHAP (SHAPLEY ADDITIVE EXPLANATIONS)"
    )

    # Mandatory Scientific Disclaimer required by specification
    render_disclaimer_card(
        text="These values describe how model inputs influenced its prediction. They do not establish real-world causation.",
        title="Explainable AI Causality Notice"
    )

    # Top Controls
    ctrl1, ctrl2 = st.columns([2, 2])
    all_c = analyzer.get_available_countries()
    with ctrl1:
        country = st.selectbox(
            "Entity for Attribution Analysis",
            all_c,
            index=all_c.index("India") if "India" in all_c else 0,
            key="xai_country"
        )
    with ctrl2:
        model_name = st.selectbox(
            "Explainable Model Architecture",
            ["Random Forest", "Gradient Boosting", "Linear Regression"],
            index=0
        )

    # Compute Global SHAP
    with st.spinner(f"Computing SHAP values for {model_name} on {country}..."):
        shap_res = shap_engine.compute_global_shap(country, model_name)

    base_val = shap_res["base_value_mt"]
    global_df = shap_res["global_importance_table"]
    top_feature = global_df.iloc[0]["Feature"]
    top_impact = global_df.iloc[0]["Mean_Abs_SHAP"]

    # 1. Headline Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            title="Model Architecture",
            value=model_name,
            unit="",
            delta_text=f"Target: {country}",
            is_reduction_positive=False,
            badge="ACTIVE"
        )
    with c2:
        render_metric_card(
            title="Base Value E[f(X)]",
            value=f"{base_val:,.1f}",
            unit="Mt CO₂eq",
            delta_text="Expected Training Mean",
            is_reduction_positive=False,
            badge="EXPECTATION"
        )
    with c3:
        render_metric_card(
            title="Top Influential Feature",
            value=top_feature,
            unit="",
            delta_text=f"|SHAP|: {top_impact:.1f} Mt",
            is_reduction_positive=False,
            badge="MAX IMPACT"
        )
    with c4:
        render_metric_card(
            title="Explanation Method",
            value="TreeSHAP" if "Forest" in model_name or "Boosting" in model_name else "LinearSHAP",
            unit="",
            delta_text="Exact Shapley Values",
            is_reduction_positive=False,
            badge="GAME THEORY"
        )

    render_html("<div style='height: 16px;'></div>")

    tab1, tab2, tab3 = st.tabs([
        "🌊 Individual Prediction Waterfall",
        "📊 Global Feature Importance (|SHAP|)",
        "🔄 Permutation Importance vs Intrinsic Weights"
    ])

    # Tab 1: Individual Prediction Waterfall
    with tab1:
        render_html(f"""
        <div style="margin-bottom: 14px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
                Local Prediction Inspector: SHAP Waterfall Decomposition
            </span>
            <p style="font-size: 0.88rem; color: {c['muted']}; margin-top: 4px; margin-bottom: 16px;">
                Inspect how each input feature pushed the model prediction higher (+) or lower (-) from the baseline expected value for a chosen year.
            </p>
        </div>
        """)

        avail_years = shap_res["test_years"]
        target_yr = st.selectbox("Select Test Year to Decompose", avail_years, index=len(avail_years) - 1)

        wf_res = shap_engine.compute_individual_waterfall(country, model_name, target_yr)
        wf_table = wf_res["waterfall_table"]

        # Build Plotly Waterfall chart
        fig_wf = go.Figure(go.Waterfall(
            name="SHAP Force",
            orientation="v",
            measure=["absolute"] + ["relative"] * len(wf_table) + ["total"],
            x=["Base E[f(X)]"] + wf_table["Feature"].tolist() + [f"Final Pred ({target_yr})"],
            textposition="outside",
            text=[f"{wf_res['base_value_mt']:.0f}"] + [f"{phi:+.1f}" for phi in wf_table["SHAP_Impact_Mt"]] + [f"{wf_res['prediction_mt']:.0f}"],
            y=[wf_res["base_value_mt"]] + wf_table["SHAP_Impact_Mt"].tolist() + [0],
            connector={"line": {"color": c["border"]}},
            decreasing={"marker": {"color": "#059669"}},  # Lowering emissions is green
            increasing={"marker": {"color": "#DC2626"}},  # Pushing emissions higher is coral
            totals={"marker": {"color": "#093326"}}
        ))

        layout_wf = get_plotly_layout(height=420)
        layout_wf.yaxis.title = "Emissions Contribution (Mt CO₂eq)"
        layout_wf.xaxis.title = "Feature Force Decomposition"
        layout_wf.xaxis.tickangle = -35
        fig_wf.update_layout(layout_wf)
        st.plotly_chart(fig_wf, use_container_width=True)

        st.dataframe(wf_table, use_container_width=True)

    # Tab 2: Global Feature Importance
    with tab2:
        render_html(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
                Global Mean Absolute Feature Impact (|SHAP|)
            </span>
            <span class="pill-forest">MODEL-WIDE ATTRIBUTION</span>
        </div>
        <p style="font-size: 0.88rem; color: {c['muted']}; margin-bottom: 16px;">
            Average absolute impact of each feature across all holdout evaluation years.
        </p>
        """)

        sorted_global = global_df.sort_values(by="Mean_Abs_SHAP", ascending=True)

        fig_g_shap = go.Figure()
        fig_g_shap.add_trace(go.Bar(
            y=sorted_global["Feature"],
            x=sorted_global["Mean_Abs_SHAP"],
            orientation="h",
            marker=dict(color="#059669", line=dict(color=c["surface"], width=1)),
            text=sorted_global["Impact_Share_Pct"].apply(lambda p: f"{p:.1f}%"),
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color=c["text"]),
            hovertemplate="<b>%{y}</b><br>Mean |SHAP|: %{x:.2f} Mt CO₂eq<br>Share: %{text}<extra></extra>"
        ))

        layout_g = get_plotly_layout(height=380)
        layout_g.xaxis.title = "Mean Absolute SHAP Impact (Mt CO₂eq)"
        layout_g.yaxis.title = ""
        layout_g.margin = dict(l=120, r=30, t=20, b=40)
        fig_g_shap.update_layout(layout_g)
        st.plotly_chart(fig_g_shap, use_container_width=True)

        st.dataframe(global_df, use_container_width=True)

    # Tab 3: Permutation Importance
    with tab3:
        render_html(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
                Permutation Feature Importance vs Intrinsic Weights
            </span>
            <span class="pill-neutral">Model-Agnostic Validation</span>
        </div>
        <p style="font-size: 0.88rem; color: {c['muted']}; margin-bottom: 16px;">
            Validates whether SHAP rankings align with model loss degradation when features are shuffled.
        </p>
        """)

        with st.spinner("Computing permutation importance on out-of-sample data..."):
            perm_df = feature_importance_engine.compute_permutation_importance(country, model_name)

        if not perm_df.empty:
            perm_sorted = perm_df.sort_values(by="Mean_RMSE_Increase_Mt", ascending=True)
            fig_perm = go.Figure()
            fig_perm.add_trace(go.Bar(
                y=perm_sorted["Feature"],
                x=perm_sorted["Mean_RMSE_Increase_Mt"],
                orientation="h",
                marker=dict(color="#093326", line=dict(color=c["surface"], width=1)),
                text=perm_sorted["Mean_RMSE_Increase_Mt"].apply(lambda v: f"+{v:.1f} Mt"),
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=10, color=c["text"]),
                hovertemplate="<b>%{y}</b><br>Loss Penalty: +%{x:.2f} Mt RMSE<extra></extra>"
            ))
            layout_perm = get_plotly_layout(height=360)
            layout_perm.xaxis.title = "Test RMSE Degradation Upon Shuffling (Mt CO₂eq)"
            layout_perm.yaxis.title = ""
            layout_perm.margin = dict(l=120, r=30, t=20, b=40)
            fig_perm.update_layout(layout_perm)
            st.plotly_chart(fig_perm, use_container_width=True)
            st.dataframe(perm_df, use_container_width=True)
        else:
            st.info("Permutation importance data is currently not available for this model configuration.")
