"""
Confidence Scoring System for Dash2BI AI Mappings.
Provides numeric scores (0.0 to 1.0), categorical confidence levels (HIGH, MEDIUM, LOW),
and transparent human-readable explanations.
"""

from typing import Dict, Any, Tuple

CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_LOW = "LOW"

def get_confidence_level(score: float) -> str:
    """Categorizes a numeric confidence score."""
    if score >= 0.85:
        return CONFIDENCE_HIGH
    elif score >= 0.60:
        return CONFIDENCE_MEDIUM
    else:
        return CONFIDENCE_LOW

def build_mapping_explanation(
    visual_title: str,
    matched_field: str,
    score: float,
    match_type: str,
    reasons: list
) -> str:
    """Builds a human-readable explanation of why a mapping was selected."""
    level = get_confidence_level(score)
    explanation = f"**'{visual_title}'** was mapped to **'{matched_field}'** (Confidence: {level}, {score*100:.0f}%):\n"
    for r in reasons:
        explanation += f"- {r}\n"
    return explanation
