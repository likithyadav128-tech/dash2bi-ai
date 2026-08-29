"""
Visual Component Mapper module for Dash2BI AI.
Maps HTML visual components to Power BI visual types and schema bindings.
"""

from typing import Dict, Any, List, Optional
from src.mapping.field_mapper import map_label_to_dataset_field
from src.mapping.confidence import get_confidence_level, build_mapping_explanation

# Power BI Visual Type Equivalents
POWERBI_VISUAL_MAP = {
    "kpi_card": "card",
    "metric_card": "card",
    "bar_chart": "barChart",
    "column_chart": "columnChart",
    "line_chart": "lineChart",
    "area_chart": "areaChart",
    "pie_chart": "pieChart",
    "donut_chart": "donutChart",
    "scatter_chart": "scatterChart",
    "gauge": "gauge",
    "table": "tableEx",
    "matrix": "pivotTable",
    "slicer": "slicer",
    "date_slicer": "slicer",
    "title": "textbox",
    "subtitle": "textbox",
    "text_box": "textbox"
}

def map_visual_to_powerbi(
    visual: Dict[str, Any],
    dataset_cols: List[Dict[str, Any]],
    ai_suggestions: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Transforms an extracted HTML visual object into a fully resolved Power BI visual spec.
    """
    html_type = visual.get("visual_type", "table")
    title = visual.get("title", "")
    pbi_visual_type = POWERBI_VISUAL_MAP.get(html_type, "tableEx")
    
    # Check if AI suggestion exists for this visual ID
    ai_item = None
    if ai_suggestions and "mappings" in ai_suggestions:
        for item in ai_suggestions["mappings"]:
            if item.get("visual_id") == visual.get("visual_id"):
                ai_item = item
                break

    matched_field = None
    score = 0.0
    match_type = "NONE"
    reasons = []

    if ai_item and ai_item.get("dataset_field"):
        matched_field = ai_item["dataset_field"]
        score = float(ai_item.get("confidence", 0.90))
        match_type = "AI_ASSISTED"
        reasons.append(ai_item.get("reason", "Mapped via Claude AI semantic analysis."))
    else:
        # Fallback to hybrid deterministic matching
        matched_field, score, match_type, reasons = map_label_to_dataset_field(title, dataset_cols)

    # Infer aggregation for KPIs and Charts
    aggregation = "SUM"
    if html_type in ["kpi_card", "metric_card"]:
        title_lower = title.lower()
        if "count" in title_lower or "orders" in title_lower or "number" in title_lower:
            aggregation = "COUNT"
        elif "avg" in title_lower or "average" in title_lower or "mean" in title_lower:
            aggregation = "AVERAGE"
        elif "margin" in title_lower or "pct" in title_lower or "%" in title or "ratio" in title_lower:
            aggregation = "DIVIDE"
        else:
            aggregation = "SUM"

    confidence_level = get_confidence_level(score)
    status = "READY" if score >= 0.70 else "NEEDS REVIEW"

    explanation = build_mapping_explanation(title, matched_field or "None", score, match_type, reasons)

    return {
        "visual_id": visual["visual_id"],
        "html_type": html_type,
        "powerbi_type": pbi_visual_type,
        "title": title,
        "mapped_field": matched_field,
        "aggregation": aggregation,
        "score": round(score, 2),
        "confidence_level": confidence_level,
        "match_type": match_type,
        "status": status,
        "explanation": explanation,
        "layout": visual.get("layout", {"x": 20, "y": 20, "width": 300, "height": 200}),
        "source_html": visual.get("source_html", "")
    }

def map_all_visuals(
    visuals: List[Dict[str, Any]],
    dataset_cols: List[Dict[str, Any]],
    ai_suggestions: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Maps all extracted visuals to Power BI visual specs."""
    mapped_list = []
    for v in visuals:
        mapped_list.append(map_visual_to_powerbi(v, dataset_cols, ai_suggestions))
    return mapped_list
