"""
CarbonScope 2.0 - Climate Intelligence UI Design System & Component Library
Exact visual identity implementation inspired by modern ESG & climate intelligence platforms:
- Deep Forest Green (#093326 / #0b3b2c)
- Clean Off-White Canvas (#F1F6F3)
- Crisp White Elevated Cards (#FFFFFF) with 20px border radius & soft elevation
- Environmental Semantic Badges (Mint #DCFCE7 / Rose #FEE2E2 / Emerald #059669)
- Dual-rail Tree Navigation & Multi-level Hierarchy
- High-contrast, accessible typography (Inter & JetBrains Mono)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional, List
import re


# Environmental Design System Palette
COLORS = {
    # Light Mode (Default as in Reference Design)
    "background": "#F0F5F2",
    "surface": "#FFFFFF",
    "surface_subtle": "#F7FAF8",
    "sidebar": "#082F22",           # Deep Forest Green
    "sidebar_surface": "#0C3C2C",   # Forest Green Elevated
    "sidebar_hover": "#114B38",     # Forest Green Hover
    "sidebar_border": "#165943",    # Forest Green Divider
    "sidebar_text": "#E8F5EF",      # Forest Sage Text
    "sidebar_muted": "#8BB7A5",     # Forest Sage Muted
    "border": "#E2EBE5",            # Card Border
    "border_light": "#EDF3EF",
    "primary": "#093326",           # Deep Forest Primary
    "primary_dark": "#052219",
    "primary_light": "#0D523C",
    "emerald": "#059669",           # Positive Action Emerald
    "emerald_bg": "#DCFCE7",        # Soft Mint Badge
    "emerald_text": "#166534",
    "sage": "#4B8B6F",              # Soft Sage
    "teal": "#0D9488",              # Muted Teal
    "scope1": "#EA580C",            # Coral / Fossil Direct
    "scope2": "#0284C7",            # Sky Blue / Electricity Indirect
    "scope3": "#16A34A",            # Leaf Green / Bio & Ag
    "scope4": "#8B5CF6",            # Purple / Waste & Other
    "warning": "#D97706",           # Amber
    "warning_bg": "#FEF3C7",
    "danger": "#DC2626",            # Alert Coral / Warning
    "danger_bg": "#FEE2E2",         # Soft Rose Badge
    "danger_text": "#991B1B",
    "text": "#0F291E",              # Deep Charcoal Forest
    "text_dark": "#05160E",
    "muted": "#5A7366",             # Slate Sage
    "muted_light": "#889F93",
    "grid": "#EBF2ED",              # Chart Gridlines
    "white": "#FFFFFF"
}

# Dark Theme Variant Palette
COLORS_DARK = {
    "background": "#0B1512",
    "surface": "#12241F",
    "surface_subtle": "#172E27",
    "sidebar": "#081813",
    "sidebar_surface": "#0E2820",
    "sidebar_hover": "#14372C",
    "sidebar_border": "#1A4537",
    "sidebar_text": "#E8F5EF",
    "sidebar_muted": "#7EA895",
    "border": "#1C382F",
    "border_light": "#25483C",
    "primary": "#34D399",
    "primary_dark": "#059669",
    "primary_light": "#6EE7B7",
    "emerald": "#10B981",
    "emerald_bg": "#064E3B",
    "emerald_text": "#A7F3D0",
    "sage": "#34D399",
    "teal": "#2DD4BF",
    "scope1": "#FB923C",
    "scope2": "#38BDF8",
    "scope3": "#4ADE80",
    "scope4": "#A78BFA",
    "warning": "#FBBF24",
    "warning_bg": "#78350F",
    "danger": "#F87171",
    "danger_bg": "#7F1D1D",
    "danger_text": "#FECACA",
    "text": "#EAF4EE",
    "text_dark": "#FFFFFF",
    "muted": "#8BAAA0",
    "muted_light": "#6A8C81",
    "grid": "#183027",
    "white": "#12241F"
}


def get_current_palette() -> Dict[str, str]:
    """Return active theme palette based on session state."""
    theme = st.session_state.get("theme", "light")
    return COLORS_DARK if theme == "dark" else COLORS


def render_html(html_str: str):
    """
    Safely render HTML without Markdown converting indented lines to code blocks.
    Strips leading whitespace from every line so Markdown's 4-space code block rule is never triggered.
    """
    clean_html = "\n".join(line.strip() for line in html_str.strip().splitlines())
    st.markdown(clean_html, unsafe_allow_html=True)


def apply_theme():
    """Inject custom environmental CSS styling into Streamlit app matching the reference design."""
    theme = st.session_state.get("theme", "light")
    c = COLORS_DARK if theme == "dark" else COLORS

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Global Canvas Setup */
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            background-color: {c["background"]} !important;
            color: {c["text"]};
        }}

        .stApp {{
            background-color: {c["background"]} !important;
        }}

        /* Main Content Container Padding */
        .main .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1440px !important;
        }}

        /* Left Navigation / Sidebar Styling (Deep Forest Green) */
        [data-testid="stSidebar"] {{
            background-color: {c["sidebar"]} !important;
            border-right: 1px solid {c["sidebar_border"]} !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.08);
        }}

        [data-testid="stSidebar"] > div:first-child {{
            background-color: {c["sidebar"]} !important;
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: {c["sidebar_border"]} !important;
            margin: 14px 0 !important;
        }}

        /* Modern Forest Green Tree Navigation */
        .sidebar-brand-rail {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 4px 18px 4px;
            border-bottom: 1px solid {c["sidebar_border"]};
            margin-bottom: 16px;
        }}

        .brand-logo-badge {{
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #FFFFFF;
            font-weight: 800;
            font-size: 1.2rem;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
        }}

        .brand-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #FFFFFF;
            letter-spacing: -0.02em;
            line-height: 1.15;
        }}

        .brand-subtitle {{
            font-size: 0.68rem;
            color: {c["sidebar_muted"]};
            font-weight: 500;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        /* Sidebar Section Header */
        .nav-section-title {{
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {c["sidebar_muted"]};
            margin: 16px 4px 8px 4px;
        }}

        /* Sidebar Default Text Color Fallback (Guarantees zero dark-on-dark invisible text) */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {{
            color: #F8FAFC !important;
        }}

        /* Streamlit Radio Re-styling for Navigation Capsule Pills (Matching Reference Design) */
        [data-testid="stSidebar"] [data-testid="stRadio"],
        [data-testid="stSidebar"] div[role="radiogroup"] {{
            gap: 6px !important;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] label,
        [data-testid="stSidebar"] div[role="radiogroup"] label {{
            background: rgba(255, 255, 255, 0.06) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 9999px !important;
            padding: 9px 16px !important;
            margin-bottom: 6px !important;
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            cursor: pointer !important;
            width: 100% !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover,
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
            background: rgba(255, 255, 255, 0.14) !important;
            border-color: rgba(52, 211, 153, 0.5) !important;
            transform: translateX(3px) !important;
        }}

        /* High-contrast crisp white typography for ALL radio label children */
        [data-testid="stSidebar"] [data-testid="stRadio"] label *,
        [data-testid="stSidebar"] div[role="radiogroup"] label *,
        [data-testid="stSidebar"] [data-testid="stRadio"] div[data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stRadio"] span,
        [data-testid="stSidebar"] div[role="radiogroup"] span {{
            color: #FFFFFF !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
        }}

        /* Active / Selected Radio Pill (Glowing Mint / Emerald Highlight) */
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked),
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked),
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {{
            background: rgba(16, 185, 129, 0.24) !important;
            border: 1px solid #10B981 !important;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) *,
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] *,
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) *,
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] *,
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p,
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p {{
            color: #34D399 !important;
            font-weight: 700 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {{
            accent-color: #10B981 !important;
            width: 15px !important;
            height: 15px !important;
        }}

        [data-testid="stSidebar"] .stButton > button {{
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: #FFFFFF !important;
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            border-radius: 9999px !important;
            padding: 4px 12px !important;
            box-shadow: none !important;
        }}

        [data-testid="stSidebar"] .stButton > button:hover {{
            background: rgba(16, 185, 129, 0.25) !important;
            border-color: #10B981 !important;
            color: #34D399 !important;
            transform: none !important;
        }}

        /* Elevated Card Panels (As in Reference Image: Pure White, Rounded 20px, Subtle Shadow) */
        .carbon-card {{
            background: {c["surface"]};
            border: 1px solid {c["border"]};
            border-radius: 20px;
            padding: 22px 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px -2px rgba(9, 51, 38, 0.04), 0 1px 3px rgba(9, 51, 38, 0.02);
            transition: box-shadow 0.25s ease, border-color 0.25s ease;
        }}

        .carbon-card:hover {{
            border-color: rgba(9, 51, 38, 0.15);
            box-shadow: 0 8px 28px -4px rgba(9, 51, 38, 0.07);
        }}

        /* KPI / Metric Container (Matching Reference Image) */
        .kpi-card {{
            background: {c["surface"]};
            border: 1px solid {c["border"]};
            border-radius: 18px;
            padding: 20px 22px;
            box-shadow: 0 4px 18px -2px rgba(9, 51, 38, 0.04);
            position: relative;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .kpi-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
        }}

        .kpi-title-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: {c["muted"]};
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: -0.01em;
        }}

        .kpi-value-row {{
            display: flex;
            align-items: baseline;
            gap: 8px;
            margin: 6px 0 10px 0;
        }}

        .kpi-value {{
            font-size: 2.3rem;
            font-weight: 800;
            color: {c["text_dark"]};
            letter-spacing: -0.03em;
            line-height: 1;
        }}

        .kpi-unit {{
            font-size: 0.85rem;
            font-weight: 600;
            color: {c["muted"]};
            font-family: 'JetBrains Mono', monospace;
        }}

        .kpi-footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: auto;
            padding-top: 8px;
        }}

        /* Badges & Pills */
        .pill-mint {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: {c["emerald_bg"]};
            color: {c["emerald_text"]};
            border: 1px solid rgba(16, 185, 129, 0.25);
        }}

        .pill-rose {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: {c["danger_bg"]};
            color: {c["danger_text"]};
            border: 1px solid rgba(220, 38, 38, 0.25);
        }}

        .pill-neutral {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            background: {c["surface_subtle"]};
            color: {c["muted"]};
            border: 1px solid {c["border"]};
        }}

        .pill-forest {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 600;
            background: {c["sidebar"]};
            color: #FFFFFF;
        }}

        /* Breakdown Table Rows (As in Study Support Card) */
        .breakdown-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 9px 12px;
            border-radius: 10px;
            margin-bottom: 6px;
            font-size: 0.85rem;
            transition: background 0.15s ease;
        }}

        .breakdown-row.active {{
            background: {c["emerald_bg"]};
            color: {c["emerald_text"]};
            font-weight: 600;
        }}

        .breakdown-row.default {{
            background: {c["surface_subtle"]};
            color: {c["text"]};
        }}

        /* Stacked Bar Segment */
        .segmented-progress {{
            height: 18px;
            border-radius: 9999px;
            overflow: hidden;
            display: flex;
            width: 100%;
            margin: 12px 0 10px 0;
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.06);
        }}

        /* Action Buttons */
        .stButton>button {{
            background: {c["sidebar"]} !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            border-radius: 9999px !important;
            border: 1px solid transparent !important;
            padding: 8px 22px !important;
            box-shadow: 0 4px 14px rgba(9, 51, 38, 0.18) !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }}

        .stButton>button:hover {{
            background: {c["primary_light"]} !important;
            color: #FFFFFF !important;
            box-shadow: 0 6px 18px rgba(9, 51, 38, 0.28) !important;
            transform: translateY(-1px);
        }}

        /* Selectboxes, Inputs & Sliders */
        div[data-baseweb="select"] > div {{
            background-color: {c["surface"]} !important;
            border-color: {c["border"]} !important;
            color: {c["text"]} !important;
            border-radius: 12px !important;
            font-size: 0.88rem !important;
        }}

        div[data-baseweb="select"] > div:hover {{
            border-color: {c["emerald"]} !important;
        }}

        .stSlider > div {{
            color: {c["emerald"]} !important;
        }}

        /* Tabs Styling (Rounded Pills) */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {c["surface"]};
            border: 1px solid {c["border"]};
            padding: 6px;
            border-radius: 14px;
            gap: 6px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.02);
            margin-bottom: 20px;
        }}

        .stTabs [data-baseweb="tab"] {{
            color: {c["muted"]} !important;
            font-weight: 500 !important;
            font-size: 0.86rem !important;
            border-radius: 10px !important;
            padding: 8px 16px !important;
            border: none !important;
            background: transparent !important;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {c["sidebar"]} !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(9, 51, 38, 0.2) !important;
        }}

        /* Dataframe Table Container */
        div[data-testid="stDataFrame"] {{
            background: {c["surface"]} !important;
            border: 1px solid {c["border"]} !important;
            border-radius: 16px !important;
            overflow: hidden !important;
        }}

        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 7px;
            height: 7px;
        }}
        ::-webkit-scrollbar-track {{
            background: {c["background"]};
        }}
        ::-webkit-scrollbar-thumb {{
            background: {c["border"]};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {c["muted_light"]};
        }}
    </style>
    """
    render_html(css)


def get_plotly_layout(title: str = "", height: int = 380) -> go.Layout:
    """Return a styled high-contrast Plotly layout matching CarbonScope 2.0 design system."""
    c = get_current_palette()
    return go.Layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family="Inter, sans-serif", size=14, color=c["text_dark"]),
            x=0.01,
            y=0.96
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=c["muted"], size=12),
        height=height,
        margin=dict(l=45, r=20, t=45, b=35),
        xaxis=dict(
            showgrid=True,
            gridcolor=c["grid"],
            zeroline=False,
            showline=True,
            linecolor=c["border"],
            tickfont=dict(family="JetBrains Mono, monospace", size=10, color=c["muted"])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=c["grid"],
            zeroline=False,
            showline=True,
            linecolor=c["border"],
            tickfont=dict(family="JetBrains Mono, monospace", size=10, color=c["muted"])
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Inter, sans-serif", size=11, color=c["text"]),
            bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(
            bgcolor=c["surface"],
            bordercolor=c["border"],
            font=dict(family="JetBrains Mono, monospace", size=12, color=c["text"])
        )
    )


def render_app_header(module_title: str, breadcrumb_step: str = "Overview"):
    """
    Render top application navigation bar matching the reference design:
    - Sama.ESG / CarbonScope 2.0 brand pill
    - Breadcrumbs: Home / Module / View
    - Theme toggle, notifications, user avatar, and action button
    """
    c = get_current_palette()
    current_theme = st.session_state.get("theme", "light")
    toggle_icon = "🌙" if current_theme == "light" else "☀️"
    toggle_label = "Dark Mode" if current_theme == "light" else "Light Mode"

    html = f"""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0 20px 0; border-bottom: 1px solid {c['border']}; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 8px; background: {c['surface']}; padding: 6px 14px; border-radius: 12px; border: 1px solid {c['border']}; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #10B981;"></span>
                <span style="font-weight: 700; font-size: 0.95rem; color: {c['text_dark']}; letter-spacing: -0.01em;">CarbonScope</span>
                <span style="font-size: 0.72rem; font-weight: 700; color: #10B981; background: {c['emerald_bg']}; padding: 2px 6px; border-radius: 6px;">2.0</span>
            </div>
            <div style="color: {c['muted']}; font-size: 0.85rem; font-weight: 500; display: flex; align-items: center; gap: 6px;">
                <span>Home</span>
                <span style="color: {c['border']}; font-size: 0.75rem;">/</span>
                <span>Climate Intelligence</span>
                <span style="color: {c['border']}; font-size: 0.75rem;">/</span>
                <span style="color: {c['text_dark']}; font-weight: 600;">{breadcrumb_step}</span>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 6px; background: {c['surface']}; padding: 5px 12px; border-radius: 9999px; border: 1px solid {c['border']}; font-size: 0.75rem; color: {c['muted']}; font-family: 'JetBrains Mono', monospace;">
                <span style="color: #10B981;">●</span> EDGAR 2026 JRC (1970–2025)
            </div>
            <div style="width: 32px; height: 32px; border-radius: 50%; background: {c['surface']}; border: 1px solid {c['border']}; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; color: {c['muted']}; cursor: pointer;" title="Notifications Active">
                🔔
            </div>
            <div style="display: flex; align-items: center; gap: 8px; background: {c['surface']}; padding: 4px 10px 4px 6px; border-radius: 9999px; border: 1px solid {c['border']};">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: linear-gradient(135deg, #10B981, #065F46); color: white; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700;">
                    CA
                </div>
                <span style="font-size: 0.78rem; font-weight: 600; color: {c['text']};">Analyst</span>
            </div>
        </div>
    </div>
    """
    render_html(html)


def render_page_header(title: str, subtitle: str, badge: str = "EDGAR 2026 VERIFIED"):
    """Render standardized top header across all dashboard pages."""
    c = get_current_palette()
    html = f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 22px;">
        <div>
            <div style="font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: {c['muted']}; margin-bottom: 4px;">
                Climate Intelligence Platform
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <h1 style="font-size: 1.85rem; font-weight: 800; color: {c['text_dark']}; margin: 0; letter-spacing: -0.025em; line-height: 1.2;">
                    {title}
                </h1>
                <span class="pill-forest">{badge}</span>
            </div>
            <p style="font-size: 0.9rem; color: {c['muted']}; margin: 6px 0 0 0; max-width: 820px; line-height: 1.5;">
                {subtitle}
            </p>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <div class="pill-neutral" style="cursor: pointer;" title="Active Filters Applied">
                Filter ⎚
            </div>
            <div class="pill-neutral" style="cursor: pointer;" title="Sort Trajectories">
                Sort ⇅
            </div>
            <div class="pill-mint" style="cursor: pointer;" title="Refresh Data Engine">
                Refresh ↻
            </div>
        </div>
    </div>
    """
    render_html(html)


def render_metric_card(
    title: str,
    value: str,
    unit: str = "",
    delta_text: str = "",
    is_reduction_positive: bool = True,
    badge: Optional[str] = None
):
    """
    Render a styled climate KPI metric card matching the reference design:
    - Large bold typography
    - Rounded pill indicators (green for reduction / negative, rose for increase)
    - Clean unit indicator
    """
    c = get_current_palette()
    pill_html = ""
    if delta_text:
        is_negative = ("-" in delta_text) or ("↓" in delta_text)
        if is_reduction_positive:
            badge_class = "pill-mint" if is_negative else "pill-rose"
        else:
            badge_class = "pill-mint" if not is_negative else "pill-rose"
        pill_html = f'<span class="{badge_class}">{delta_text}</span>'

    badge_top = f'<span class="pill-neutral" style="font-size: 0.68rem;">{badge}</span>' if badge else ""

    html = f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <div class="kpi-title-row">
                <span>{title}</span>
            </div>
            {badge_top}
        </div>
        <div class="kpi-value-row">
            <span class="kpi-value">{value}</span>
            {f'<span class="kpi-unit">{unit}</span>' if unit else ''}
        </div>
        <div class="kpi-footer">
            {pill_html}
            <span style="font-size: 0.72rem; color: {c['muted_light']}; font-family: 'JetBrains Mono', monospace;">Verified</span>
        </div>
    </div>
    """
    render_html(html)


def render_scope_breakdown_card(
    title: str = "Study Support",
    subtitle: str = "Available Data",
    items: Optional[List[Dict[str, Any]]] = None
):
    """Render the breakdown table card seen in the reference image with soft rounded pill rows."""
    c = get_current_palette()
    if items is None:
        items = [
            {"label": "Scope 1 (Direct Emissions)", "value": "2.71 Gt CO₂", "active": True, "icon": "🔥"},
            {"label": "Scope 2 (Electricity & Heat)", "value": "0.41 Gt CO₂", "active": False, "icon": "⚡"},
            {"label": "Scope 3 (Supply & Transport)", "value": "1.15 Gt CO₂", "active": False, "icon": "🚛"}
        ]

    rows_html = ""
    for it in items:
        row_cls = "breakdown-row active" if it.get("active") else "breakdown-row default"
        icon = it.get("icon", "●")
        rows_html += f"""
        <div class="{row_cls}">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>{icon}</span>
                <span>{it['label']}</span>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">
                {it['value']}
            </div>
        </div>
        """

    html = f"""
    <div class="kpi-card" style="padding: 18px 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 0.8rem; font-weight: 700; color: {c['muted']}; text-transform: uppercase; letter-spacing: 0.05em;">
            <span>{title}</span>
            <span>{subtitle}</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            {rows_html}
        </div>
    </div>
    """
    render_html(html)


def render_scope_segmented_bar(
    title: str = "Emissions Per Scope",
    year_label: str = "In 2025",
    segments: Optional[List[Dict[str, Any]]] = None
):
    """Render the horizontal segmented bar seen in the reference image (coral & sky blue segments)."""
    c = get_current_palette()
    if segments is None:
        segments = [
            {"label": "Scope 1 (Fossil & Process)", "pct": 60, "color": c["scope1"]},
            {"label": "Scope 2 (Electricity & Steam)", "pct": 40, "color": c["scope2"]}
        ]

    bar_segments = ""
    legends_html = ""
    for seg in segments:
        bar_segments += f'<div style="width: {seg["pct"]}%; background: {seg["color"]};" title="{seg["label"]}: {seg["pct"]}%"></div>'
        legends_html += f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px; font-size: 0.82rem;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 3px; background: {seg['color']};"></span>
                <span style="color: {c['muted']}; font-weight: 500;">{seg['label']}</span>
            </div>
            <span style="font-weight: 700; color: {c['text_dark']}; font-family: 'JetBrains Mono', monospace;">{seg['pct']}%</span>
        </div>
        """

    html = f"""
    <div class="kpi-card" style="padding: 18px 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.85rem; font-weight: 700; color: {c['text_dark']};">{title}</span>
            <span style="font-size: 0.75rem; color: {c['muted']}; font-family: 'JetBrains Mono', monospace;">{year_label}</span>
        </div>
        <div class="segmented-progress">
            {bar_segments}
        </div>
        <div style="display: flex; flex-direction: column; gap: 2px;">
            {legends_html}
        </div>
    </div>
    """
    render_html(html)


def render_comparison_pill_card(
    category: str,
    substance: str,
    delta_str: str,
    amount_str: str,
    is_reduction: bool = True
):
    """Render the quick comparison card seen in the reference image (e.g. Natural gas ↓ 39% or Air conditioning ↑ 102%)."""
    c = get_current_palette()
    pill_cls = "pill-mint" if is_reduction else "pill-rose"
    arrow = "↓" if is_reduction else "↑"

    html = f"""
    <div class="kpi-card" style="padding: 16px 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.78rem; color: {c['muted']}; font-weight: 600;">{category}</span>
            <span class="{pill_cls}">{arrow} {delta_str}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <span style="font-size: 0.95rem; font-weight: 700; color: {c['text_dark']};">{substance}</span>
            <span style="font-size: 0.95rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: {c['text_dark']};">{amount_str}</span>
        </div>
    </div>
    """
    render_html(html)


def render_export_card():
    """Render the Export as CSV / Excel utility card matching the reference image."""
    c = get_current_palette()
    html = f"""
    <div class="kpi-card" style="padding: 16px 20px; display: flex; flex-direction: row; align-items: center; justify-content: space-between;">
        <div>
            <div style="font-size: 0.9rem; font-weight: 700; color: {c['text_dark']};">Export as CSV / Excel</div>
            <div style="font-size: 0.75rem; color: {c['muted']}; margin-top: 2px;">Complete 1970–2025 Dataset</div>
        </div>
        <div style="width: 40px; height: 40px; border-radius: 10px; background: #10B981; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 1.1rem; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">
            📊
        </div>
    </div>
    """
    render_html(html)


def render_disclaimer_card(text: str, title: str = "Scientific Methodology & Policy Notice"):
    """Render clean, credible scientific disclaimer for ML and scenario tools."""
    c = get_current_palette()
    html = f"""
    <div style="background: {c['surface_subtle']}; border: 1px solid {c['border']}; border-left: 4px solid #10B981; border-radius: 12px; padding: 14px 18px; margin: 16px 0;">
        <div style="font-size: 0.8rem; font-weight: 700; color: {c['text_dark']}; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
            <span>🛡️</span> {title}
        </div>
        <div style="font-size: 0.82rem; color: {c['muted']}; line-height: 1.5;">
            {text}
        </div>
    </div>
    """
    render_html(html)
