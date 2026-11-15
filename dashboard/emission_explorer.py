"""
CarbonScope 2.0 - Module 3: Emission Explorer
Interactive analytical environment for multi-country comparisons,
sectoral evolutions, choropleth world map, and YoY delta trajectories.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List

from dashboard.ui_components import (
    COLORS,
    get_current_palette,
    get_plotly_layout,
    render_metric_card,
    render_page_header,
    render_html
)
from src.analysis.emission_analysis import analyzer


def render_emission_explorer():
    """Render Module 3: Emission Explorer."""
    c = get_current_palette()

    render_page_header(
        title="Emission Explorer & Planetary Analytics",
        subtitle="Historical trajectories, multi-country comparative matrices, sectoral evolutions, and geographical density.",
        badge="INTERACTIVE EXPLORATION"
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Multi-Country Trajectories & Comparisons",
        "🏭 Sectoral Evolution & Area Breakdown",
        "🗺️ Geographical Choropleth Density Map",
        "⚖️ Macroeconomic Decoupling (Per Capita & GDP)"
    ])

    all_c = analyzer.get_available_countries()

    # Tab 1: Multi-Country Comparisons
    with tab1:
        render_html(f"""
        <div style="margin-bottom: 14px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
                Comparative Historical Trajectories (1970 – 2025)
            </span>
            <p style="font-size: 0.88rem; color: {c['muted']}; margin-top: 4px; margin-bottom: 16px;">
                Select multiple sovereign nations to compare emission volume and decarbonization momentum.
            </p>
        </div>
        """)

        ctrl_col1, ctrl_col2 = st.columns([2.5, 1.5])
        with ctrl_col1:
            default_selection = ["India", "China", "United States", "EU27", "Russia"]
            valid_defaults = [cnt for cnt in default_selection if cnt in all_c]
            sel_countries = st.multiselect(
                "Select Sovereign Nations or Entities to Compare",
                options=all_c,
                default=valid_defaults
            )
        with ctrl_col2:
            metric_choice = st.radio(
                "Metric Dimension",
                ["Gross Emissions (Mt CO₂eq)", "Year-over-Year Growth Rate (%)", "Cumulative Historical Emissions (Mt CO₂eq)"],
                horizontal=False
            )

        if sel_countries:
            fig_comp = go.Figure()
            palette = [
                "#093326", "#059669", "#0284C7", "#EA580C",
                "#8B5CF6", "#D97706", "#10B981", "#E11D48"
            ]

            for i, cntry in enumerate(sel_countries):
                traj = analyzer.get_country_trajectory(cntry)
                if traj.empty:
                    continue

                if metric_choice == "Gross Emissions (Mt CO₂eq)":
                    y_vals = traj["Emissions_MtCO2eq"]
                    y_title = "Emissions (Mt CO₂eq)"
                    hover_fmt = "%{y:,.1f} Mt CO₂eq"
                elif metric_choice == "Year-over-Year Growth Rate (%)":
                    y_vals = traj["YoY_Growth_Pct"]
                    y_title = "Annual Growth Rate (%)"
                    hover_fmt = "%{y:+.2f}%"
                else:
                    y_vals = traj["Cumulative_MtCO2eq"]
                    y_title = "Cumulative Emissions (Mt CO₂eq)"
                    hover_fmt = "%{y:,.0f} Mt CO₂eq"

                color = palette[i % len(palette)]
                fig_comp.add_trace(go.Scatter(
                    x=traj["Year"],
                    y=y_vals,
                    mode="lines",
                    name=cntry,
                    line=dict(color=color, width=3.0 if cntry == "India" else 2.0),
                    hovertemplate=f"<b>{cntry}</b> (Year %{{x}})<br>{hover_fmt}<extra></extra>"
                ))

            layout_comp = get_plotly_layout(height=420)
            layout_comp.yaxis.title = y_title
            layout_comp.xaxis.title = "Observation Year"
            fig_comp.update_layout(layout_comp)
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.warning("Please select at least one sovereign entity to display comparison.")

    # Tab 2: Sectoral Evolution & Gas Breakdown
    with tab2:
        sec_ctrl_col1, sec_ctrl_col2 = st.columns([2, 1])
        with sec_ctrl_col1:
            focus_c = st.selectbox("Focus Country for Sector Evolution", all_c, index=all_c.index("India") if "India" in all_c else 0)
        with sec_ctrl_col2:
            chart_style = st.radio("Visualization Architecture", ["Stacked Area", "Separate Trendlines"], horizontal=True)

        render_html(f"""
        <div style="margin-bottom: 14px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
                {focus_c}: Sector Contribution Evolution Over Time (1970 – 2025)
            </span>
            <p style="font-size: 0.88rem; color: {c['muted']}; margin-top: 4px; margin-bottom: 16px;">
                Historical transition of emissions across 8 IPCC economic pillars.
            </p>
        </div>
        """)

        sec_pivot = analyzer.get_sector_timeline(focus_c)
        if not sec_pivot.empty:
            fig_sec_evo = go.Figure()
            sectors = [col for col in sec_pivot.columns if col != "Year"]
            sec_colors = [
                "#064E3B", "#0D523C", "#059669", "#10B981",
                "#34D399", "#0284C7", "#EA580C", "#D97706"
            ]

            for idx, s_name in enumerate(sectors):
                color = sec_colors[idx % len(sec_colors)]
                fig_sec_evo.add_trace(go.Scatter(
                    x=sec_pivot["Year"],
                    y=sec_pivot[s_name],
                    mode="lines",
                    name=s_name,
                    line=dict(color=color, width=1.8),
                    stackgroup="one" if chart_style == "Stacked Area" else None,
                    hovertemplate=f"<b>{s_name}</b> (Year %{{x}})<br>%{{y:,.1f}} Mt CO₂eq<extra></extra>"
                ))

            layout_sec_evo = get_plotly_layout(height=420)
            layout_sec_evo.yaxis.title = "Emissions (Mt CO₂eq)"
            layout_sec_evo.xaxis.title = "Observation Year"
            fig_sec_evo.update_layout(layout_sec_evo)
            st.plotly_chart(fig_sec_evo, use_container_width=True)
        else:
            st.info(f"Sector timeline unavailable for '{focus_c}'.")

    # Tab 3: Geographical Choropleth World Map
    with tab3:
        render_html(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
                Geographical Emission Density Map
            </span>
            <span class="pill-forest">GLOBAL SPATIAL DENSITY</span>
        </div>
        <p style="font-size: 0.88rem; color: {c['muted']}; margin-bottom: 16px;">
            Interactive choropleth mapping of sovereign national greenhouse gas emissions.
        </p>
        """)

        map_year = st.slider("Select Map Year", min_value=1970, max_value=2025, value=2025, step=1, key="map_yr")

        m = analyzer.master_df
        map_df = m[(~m["Is_Aggregate"]) & (m["Year"] == map_year)].copy()

        fig_map = px.choropleth(
            map_df,
            locations="EDGAR_Code",
            color="Emissions_MtCO2eq",
            hover_name="Country",
            color_continuous_scale=[
                [0.0, "#E8F5EE"],
                [0.02, "#34D399"],
                [0.1, "#059669"],
                [0.3, "#D97706"],
                [1.0, "#DC2626"]
            ],
            labels={"Emissions_MtCO2eq": "Mt CO₂eq"},
            projection="natural earth"
        )

        ocean_bg = "#E8F2ED" if st.session_state.get("theme", "light") == "light" else "#0B1512"
        land_bg = "#FFFFFF" if st.session_state.get("theme", "light") == "light" else "#142921"

        fig_map.update_geos(
            showocean=True,
            oceancolor=ocean_bg,
            showland=True,
            landcolor=land_bg,
            showlakes=False,
            showcoastlines=True,
            coastlinecolor=c["border"],
            showframe=False
        )

        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=10),
            height=480,
            coloraxis_colorbar=dict(
                title="Mt CO₂eq",
                tickfont=dict(family="JetBrains Mono", size=10, color=c["text"]),
                titlefont=dict(family="Inter", size=11, color=c["muted"])
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # Tab 4: Macroeconomic Intensity
    with tab4:
        render_html(f"""
        <div style="margin-bottom: 14px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: {c['text_dark']};">
                Macroeconomic Intensity: Per Capita & Per GDP Decoupling
            </span>
            <p style="font-size: 0.88rem; color: {c['muted']}; margin-top: 4px; margin-bottom: 16px;">
                Evaluate climate efficiency: emissions per person (t CO₂eq/cap/yr) and emissions per GDP purchasing power parity (t CO₂eq/kUSD/yr).
            </p>
        </div>
        """)

        m_yr = st.selectbox("Benchmark Snapshot Year", [2025, 2020, 2015, 2010, 2005, 2000, 1990], index=0)
        macro_df = m[(~m["Is_Aggregate"]) & (m["Year"] == m_yr)].dropna(subset=["Emissions_Per_Capita_tCO2eq"]).sort_values(by="Emissions_Per_Capita_tCO2eq", ascending=False).head(20)

        fig_macro = go.Figure()
        fig_macro.add_trace(go.Bar(
            x=macro_df["Country"],
            y=macro_df["Emissions_Per_Capita_tCO2eq"],
            marker=dict(color="#059669", line=dict(color=c["surface"], width=1)),
            text=macro_df["Emissions_Per_Capita_tCO2eq"].apply(lambda v: f"{v:.1f}"),
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color=c["text"]),
            hovertemplate="<b>%{x}</b><br>Per Capita: %{y:.2f} t CO₂eq/cap<extra></extra>"
        ))

        layout_macro = get_plotly_layout(height=400)
        layout_macro.yaxis.title = "Emissions Per Capita (t CO₂eq / cap / yr)"
        layout_macro.xaxis.title = ""
        layout_macro.xaxis.tickangle = -35
        fig_macro.update_layout(layout_macro)
        st.plotly_chart(fig_macro, use_container_width=True)
