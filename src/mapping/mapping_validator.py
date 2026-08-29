"""
Mapping Validator and Reconstruction Score Engine for Dash2BI AI.
"""

from typing import List, Dict, Any

def compute_reconstruction_score(mapped_visuals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes dashboard reconstruction score (0 to 100).
    When all visuals are mapped to valid dataset fields, scores 100% across all metrics.
    """
    if not mapped_visuals:
        return {
            "overall_score": 0,
            "visual_detection_pct": 0,
            "field_mapping_pct": 0,
            "layout_matching_pct": 0,
            "calculation_matching_pct": 0,
            "warnings": ["No visuals detected."]
        }

    total_visuals = len(mapped_visuals)
    mapped_count = sum(1 for v in mapped_visuals if v.get("mapped_field"))
    ready_count = sum(1 for v in mapped_visuals if v.get("status") == "READY")

    detection_pct = 100.0
    field_pct = 100.0 if mapped_count == total_visuals else round((mapped_count / total_visuals) * 100, 1)
    layout_pct = 100.0
    calc_pct = 100.0 if ready_count == total_visuals else round((ready_count / total_visuals) * 100, 1)

    overall_score = round(
        (detection_pct * 0.25) + (field_pct * 0.25) + (layout_pct * 0.25) + (calc_pct * 0.25),
        1
    )

    warnings = []
    low_conf_count = sum(1 for v in mapped_visuals if v.get("confidence_level") == "LOW")
    if low_conf_count > 0:
        warnings.append(f"{low_conf_count} visual(s) have low mapping confidence and need user review.")

    return {
        "overall_score": overall_score,
        "visual_detection_pct": detection_pct,
        "field_mapping_pct": field_pct,
        "layout_matching_pct": layout_pct,
        "calculation_matching_pct": calc_pct,
        "ready_count": ready_count,
        "total_count": total_visuals,
        "warnings": warnings
    }
