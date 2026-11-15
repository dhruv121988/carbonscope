"""
CarbonScope 2.0: An Explainable Climate Intelligence and Greenhouse Gas Emission Forecasting System
Authoritative Data Source: European Commission Joint Research Centre (EDGAR 2026)
Master Application Entry Point with Climate-Tech Design System
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

# Configure Streamlit Page
st.set_page_config(
    page_title="CarbonScope 2.0 | Climate Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

from dashboard.ui_components import (
    apply_theme,
    get_current_palette,
    render_app_header,
    render_html,
    COLORS
)
from dashboard.overview import render_overview
from dashboard.data_intelligence import render_data_intelligence
from dashboard.emission_explorer import render_emission_explorer
from dashboard.ml_laboratory import render_ml_laboratory
from dashboard.anomaly_radar import render_anomaly_radar
from dashboard.explainability import render_explainability
from dashboard.scenario_simulator import render_scenario_simulator

# Initialize theme state (Default: light matching the reference image)
if "theme" not in st.session_state:
    st.session_state.theme = "light"

apply_theme()


MODULE_SUBITEMS = {
    "1. Overview Dashboard": [
        "Global GHG Trajectory",
        "India Decarbonization Profile",
        "IPCC Sector Distribution",
        "Top Sovereign Emitters"
    ],
    "2. Data Intelligence": [
        "Cryptographic Provenance (SHA-256)",
        "Automated Quality Audit (99.88%)",
        "Decadal Completeness Matrix",
        "Official EDGAR Ingestion"
    ],
    "3. Emission Explorer": [
        "Multi-Country Trajectories",
        "Sectoral Evolution & Areas",
        "Planetary Choropleth Density Map",
        "Macroeconomic Intensity (GDP/Capita)"
    ],
    "4. ML Laboratory": [
        "Chronological Holdout Validation",
        "Multi-Model Regression Benchmark",
        "Actual vs Predicted Fit Curve",
        "10-Year Recursive Forecast (2026–2035)"
    ],
    "5. Anomaly Radar": [
        "Statistical Z-Score Detector",
        "Unsupervised Isolation Forest",
        "Historical Disruption Timeline",
        "Automated Root-Cause Attribution"
    ],
    "6. Explainability Centre": [
        "Global SHAP Feature Importance",
        "Local Prediction Waterfall (SHAP)",
        "Permutation Feature Impact",
        "Model Interpretability Diagnostics"
    ],
    "7. Scenario Simulator": [
        "Baseline vs Policy Divergence",
        "Sectoral Decarbonization Sliders",
        "Cumulative Avoided Carbon Wedge",
        "Policy Impact Comparative Curves"
    ]
}


def render_sidebar():
    """Render CarbonScope 2.0 operational sidebar with tree navigation."""
    c = get_current_palette()
    with st.sidebar:
        # Branding Header with green badge icon (as seen in reference design)
        render_html(f"""
        <div class="sidebar-brand-rail">
            <div class="brand-logo-badge">
                CS
            </div>
            <div>
                <div class="brand-title">
                    CarbonScope <span style="color: #34D399; font-size: 0.9em;">2.0</span>
                </div>
                <div class="brand-subtitle">
                    Climate Intelligence
                </div>
            </div>
        </div>
        """)

        # Theme Switcher Pill in Sidebar
        cur_theme = st.session_state.theme
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            render_html(f"""
            <div style="font-size: 0.72rem; color: {c['sidebar_muted']}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px;">
                ACTIVE PALETTE: <span style="color: #FFFFFF;">{'LIGHT (REFERENCE)' if cur_theme == 'light' else 'DARK FOREST'}</span>
            </div>
            """)
        with col_t2:
            btn_label = "🌙 Dark" if cur_theme == "light" else "☀️ Light"
            if st.button(btn_label, key="theme_toggle_btn", help="Switch between Light (Reference Design) and Dark Forest palette"):
                st.session_state.theme = "dark" if cur_theme == "light" else "light"
                st.rerun()

        render_html(f"""
        <div class="nav-section-title">
            PLATFORM MODULES
        </div>
        """)

        modules = list(MODULE_SUBITEMS.keys())

        if "selected_module" not in st.session_state:
            st.session_state.selected_module = modules[0]

        choice = st.radio(
            "Select Dashboard Module",
            options=modules,
            index=modules.index(st.session_state.selected_module),
            label_visibility="collapsed"
        )
        st.session_state.selected_module = choice

        # Tree Navigation Sub-Items with branching lines (Matching reference image)
        sub_items = MODULE_SUBITEMS.get(choice, [])
        tree_branches_html = ""
        for i, item in enumerate(sub_items):
            is_last = (i == len(sub_items) - 1)
            branch_char = "└──" if is_last else "├──"
            tree_branches_html += f"""
            <div style="display: flex; align-items: center; gap: 8px; font-size: 0.76rem; color: {c['sidebar_muted']}; padding: 4px 0 4px 14px; font-family: 'JetBrains Mono', monospace;">
                <span style="color: rgba(52, 211, 153, 0.6);">{branch_char}</span>
                <span style="color: {c['sidebar_text']};">{item}</span>
            </div>
            """

        render_html(f"""
        <div style="background: {c['sidebar_surface']}; border: 1px solid {c['sidebar_border']}; border-radius: 12px; padding: 10px 12px; margin-top: 10px; margin-bottom: 20px;">
            <div style="font-size: 0.7rem; font-weight: 700; color: #34D399; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                OPERATIONAL LENSES
            </div>
            {tree_branches_html}
        </div>
        """)

        # Telemetry & Provenance Registry Footer
        render_html(f"""
        <div style="padding-top: 14px; border-top: 1px solid {c['sidebar_border']}; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: {c['sidebar_muted']}; line-height: 1.6;">
            <div><b style="color: #FFFFFF;">SOURCE:</b> EDGAR 2026 (JRC147815)</div>
            <div><b style="color: #FFFFFF;">INTERVAL:</b> 1970 – 2025 (56 Yrs)</div>
            <div><b style="color: #FFFFFF;">STANDARD:</b> IPCC AR5 GWP-100</div>
            <div><b style="color: #FFFFFF;">HEALTH:</b> <span style="color: #34D399;">99.88% COMPLETE</span></div>
        </div>
        """)


def main():
    """Main routing controller."""
    render_sidebar()
    current_module = st.session_state.selected_module

    # Top App Header
    render_app_header(module_title=current_module, breadcrumb_step=current_module.split(". ")[-1])

    # Module Content
    if "1. Overview Dashboard" in current_module:
        render_overview()
    elif "2. Data Intelligence" in current_module:
        render_data_intelligence()
    elif "3. Emission Explorer" in current_module:
        render_emission_explorer()
    elif "4. ML Laboratory" in current_module:
        render_ml_laboratory()
    elif "5. Anomaly Radar" in current_module:
        render_anomaly_radar()
    elif "6. Explainability Centre" in current_module:
        render_explainability()
    elif "7. Scenario Simulator" in current_module:
        render_scenario_simulator()


if __name__ == "__main__":
    main()
