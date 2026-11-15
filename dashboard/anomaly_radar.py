"""
CarbonScope 2.0 - Module 5: Emission Anomaly Radar
Detects and explains non-linear disruptions, macroeconomic shocks (1991 Soviet collapse,
2008 GFC, 2020 COVID deflection), and abnormal emission spikes.
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
from src.anomaly.statistical_detection import statistical_detector
from src.anomaly.isolation_forest import iso_detector
from src.analysis.emission_analysis import analyzer


def render_anomaly_radar():
    """Render Module 5: Emission Anomaly Radar."""
    c = get_current_palette()

    render_page_header(
        title="Emission Anomaly Radar & Structural Deflection",
        subtitle="Unsupervised Isolation Forest and Statistical Z-Score detectors with automated root-cause attribution.",
        badge="PATTERN ANOMALY DETECTION"
    )

    # Top Control Filters (Country, Sector, Gas, Year, Method)
    all_c = analyzer.get_available_countries()
    sectors = analyzer.get_available_sectors()
    gases = analyzer.get_available_substances()

    with st.container():
        ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.5, 1.2, 1.2, 1.5])
        with ctrl1:
            country = st.selectbox(
                "Entity for Anomaly Radar",
                all_c,
                index=all_c.index("India") if "India" in all_c else 0
            )
        with ctrl2:
            target_sector = st.selectbox("IPCC Economic Sector", ["All National Sectors"] + sectors, index=0)
        with ctrl3:
            target_gas = st.selectbox("Greenhouse Gas", ["All GHGs (AR5 CO₂eq)"] + gases, index=0)
        with ctrl4:
            method = st.radio("Detection Engine", ["Statistical Z-Score", "Isolation Forest (ML)"], horizontal=True)

    with st.container():
        f_sub1, f_sub2 = st.columns([2, 2])
        with f_sub1:
            if method == "Statistical Z-Score":
                threshold = st.slider("Z-Score Sensitivity Threshold (σ)", min_value=1.5, max_value=3.5, value=2.0, step=0.1, help="Standard deviations above or below historical rolling trend.")
            else:
                contamination = st.slider("Contamination Rate (Outlier %)", min_value=0.02, max_value=0.15, value=0.08, step=0.01, help="Expected proportion of anomalies in empirical sample.")
        with f_sub2:
            year_range = st.slider("Observation Window", min_value=1970, max_value=2025, value=(1970, 2025), step=1)

    # Execute Detection
    if method == "Statistical Z-Score":
        anom_df = statistical_detector.detect_trajectory_anomalies(country, z_threshold=threshold)
        flagged = anom_df[anom_df["Is_Anomaly"]].copy()
        thresh_label = f"Threshold: {threshold}σ"
    else:
        anom_df = iso_detector.detect_anomalies(country, contamination=contamination)
        flagged = anom_df[anom_df["Is_Anomaly"]].copy()
        thresh_label = f"Contamination: {contamination*100:.0f}%"

    # Filter by year range
    anom_df = anom_df[(anom_df["Year"] >= year_range[0]) & (anom_df["Year"] <= year_range[1])].copy()
    flagged = flagged[(flagged["Year"] >= year_range[0]) & (flagged["Year"] <= year_range[1])].copy()

    # 1. Headline Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            title="Flagged Anomalies",
            value=str(len(flagged)),
            unit=f"of {len(anom_df)} Years",
            delta_text=thresh_label,
            is_reduction_positive=True,
            badge="TELEMETRY"
        )
    with c2:
        covid_row = anom_df[anom_df["Year"] == 2020]
        covid_flagged = bool(covid_row["Is_Anomaly"].values[0]) if not covid_row.empty else False
        render_metric_card(
            title="2020 Pandemic Shock",
            value="DETECTED" if covid_flagged else "NORMAL",
            unit="",
            delta_text="COVID-19 Deflection",
            is_reduction_positive=False,
            badge="HISTORICAL MILESTONE"
        )
    with c3:
        max_dev = flagged["Pct_Deviation"].abs().max() if not flagged.empty else 0.0
        render_metric_card(
            title="Max Trajectory Deviation",
            value=f"{max_dev:.1f}%",
            unit="Delta",
            delta_text="From Baseline",
            is_reduction_positive=True,
            badge="DISPERSION"
        )
    with c4:
        render_metric_card(
            title="Detection Paradigm",
            value=method.split()[0],
            unit="",
            delta_text="Unsupervised Diagnostics",
            is_reduction_positive=False,
            badge="SCIENTIFIC"
        )

    render_html("<div style='height: 16px;'></div>")

    # 2. Main Visualization: Historical Trajectory with Flagged Anomaly Nodes
    render_html(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
            {country}: Emission Trajectory & Flagged Anomaly Radar Nodes ({year_range[0]} – {year_range[1]})
        </span>
        <span class="pill-rose">● RED DIAMONDS = FLAGGED ANOMALIES</span>
    </div>
    """)

    fig_anom = go.Figure()

    # Normal curve
    fig_anom.add_trace(go.Scatter(
        x=anom_df["Year"],
        y=anom_df["Emissions_MtCO2eq"],
        mode="lines",
        name="Historical Emissions",
        line=dict(color="#093326", width=2.5),
        hovertemplate="<b>Year %{x}</b><br>Emissions: %{y:,.1f} Mt CO₂eq<extra></extra>"
    ))

    # Baseline envelope
    baseline_col = "Historical_Baseline" if "Historical_Baseline" in anom_df.columns else "Baseline_5yr"
    if baseline_col in anom_df.columns:
        fig_anom.add_trace(go.Scatter(
            x=anom_df["Year"],
            y=anom_df[baseline_col],
            mode="lines",
            name="Expected Rolling Baseline",
            line=dict(color=c["muted"], width=1.5, dash="dot"),
            hovertemplate="<b>Baseline %{x}</b><br>%{y:,.1f} Mt CO₂eq<extra></extra>"
        ))

    # Flagged anomaly red diamond nodes
    if not flagged.empty:
        fig_anom.add_trace(go.Scatter(
            x=flagged["Year"],
            y=flagged["Emissions_MtCO2eq"],
            mode="markers+text",
            name="Flagged Anomalies",
            marker=dict(size=12, color="#DC2626", symbol="diamond", line=dict(color="#FFFFFF", width=2)),
            text=flagged["Year"].astype(str),
            textposition="top center",
            textfont=dict(family="JetBrains Mono", size=11, color="#DC2626"),
            hovertemplate="<b>ANOMALY: Year %{x}</b><br>Emissions: %{y:,.1f} Mt<br>Deviation: %{customdata:+.1f}%<extra></extra>",
            customdata=flagged["Pct_Deviation"]
        ))

    layout_anom = get_plotly_layout(height=420)
    layout_anom.yaxis.title = "Emissions (Mt CO₂eq)"
    layout_anom.xaxis.title = "Observation Year"
    fig_anom.update_layout(layout_anom)
    st.plotly_chart(fig_anom, use_container_width=True)

    render_disclaimer_card(
        text="An anomaly observation does not automatically indicate an environmental catastrophe. It represents an empirically unusual deflection that diverges significantly from preceding historical momentum (e.g. pandemic economic lockdowns, geopolitical reconfigurations, or post-recession rebounds).",
        title="Scientific Attribution Framework"
    )

    # 3. Anomaly Score Distribution Chart
    render_html(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 24px; margin-bottom: 12px;">
        <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
            Anomaly Score / Deviation Distribution
        </span>
        <span class="pill-neutral">Dispersion Analysis</span>
    </div>
    """)

    fig_dist = go.Figure()
    bar_colors = ["#DC2626" if is_anom else "#10B981" for is_anom in anom_df["Is_Anomaly"]]
    fig_dist.add_trace(go.Bar(
        x=anom_df["Year"],
        y=anom_df["Pct_Deviation"],
        marker=dict(color=bar_colors, line=dict(color=c["surface"], width=0.8)),
        hovertemplate="<b>Year %{x}</b><br>Deviation: %{y:+.2f}%<extra></extra>"
    ))
    fig_dist.add_hline(y=0, line_dash="solid", line_color=c["muted"], line_width=1)
    layout_dist = get_plotly_layout(height=320)
    layout_dist.yaxis.title = "Deviation from Baseline (%)"
    layout_dist.xaxis.title = "Year"
    fig_dist.update_layout(layout_dist)
    st.plotly_chart(fig_dist, use_container_width=True)

    # 4. Granular Anomaly Explanation Table
    render_html(f"""
    <div style="margin-top: 24px; margin-bottom: 12px;">
        <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
            Granular Anomaly Attribution & Root-Cause Explanation Table
        </span>
        <p style="font-size: 0.88rem; color: {c['muted']}; margin-top: 4px; margin-bottom: 16px;">
            Detailed rationale for each flagged observation showing baseline, numerical delta, percentage deviation, and historical context.
        </p>
    </div>
    """)

    if not flagged.empty:
        display_cols = ["Year", "Emissions_MtCO2eq", "Pct_Deviation", "Explanation", "Detection_Method"]
        st.dataframe(flagged[display_cols], use_container_width=True)
    else:
        st.info(f"No statistical anomalies detected for '{country}' under current sensitivity settings.")
