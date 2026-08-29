"""
Prompt builder for LLM-assisted semantic mapping in Dash2BI AI.
"""

import json
from typing import Dict, Any, List

def build_mapping_prompt(dataset_schema: Dict[str, Any], visuals: List[Dict[str, Any]]) -> str:
    """
    Builds a structured prompt asking the AI to map HTML visual elements to dataset schema fields.
    Does NOT include full dataset rows to protect data privacy.
    """
    column_summary = []
    for col in dataset_schema.get("columns", []):
        column_summary.append({
            "name": col["original_name"],
            "data_type": col["data_type"],
            "role": col["role"],
            "examples": col["stats"].get("examples", [])[:3]
        })

    visual_summary = []
    for v in visuals:
        visual_summary.append({
            "visual_id": v["visual_id"],
            "visual_type": v["visual_type"],
            "title": v.get("title", ""),
            "raw_value": v.get("raw_value", "")
        })

    prompt = f"""
You are an expert BI Data Architect assisting in converting an HTML Dashboard design into Power BI report definitions.

Here is the Dataset Metadata (Schema only, no personal data):
{json.dumps(column_summary, indent=2)}

Here are the Detected HTML Dashboard Components:
{json.dumps(visual_summary, indent=2)}

For each visual component, analyze its title, type, and value, and determine:
1. The most appropriate dataset field name to map to.
2. The recommended aggregation (SUM, AVERAGE, COUNT, DISTINCTCOUNT, DIVIDE, or None).
3. Suggested DAX measure formula if applicable.
4. Confidence score between 0.0 and 1.0.

Respond strictly in valid JSON format with the structure:
{{
  "mappings": [
    {{
      "visual_id": "kpi_1",
      "dataset_field": "Sales",
      "aggregation": "SUM",
      "dax_formula": "Total Sales = SUM('Dataset'[Sales])",
      "confidence": 0.95,
      "reason": "Matching title 'Total Sales' with numeric column 'Sales'"
    }}
  ]
}}
"""
    return prompt.strip()
