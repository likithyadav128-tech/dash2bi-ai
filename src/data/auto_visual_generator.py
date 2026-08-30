"""
Auto Visual Generator for Dash2BI AI.
Automatically synthesizes full Power BI report visual specifications (KPI cards, line trend charts, bar charts, pie charts, slicers, and tables) directly from a raw dataset schema (CSV / Excel) without requiring an HTML file.
"""

import re
from typing import Dict, Any, List, Tuple

# Patterns for ID / Serial columns to exclude from primary metrics
IGNORE_ID_PATTERNS = re.compile(r'^(sno|sn|s_no|sl_no|slno|id|index|row_id|key|uuid|guid|code|number|num)$', re.I)

def auto_generate_visuals(
    table_name: str,
    dataset_cols: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Analyzes dataset columns and automatically generates:
    1. html_visuals: Visual components structure (compatible with wireframe renderer and parser).
    2. mapped_visuals: Fully resolved, ready-to-export visual specifications.
    
    Returns (html_visuals, mapped_visuals).
    """
    if not dataset_cols:
        return [], []

    # Categorize columns
    measures = []
    dimensions = []
    date_cols = []

    for col in dataset_cols:
        name = col["original_name"]
        role = col.get("role", "Dimension")
        d_type = col.get("data_type", "string")

        if IGNORE_ID_PATTERNS.match(name.strip().lower()):
            continue

        if role == "Date" or "date" in name.lower() or "year" in name.lower() or "time" in name.lower():
            date_cols.append(name)
        elif role == "Measure" or d_type in ["int64", "float64"]:
            measures.append(name)
        else:
            dimensions.append(name)

    # Fallbacks if categories are sparse
    if not measures:
        measures = [c["original_name"] for c in dataset_cols if not IGNORE_ID_PATTERNS.match(c["original_name"].strip().lower())]
    if not measures:
        measures = [dataset_cols[0]["original_name"]]

    if not dimensions:
        dimensions = [c["original_name"] for c in dataset_cols if c["original_name"] not in measures]
    if not dimensions:
        dimensions = [dataset_cols[0]["original_name"]]

    primary_measure = measures[0]
    secondary_measure = measures[1] if len(measures) > 1 else primary_measure
    third_measure = measures[2] if len(measures) > 2 else primary_measure
    fourth_measure = measures[3] if len(measures) > 3 else primary_measure

    primary_dimension = dimensions[0]
    secondary_dimension = dimensions[1] if len(dimensions) > 1 else primary_dimension
    primary_date = date_cols[0] if date_cols else None

    html_visuals = []
    mapped_visuals = []

    # 1. Generate KPI Cards (Up to 4 top measures)
    kpi_measures = [primary_measure, secondary_measure, third_measure, fourth_measure]
    for idx, m_name in enumerate(kpi_measures):
        v_id = f"kpi_{idx + 1}"
        x_pos = 15 + (idx * 253)
        y_pos = 80
        width = 238
        height = 110

        vis_item = {
            "visual_id": v_id,
            "visual_type": "kpi_card",
            "title": m_name.upper(),
            "extracted_text": m_name.upper(),
            "attributes": {"id": f"kpi_{idx + 1}"},
            "layout": {"x": x_pos, "y": y_pos, "width": width, "height": height},
            "raw_html": f"<div class='kpi'><h2>{m_name.upper()}</h2></div>"
        }
        html_visuals.append(vis_item)

        mapped_item = {
            "visual_id": v_id,
            "html_type": "kpi_card",
            "powerbi_type": "card",
            "title": m_name.upper(),
            "mapped_field": m_name,
            "aggregation": "SUM",
            "score": 1.0,
            "confidence_level": "HIGH",
            "match_type": "EXACT",
            "status": "READY",
            "explanation": f"Auto-generated KPI metric card for '{m_name}'.",
            "layout": {"x": x_pos, "y": y_pos, "width": width, "height": height},
            "source_html": vis_item["raw_html"],
            "measure_name": m_name.upper()
        }
        mapped_visuals.append(mapped_item)

    # 2. Main Visual Charts Grid (4 Charts)
    # Chart 1: Time Series Trend (if date exists) or Bar Chart
    c1_title = f"📈 {primary_measure} Trend over {primary_date}" if primary_date else f"📈 {primary_measure} by {primary_dimension}"
    c1_field = primary_date if primary_date else primary_dimension
    c1_pbi_type = "lineChart" if primary_date else "barChart"

    vis_c1 = {
        "visual_id": "chart_1",
        "visual_type": "bar_chart",
        "title": c1_title,
        "extracted_text": c1_title,
        "attributes": {"id": "trend"},
        "layout": {"x": 15, "y": 205, "width": 617, "height": 250},
        "raw_html": "<div class='chart' id='trend'></div>"
    }
    html_visuals.append(vis_c1)
    mapped_visuals.append({
        "visual_id": "chart_1",
        "html_type": "bar_chart",
        "powerbi_type": c1_pbi_type,
        "title": c1_title,
        "mapped_field": c1_field,
        "aggregation": "SUM",
        "score": 1.0,
        "confidence_level": "HIGH",
        "match_type": "SMART_TREND_MATCH" if primary_date else "SMART_DIM_MATCH",
        "status": "READY",
        "explanation": f"Auto-generated trend chart for '{primary_measure}'.",
        "layout": {"x": 15, "y": 205, "width": 617, "height": 250},
        "source_html": vis_c1["raw_html"],
        "measure_name": primary_measure.upper()
    })

    # Chart 2: Categorical Dimension Breakdown
    c2_title = f"🏆 Top {primary_dimension} by {primary_measure}"
    vis_c2 = {
        "visual_id": "chart_2",
        "visual_type": "bar_chart",
        "title": c2_title,
        "extracted_text": c2_title,
        "attributes": {"id": "bar_cat"},
        "layout": {"x": 647, "y": 205, "width": 617, "height": 250},
        "raw_html": "<div class='chart' id='bar_cat'></div>"
    }
    html_visuals.append(vis_c2)
    mapped_visuals.append({
        "visual_id": "chart_2",
        "html_type": "bar_chart",
        "powerbi_type": "barChart",
        "title": c2_title,
        "mapped_field": primary_dimension,
        "aggregation": "SUM",
        "score": 1.0,
        "confidence_level": "HIGH",
        "match_type": "SMART_DIM_MATCH",
        "status": "READY",
        "explanation": f"Auto-generated categorical breakdown chart by '{primary_dimension}'.",
        "layout": {"x": 647, "y": 205, "width": 617, "height": 250},
        "source_html": vis_c2["raw_html"],
        "measure_name": primary_measure.upper()
    })

    # Chart 3: Proportional Share (Pie / Donut Chart)
    c3_title = f"🥧 {secondary_measure} Share by {primary_dimension}"
    vis_c3 = {
        "visual_id": "chart_3",
        "visual_type": "bar_chart",
        "title": c3_title,
        "extracted_text": c3_title,
        "attributes": {"id": "pie_share"},
        "layout": {"x": 15, "y": 480, "width": 617, "height": 250},
        "raw_html": "<div class='chart' id='pie_share'></div>"
    }
    html_visuals.append(vis_c3)
    mapped_visuals.append({
        "visual_id": "chart_3",
        "html_type": "bar_chart",
        "powerbi_type": "pieChart",
        "title": c3_title,
        "mapped_field": primary_dimension,
        "aggregation": "SUM",
        "score": 1.0,
        "confidence_level": "HIGH",
        "match_type": "SMART_DIM_MATCH",
        "status": "READY",
        "explanation": f"Auto-generated proportional share chart by '{primary_dimension}'.",
        "layout": {"x": 15, "y": 480, "width": 617, "height": 250},
        "source_html": vis_c3["raw_html"],
        "measure_name": secondary_measure.upper()
    })

    # Chart 4: Secondary Dimension Breakdown (Column Chart)
    c4_title = f"📊 {third_measure} by {secondary_dimension}"
    vis_c4 = {
        "visual_id": "chart_4",
        "visual_type": "bar_chart",
        "title": c4_title,
        "extracted_text": c4_title,
        "attributes": {"id": "col_sec"},
        "layout": {"x": 647, "y": 480, "width": 617, "height": 250},
        "raw_html": "<div class='chart' id='col_sec'></div>"
    }
    html_visuals.append(vis_c4)
    mapped_visuals.append({
        "visual_id": "chart_4",
        "html_type": "bar_chart",
        "powerbi_type": "columnChart",
        "title": c4_title,
        "mapped_field": secondary_dimension,
        "aggregation": "SUM",
        "score": 1.0,
        "confidence_level": "HIGH",
        "match_type": "SMART_DIM_MATCH",
        "status": "READY",
        "explanation": f"Auto-generated breakdown chart for '{secondary_dimension}'.",
        "layout": {"x": 647, "y": 480, "width": 617, "height": 250},
        "source_html": vis_c4["raw_html"],
        "measure_name": third_measure.upper()
    })

    # 3. Slicers
    # Categorical Slicer
    vis_s1 = {
        "visual_id": "filter_1",
        "visual_type": "slicer",
        "title": f"{primary_dimension} Filter",
        "extracted_text": primary_dimension,
        "attributes": {"id": "filter_dim"},
        "layout": {"x": 1045, "y": 20, "width": 220, "height": 90},
        "raw_html": "<select id='dim_select'></select>"
    }
    html_visuals.append(vis_s1)
    mapped_visuals.append({
        "visual_id": "filter_1",
        "html_type": "slicer",
        "powerbi_type": "slicer",
        "title": primary_dimension,
        "mapped_field": primary_dimension,
        "aggregation": "SUM",
        "score": 1.0,
        "confidence_level": "HIGH",
        "match_type": "EXACT",
        "status": "READY",
        "explanation": f"Auto-generated slicer for dimension '{primary_dimension}'.",
        "layout": {"x": 1045, "y": 20, "width": 220, "height": 90},
        "source_html": vis_s1["raw_html"]
    })

    # Date Slicer (if date exists)
    if primary_date:
        vis_ds = {
            "visual_id": "date_filter_1",
            "visual_type": "date_slicer",
            "title": f"{primary_date} Range",
            "extracted_text": primary_date,
            "attributes": {"id": "date_select"},
            "layout": {"x": 20, "y": 20, "width": 300, "height": 90},
            "raw_html": "<input type='date'/>"
        }
        html_visuals.append(vis_ds)
        mapped_visuals.append({
            "visual_id": "date_filter_1",
            "html_type": "date_slicer",
            "powerbi_type": "slicer",
            "title": primary_date,
            "mapped_field": primary_date,
            "aggregation": "SUM",
            "score": 1.0,
            "confidence_level": "HIGH",
            "match_type": "EXACT",
            "status": "READY",
            "explanation": f"Auto-generated date range slicer for '{primary_date}'.",
            "layout": {"x": 20, "y": 20, "width": 300, "height": 90},
            "source_html": vis_ds["raw_html"]
        })

    return html_visuals, mapped_visuals
