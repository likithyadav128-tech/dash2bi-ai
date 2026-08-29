"""
Report Generator module for Dash2BI AI.
Generates Power BI PBIR Visual JSON objects with exact layout positioning.
"""

import json
from typing import Dict, Any, List

def build_pbir_visual_json(visual_spec: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    """
    Generates PBIR visual.json format.
    """
    v_id = visual_spec["visual_id"]
    pbi_type = visual_spec.get("powerbi_type", "tableEx")
    layout = visual_spec.get("layout", {"x": 20, "y": 20, "width": 300, "height": 200})
    title = visual_spec.get("title", "")
    field = visual_spec.get("mapped_field", "")

    visual_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
        "name": v_id,
        "position": {
            "x": layout.get("x", 20),
            "y": layout.get("y", 20),
            "width": layout.get("width", 300),
            "height": layout.get("height", 200),
            "z": 100
        },
        "visual": {
            "visualType": pbi_type,
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": { "SourceRef": { "Entity": table_name } },
                                        "Property": field or "Sales"
                                    }
                                },
                                "queryRef": f"{table_name}.{field or 'Sales'}"
                            }
                        ]
                    }
                }
            },
            "visualCustomizations": {
                "title": title
            }
        }
    }
    return visual_json
