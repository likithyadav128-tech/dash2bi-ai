"""
Visual Wireframe & Live Interactive Dashboard Reconstruction Preview UI for Dash2BI AI.
Renders real Plotly interactive visual mockups and 2D spatial canvas placement directly on the Streamlit webpage.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any, Optional

def _find_numeric_col(df: pd.DataFrame, hint: str = "") -> Optional[str]:
    """Find the best numeric column from df, preferring one matching hint."""
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not num_cols:
        return None
    if hint:
        hint_lower = hint.strip().lower()
        for c in num_cols:
            if c.lower() == hint_lower:
                return c
        for c in num_cols:
            if hint_lower in c.lower() or c.lower() in hint_lower:
                return c
    return num_cols[0]

def _find_category_col(df: pd.DataFrame, hint: str = "") -> Optional[str]:
    """Find the best categorical/string column from df, preferring one matching hint."""
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if not cat_cols:
        return None
    if hint:
        hint_lower = hint.strip().lower()
        for c in cat_cols:
            if c.lower() == hint_lower:
                return c
        for c in cat_cols:
            if hint_lower in c.lower() or c.lower() in hint_lower:
                return c
    return cat_cols[0]

def _find_date_col(df: pd.DataFrame) -> Optional[str]:
    """Find a date/datetime column."""
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            return c
    # Heuristic: look for column names suggesting date
    for c in df.columns:
        if any(kw in c.lower() for kw in ["date", "time", "day", "month", "year", "period"]):
            try:
                pd.to_datetime(df[c].dropna().head(20))
                return c
            except Exception:
                continue
    return None

def _compute_kpi_value(df: pd.DataFrame, visual: Dict[str, Any]) -> str:
    """Compute the actual KPI numeric value from the dataframe."""
    field = visual.get("mapped_field", "")
    title = visual.get("title", "").upper()

    # Try domain-specific composite calculations
    if "CONFIRMED" in title and "ConfirmedIndianNational" in df.columns:
        val = df["ConfirmedIndianNational"].sum()
        if "ConfirmedForeignNational" in df.columns:
            val += df["ConfirmedForeignNational"].sum()
        return f"{int(val):,}"
    if "ACTIVE" in title and "ConfirmedIndianNational" in df.columns and "Cured" in df.columns:
        conf = df["ConfirmedIndianNational"].sum() + (df["ConfirmedForeignNational"].sum() if "ConfirmedForeignNational" in df.columns else 0)
        act = conf - df["Cured"].sum() - (df["Deaths"].sum() if "Deaths" in df.columns else 0)
        return f"{int(act):,}"

    # Try direct field
    if field and field in df.columns and pd.api.types.is_numeric_dtype(df[field]):
        return f"{df[field].sum():,.0f}"

    # Try matching field name heuristically
    num_col = _find_numeric_col(df, field)
    if num_col:
        return f"{df[num_col].sum():,.0f}"

    return "N/A"

def render_reconstruction_wireframe(
    mapped_visuals: List[Dict[str, Any]],
    score_data: Dict[str, Any],
    raw_df: Optional[pd.DataFrame] = None
):
    """
    Renders both a Live Plotly Dashboard Visual Mockup and a 2D Power BI Canvas Layout preview.
    """
    st.markdown("### 🖥️ Power BI Dashboard Visual Preview")
    st.caption("Live Interactive Mockup & 2D Spatial Layout Preview (1280×720 Canvas)")

    # Header bar
    st.markdown("""
        <div style="background-color: #1E293B; padding: 12px 20px; border-top-left-radius: 10px; border-top-right-radius: 10px; color: white; font-weight: bold; font-size: 1.1rem; display: flex; justify-content: space-between; align-items: center;">
            <span>📊 Power BI Report Canvas — Live Preview</span>
            <span style="font-size: 0.85rem; background: #0F172A; padding: 4px 10px; border-radius: 12px; color: #38BDF8;">
                Reconstruction Score: {score}/100
            </span>
        </div>
    """.format(score=score_data.get('overall_score', 100)), unsafe_allow_html=True)

    with st.container():
        st.markdown('<div style="background: #F1F5F9; border: 1px solid #CBD5E1; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; padding: 20px; margin-bottom: 25px;">', unsafe_allow_html=True)

        # ── KPI Cards Row ──
        kpis = [v for v in mapped_visuals if v["html_type"] in ["kpi_card", "metric_card"]]
        if kpis:
            kpi_cols = st.columns(min(len(kpis), 4))
            for idx, k in enumerate(kpis[:4]):
                with kpi_cols[idx % len(kpi_cols)]:
                    if raw_df is not None and not raw_df.empty:
                        val = _compute_kpi_value(raw_df, k)
                    else:
                        val = "—"
                    st.markdown(f"""
                        <div style="background: white; border-radius: 10px; padding: 18px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.08); border-left: 4px solid #3B82F6;">
                            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">{k['title']}</div>
                            <div style="font-size: 1.8rem; font-weight: 800; color: #0F172A;">{val}</div>
                            <div style="font-size: 0.7rem; color: #22C55E; margin-top: 4px;">✓ 100% READY</div>
                        </div>
                    """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts Section ──
        charts = [v for v in mapped_visuals if "chart" in v["html_type"]]
        if charts and raw_df is not None and not raw_df.empty:
            chart_cols = st.columns(min(len(charts), 2))
            for idx, c_spec in enumerate(charts[:4]):
                with chart_cols[idx % 2]:
                    p_type = c_spec.get("powerbi_type", "barChart")
                    field_hint = c_spec.get("mapped_field", "")

                    try:
                        if p_type == "lineChart":
                            date_col = _find_date_col(raw_df)
                            num_col = _find_numeric_col(raw_df, field_hint)
                            if date_col and num_col:
                                df_plot = raw_df.copy()
                                df_plot[date_col] = pd.to_datetime(df_plot[date_col], errors="coerce")
                                df_plot = df_plot.dropna(subset=[date_col])
                                df_agg = df_plot.groupby(date_col)[num_col].sum().reset_index()
                                fig = px.line(df_agg, x=date_col, y=num_col, title=c_spec["title"], template="plotly_white")
                                fig.update_layout(height=280, margin=dict(l=30, r=20, t=40, b=30))
                                fig.update_traces(line_color="#3B82F6")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                _render_chart_placeholder(c_spec)

                        elif p_type in ["pieChart", "donutChart"]:
                            cat_col = _find_category_col(raw_df, field_hint)
                            num_col = _find_numeric_col(raw_df, "")
                            if cat_col and num_col:
                                df_pie = raw_df.groupby(cat_col)[num_col].sum().nlargest(6).reset_index()
                                hole = 0.45 if p_type == "donutChart" else 0.4
                                fig = px.pie(df_pie, names=cat_col, values=num_col, title=c_spec["title"], hole=hole, template="plotly_white",
                                             color_discrete_sequence=px.colors.qualitative.Set2)
                                fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                _render_chart_placeholder(c_spec)

                        elif p_type in ["barChart", "columnChart"]:
                            cat_col = _find_category_col(raw_df, field_hint)
                            num_col = _find_numeric_col(raw_df, "")
                            if cat_col and num_col:
                                df_bar = raw_df.groupby(cat_col)[num_col].sum().nlargest(8).reset_index()
                                orientation = "h" if p_type == "barChart" else "v"
                                if orientation == "h":
                                    fig = px.bar(df_bar, y=cat_col, x=num_col, title=c_spec["title"], orientation="h", template="plotly_white",
                                                 color_discrete_sequence=["#3B82F6"])
                                else:
                                    fig = px.bar(df_bar, x=cat_col, y=num_col, title=c_spec["title"], template="plotly_white",
                                                 color_discrete_sequence=["#3B82F6"])
                                fig.update_layout(height=280, margin=dict(l=30, r=20, t=40, b=30))
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                _render_chart_placeholder(c_spec)

                        else:
                            _render_chart_placeholder(c_spec)

                    except Exception as e:
                        _render_chart_placeholder(c_spec)

        elif charts:
            chart_cols = st.columns(2)
            for idx, c_spec in enumerate(charts[:4]):
                with chart_cols[idx % 2]:
                    _render_chart_placeholder(c_spec)

        # ── Slicers / Filters ──
        filters = [v for v in mapped_visuals if v["html_type"] in ["slicer", "date_slicer"]]
        if filters:
            st.markdown("<br>", unsafe_allow_html=True)
            f_cols = st.columns(min(len(filters), 3))
            for idx, flt in enumerate(filters[:3]):
                with f_cols[idx % len(f_cols)]:
                    field = flt.get("mapped_field", "Filter")
                    st.markdown(f"""
                        <div style="background: white; border-radius: 8px; padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border-top: 3px solid #8B5CF6;">
                            <div style="font-size: 0.7rem; color: #8B5CF6; text-transform: uppercase; letter-spacing: 1px;">🎛️ Slicer</div>
                            <div style="font-weight: 600; color: #1E293B; margin-top: 4px;">{flt['title']}</div>
                            <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">Field: {field}</div>
                        </div>
                    """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Collapsible Coordinate Wireframe Table ──
    with st.expander("📍 View 2D Spatial Layout Coordinate Wireframe (1280×720 Canvas Specs)"):
        coords_data = []
        for v in mapped_visuals:
            coords_data.append({
                "Visual ID": v["visual_id"],
                "Title": v["title"],
                "Power BI Type": v["powerbi_type"],
                "Target Field": v.get("mapped_field"),
                "X (px)": v["layout"]["x"],
                "Y (px)": v["layout"]["y"],
                "Width (px)": v["layout"]["width"],
                "Height (px)": v["layout"]["height"],
                "Status": v["status"]
            })
        st.dataframe(pd.DataFrame(coords_data), use_container_width=True)

def _render_chart_placeholder(c_spec: Dict[str, Any]):
    """Renders a styled placeholder card for a chart when data isn't available."""
    st.markdown(f"""
        <div style="background: white; border-radius: 10px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); border-top: 3px solid #F59E0B; min-height: 150px;">
            <div style="font-weight: 700; color: #1E293B; margin-bottom: 8px;">📈 {c_spec['title']}</div>
            <div style="font-size: 0.85rem; color: #64748B;">
                <b>Type:</b> <code>{c_spec.get('powerbi_type', 'chart')}</code><br>
                <b>Field:</b> <code>{c_spec.get('mapped_field', 'N/A')}</code><br>
                <b>Position:</b> (x={c_spec['layout']['x']}, y={c_spec['layout']['y']}, w={c_spec['layout']['width']}, h={c_spec['layout']['height']})
            </div>
        </div>
    """, unsafe_allow_html=True)
