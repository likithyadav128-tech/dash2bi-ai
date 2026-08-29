"""
Mapping Review & Manual Override Editor UI for Dash2BI AI.
"""

import streamlit as st
from typing import List, Dict, Any
from src.mapping.confidence import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW

def render_mapping_review_table(mapped_visuals: List[Dict[str, Any]], dataset_cols: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Renders an interactive mapping table allowing users to inspect and override field/visual mappings.
    Returns the updated list of mapped visuals.
    """
    st.markdown("### 🧩 Field & Visual Mapping Review")
    st.caption("Review the detected dashboard elements, target dataset fields, confidence levels, and DAX calculations.")

    col_names = [c["original_name"] for c in dataset_cols]
    updated_visuals = []

    for idx, v in enumerate(mapped_visuals):
        with st.expander(f"Visual {idx+1}: **{v['title']}** ({v['html_type'].replace('_', ' ').title()})", expanded=(v['status'] == 'NEEDS REVIEW')):
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                st.markdown(f"**Detected Title:** {v['title']}")
                st.markdown(f"**HTML Element:** `{v['html_type']}`")
                st.markdown(f"**Source Snippet:** `{v.get('source_html', '')[:60]}...`")

            with col2:
                status_color = "🟢" if v["status"] == "READY" else "🟡"
                st.markdown(f"**Status:** {status_color} {v['status']}")
                st.markdown(f"**Confidence:** `{v['confidence_level']}` ({v['score']*100:.0f}%)")
                st.markdown(f"**Match Type:** `{v['match_type']}`")

            with col3:
                # Manual Override Controls
                default_field_idx = col_names.index(v['mapped_field']) if v['mapped_field'] in col_names else 0
                new_field = st.selectbox(
                    f"Mapped Field ({v['visual_id']}):",
                    options=col_names,
                    index=default_field_idx,
                    key=f"field_sel_{v['visual_id']}"
                )

                new_agg = st.selectbox(
                    f"Aggregation ({v['visual_id']}):",
                    options=["SUM", "AVERAGE", "COUNT", "DISTINCTCOUNT", "DIVIDE", "MIN", "MAX"],
                    index=["SUM", "AVERAGE", "COUNT", "DISTINCTCOUNT", "DIVIDE", "MIN", "MAX"].index(v.get('aggregation', 'SUM')),
                    key=f"agg_sel_{v['visual_id']}"
                )

            # Show Explanation
            st.info(v.get("explanation", "Mapped based on semantic analysis."))

            # Update spec
            v_copy = dict(v)
            v_copy['mapped_field'] = new_field
            v_copy['aggregation'] = new_agg
            updated_visuals.append(v_copy)

    return updated_visuals
