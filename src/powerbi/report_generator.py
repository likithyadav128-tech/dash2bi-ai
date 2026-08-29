"""
Report Generator module for Dash2BI AI.
Generates Power BI PBIR Visual JSON objects with exact query projections and canvas positioning.
"""

import json
from typing import Dict, Any, List

def build_pbir_visual_json(visual_spec: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    """
    Generates PBIR visual.json format with valid projections for Card, Chart, Table, and Slicer visuals.
    """
    safe_table = table_name.replace(" ", "_")
    v_id = visual_spec["visual_id"]
    pbi_type = visual_spec.get("powerbi_type", "tableEx")
    layout = visual_spec.get("layout", {"x": 20, "y": 20, "width": 300, "height": 200})
    title = visual_spec.get("title", "")
    mapped_field = visual_spec.get("mapped_field", "")
    measure_name = visual_spec.get("measure_name", title)

    query_state: Dict[str, Any] = {}

    if pbi_type == "card":
        # Card Visual Projection bound to Measure
        prop_name = measure_name if measure_name else (mapped_field or "Confirmed")
        query_state = {
            "Fields": {
                "projections": [
                    {
                        "field": {
                            "Measure": {
                                "Expression": { "SourceRef": { "Entity": safe_table } },
                                "Property": prop_name
                            }
                        },
                        "queryRef": f"{safe_table}.{prop_name}"
                    }
                ]
            }
        }
    elif pbi_type in ["barChart", "columnChart", "lineChart", "areaChart", "pieChart", "donutChart"]:
        # Chart Visual Projections (Category + Y Measure/Value)
        cat_prop = mapped_field or "State"
        val_prop = measure_name or "TOTAL CONFIRMED"
        
        query_state = {
            "Category": {
                "projections": [
                    {
                        "field": {
                            "Column": {
                                "Expression": { "SourceRef": { "Entity": safe_table } },
                                "Property": cat_prop
                            }
                        },
                        "queryRef": f"{safe_table}.{cat_prop}"
                    }
                ]
            },
            "Y": {
                "projections": [
                    {
                        "field": {
                            "Measure": {
                                "Expression": { "SourceRef": { "Entity": safe_table } },
                                "Property": val_prop
                            }
                        },
                        "queryRef": f"{safe_table}.{val_prop}"
                    }
                ]
            }
        }
    elif pbi_type == "slicer":
        # Slicer Visual Projection
        prop_name = mapped_field or "State"
        query_state = {
            "Values": {
                "projections": [
                    {
                        "field": {
                            "Column": {
                                "Expression": { "SourceRef": { "Entity": safe_table } },
                                "Property": prop_name
                            }
                        },
                        "queryRef": f"{safe_table}.{prop_name}"
                    }
                ]
            }
        }
    else:
        # Default TableEx Projection
        prop_name = mapped_field or "State"
        query_state = {
            "Values": {
                "projections": [
                    {
                        "field": {
                            "Column": {
                                "Expression": { "SourceRef": { "Entity": safe_table } },
                                "Property": prop_name
                            }
                        },
                        "queryRef": f"{safe_table}.{prop_name}"
                    }
                ]
            }
        }

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
                "queryState": query_state
            }
        }
    }
    return visual_json
