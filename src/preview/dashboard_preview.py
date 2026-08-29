"""
Visual Wireframe & Dashboard Reconstruction Preview UI for Dash2BI AI.
"""

import streamlit as st
from typing import List, Dict, Any

def render_reconstruction_wireframe(mapped_visuals: List[Dict[str, Any]], score_data: Dict[str, Any]):
    """Renders visual layout wireframe representing the Power BI canvas (1280x720)."""
    st.markdown("### 🖥️ Reconstructed Power BI Canvas Layout")
    st.caption("2D Spatial Layout Wireframe (1280x720 canvas coordinates)")

    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; border: 2px dashed #0d6efd; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <span style="font-weight: bold; color: #0d6efd;">📊 Power BI Reconstructed Page</span>
                <span style="font-weight: bold; background: #e7f1ff; color: #0d6efd; padding: 4px 12px; border-radius: 12px;">
                    Reconstruction Score: {score_data.get('overall_score', 0)}/100
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render KPIs row
    kpis = [v for v in mapped_visuals if v["html_type"] in ["kpi_card", "metric_card"]]
    if kpis:
        st.markdown("**KPI Cards Placement:**")
        cols = st.columns(min(len(kpis), 4))
        for idx, k in enumerate(kpis):
            with cols[idx % len(cols)]:
                st.metric(
                    label=k["title"],
                    value=f"SUM('{k.get('mapped_field', 'Sales')}')",
                    delta=f"{k['score']*100:.0f}% confidence"
                )

    # Render Charts grid
    charts = [v for v in mapped_visuals if "chart" in v["html_type"]]
    if charts:
        st.markdown("**Visual Charts Placement:**")
        cols = st.columns(2)
        for idx, c in enumerate(charts):
            with cols[idx % 2]:
                st.info(f"📈 **{c['title']}**\n- Type: `{c['powerbi_type']}`\n- Field: `{c.get('mapped_field')}`\n- Position: (x={c['layout']['x']}, y={c['layout']['y']}, w={c['layout']['width']}, h={c['layout']['height']})")

    # Render Tables & Filters
    tables_filters = [v for v in mapped_visuals if v["html_type"] in ["table", "slicer", "date_slicer"]]
    if tables_filters:
        st.markdown("**Tables & Slicers Placement:**")
        for tf in tables_filters:
            st.warning(f"🎛️ **{tf['title']}** — `{tf['powerbi_type']}` bound to `{tf.get('mapped_field')}`")
