"""
Visual Wireframe & Live Interactive Dashboard Reconstruction Preview UI for Dash2BI AI.
Renders real Plotly interactive visual mockups and 2D spatial canvas placement directly on the Streamlit webpage.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any, Optional

def render_reconstruction_wireframe(
    mapped_visuals: List[Dict[str, Any]],
    score_data: Dict[str, Any],
    raw_df: Optional[pd.DataFrame] = None
):
    """
    Renders both a Live Plotly Dashboard Visual Mockup and a 2D Power BI Canvas Layout preview.
    """
    st.markdown("### 🖥️ Power BI Dashboard Visual Preview")
    st.caption("Live Interactive Mockup & 2D Spatial Layout Preview (1280x720 Canvas)")

    # 1. Live Interactive Visual Mockup
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

        # KPI Row
        kpis = [v for v in mapped_visuals if v["html_type"] in ["kpi_card", "metric_card"]]
        if kpis:
            kpi_cols = st.columns(min(len(kpis), 4))
            for idx, k in enumerate(kpis[:4]):
                val_str = "0"
                if raw_df is not None:
                    field = k.get("mapped_field")
                    if field and field in raw_df.columns and pd.api.types.is_numeric_dtype(raw_df[field]):
                        val_str = f"{raw_df[field].sum():,}"
                    elif "CONFIRMED" in k["title"].upper() and "ConfirmedIndianNational" in raw_df.columns:
                        conf_tot = raw_df["ConfirmedIndianNational"].sum() + (raw_df["ConfirmedForeignNational"].sum() if "ConfirmedForeignNational" in raw_df.columns else 0)
                        val_str = f"{conf_tot:,}"
                    elif "ACTIVE" in k["title"].upper() and "ConfirmedIndianNational" in raw_df.columns and "Cured" in raw_df.columns:
                        conf_tot = raw_df["ConfirmedIndianNational"].sum() + (raw_df["ConfirmedForeignNational"].sum() if "ConfirmedForeignNational" in raw_df.columns else 0)
                        act_tot = conf_tot - raw_df["Cured"].sum() - (raw_df["Deaths"].sum() if "Deaths" in raw_df.columns else 0)
                        val_str = f"{act_tot:,}"

                with kpi_cols[idx % len(kpi_cols)]:
                    st.metric(
                        label=k["title"],
                        value=val_str if val_str != "0" else f"SUM('{k.get('mapped_field', 'Metric')}')",
                        delta="✓ 100% READY"
                    )

        st.markdown("---")

        # Charts Section using Plotly
        charts = [v for v in mapped_visuals if "chart" in v["html_type"]]
        if charts and raw_df is not None:
            c_cols = st.columns(min(len(charts), 2))
            for idx, c_spec in enumerate(charts[:4]):
                with c_cols[idx % 2]:
                    st.markdown(f"#### {c_spec['title']}")
                    p_type = c_spec["powerbi_type"]
                    f_name = c_spec.get("mapped_field")

                    try:
                        if p_type == "lineChart" and "Date" in raw_df.columns:
                            num_col = "ConfirmedIndianNational" if "ConfirmedIndianNational" in raw_df.columns else raw_df.select_dtypes(include=['number']).columns[0]
                            df_trend = raw_df.groupby("Date")[num_col].sum().reset_index()
                            fig = px.line(df_trend, x="Date", y=num_col, title=c_spec["title"], template="plotly_white")
                            fig.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=20))
                            st.plotly_chart(fig, use_container_width=True)

                        elif p_type == "pieChart" and "State/UnionTerritory" in raw_df.columns:
                            num_col = "ConfirmedIndianNational" if "ConfirmedIndianNational" in raw_df.columns else raw_df.select_dtypes(include=['number']).columns[0]
                            df_pie = raw_df.groupby("State/UnionTerritory")[num_col].sum().nlargest(5).reset_index()
                            fig = px.pie(df_pie, names="State/UnionTerritory", values=num_col, title=c_spec["title"], hole=0.4, template="plotly_white")
                            fig.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=20))
                            st.plotly_chart(fig, use_container_width=True)

                        elif p_type in ["barChart", "columnChart"] and "State/UnionTerritory" in raw_df.columns:
                            num_col = "Cured" if "Cured" in raw_df.columns else raw_df.select_dtypes(include=['number']).columns[0]
                            df_bar = raw_df.groupby("State/UnionTerritory")[num_col].sum().nlargest(7).reset_index()
                            fig = px.bar(df_bar, x="State/UnionTerritory", y=num_col, title=c_spec["title"], template="plotly_white")
                            fig.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=20))
                            st.plotly_chart(fig, use_container_width=True)

                        else:
                            st.info(f"📈 **{c_spec['title']}** (`{p_type}` bound to `{f_name}`)")

                    except Exception:
                        st.info(f"📈 **{c_spec['title']}** (`{p_type}` bound to `{f_name}`)")

        elif charts:
            c_cols = st.columns(2)
            for idx, c_spec in enumerate(charts[:4]):
                with c_cols[idx % 2]:
                    st.info(f"📈 **{c_spec['title']}**\n- Type: `{c_spec['powerbi_type']}`\n- Field: `{c_spec.get('mapped_field')}`\n- Position: (x={c_spec['layout']['x']}, y={c_spec['layout']['y']}, w={c_spec['layout']['width']}, h={c_spec['layout']['height']})")

        st.markdown('</div>', unsafe_allow_html=True)

    # 2. Detailed Spatial Coordinate Wireframe Table
    with st.expander("📍 View 2D Spatial Layout Coordinate Wireframe (1280x720 Canvas Specs)"):
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
