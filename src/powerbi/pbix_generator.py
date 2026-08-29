"""
PBIX (Power BI Report) Generator for Dash2BI AI.
Generates single-file Power BI Report files (.pbix) containing DataModelSchema, Report/Layout, Version, and Content_Types.xml.
"""

import os
import json
import zipfile
import tempfile
import base64
from typing import Dict, Any, List, Optional
from src.powerbi.pbit_generator import build_data_model_schema_json

def generate_classic_report_layout(
    table_name: str,
    mapped_visuals: List[Dict[str, Any]],
    dataset_cols: List[Dict[str, Any]],
    measures: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates standard Power BI Report Layout JSON containing all visual containers and page structure."""
    safe_table = table_name.replace(" ", "_")
    visual_containers = []
    
    for idx, v in enumerate(mapped_visuals):
        v_id = v["visual_id"]
        pbi_type = v.get("powerbi_type", "card")
        layout = v.get("layout", {"x": 20, "y": 20, "width": 300, "height": 110})
        title = v.get("title", "")
        mapped_field = v.get("mapped_field", "")
        measure_name = v.get("measure_name", title)
        
        prop_name = measure_name if measure_name else (mapped_field or "Confirmed")
        dim_prop = mapped_field or "State"
        val_prop = measure_name or "TOTAL CONFIRMED"

        if pbi_type == "card":
            single_visual = {
                "visualType": "card",
                "projections": {
                    "Values": [
                        {
                            "queryRef": f"{safe_table}.{prop_name}"
                        }
                    ]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [
                        {
                            "Name": "t",
                            "Entity": safe_table,
                            "Type": 0
                        }
                    ],
                    "Select": [
                        {
                            "Measure": {
                                "Expression": {
                                    "SourceRef": {
                                        "Source": "t"
                                    }
                                },
                                "Property": prop_name
                            },
                            "Name": f"{safe_table}.{prop_name}"
                        }
                    ]
                }
            }
        elif pbi_type in ["barChart", "columnChart", "lineChart", "areaChart", "pieChart", "donutChart"]:
            single_visual = {
                "visualType": pbi_type,
                "projections": {
                    "Category": [
                        {
                            "queryRef": f"{safe_table}.{dim_prop}"
                        }
                    ],
                    "Y": [
                        {
                            "queryRef": f"{safe_table}.{val_prop}"
                        }
                    ]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [
                        {
                            "Name": "t",
                            "Entity": safe_table,
                            "Type": 0
                        }
                    ],
                    "Select": [
                        {
                            "Column": {
                                "Expression": {
                                    "SourceRef": {
                                        "Source": "t"
                                    }
                                },
                                "Property": dim_prop
                            },
                            "Name": f"{safe_table}.{dim_prop}"
                        },
                        {
                            "Measure": {
                                "Expression": {
                                    "SourceRef": {
                                        "Source": "t"
                                    }
                                },
                                "Property": val_prop
                            },
                            "Name": f"{safe_table}.{val_prop}"
                        }
                    ]
                }
            }
        else:  # slicer, tableEx
            single_visual = {
                "visualType": pbi_type,
                "projections": {
                    "Values": [
                        {
                            "queryRef": f"{safe_table}.{dim_prop}"
                        }
                    ]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [
                        {
                            "Name": "t",
                            "Entity": safe_table,
                            "Type": 0
                        }
                    ],
                    "Select": [
                        {
                            "Column": {
                                "Expression": {
                                    "SourceRef": {
                                        "Source": "t"
                                    }
                                },
                                "Property": dim_prop
                            },
                            "Name": f"{safe_table}.{dim_prop}"
                        }
                    ]
                }
            }

        config_obj = {
            "name": v_id,
            "layouts": [
                {
                    "id": 0,
                    "position": {
                        "x": layout.get("x", 20),
                        "y": layout.get("y", 20),
                        "z": 1000 + idx,
                        "width": layout.get("width", 300),
                        "height": layout.get("height", 110)
                    }
                }
            ],
            "singleVisual": single_visual
        }

        visual_containers.append({
            "x": layout.get("x", 20),
            "y": layout.get("y", 20),
            "z": 1000 + idx,
            "width": layout.get("width", 300),
            "height": layout.get("height", 110),
            "config": json.dumps(config_obj)
        })

    return {
        "id": 0,
        "resourcePackage": { "items": [] },
        "sections": [
            {
                "name": "ReportSection1",
                "displayName": "Reconstructed Dashboard",
                "filters": "[]",
                "ordinal": 0,
                "width": 1280,
                "height": 720,
                "visualContainers": visual_containers
            }
        ]
    }

def create_pbix_file(
    project_name: str,
    table_name: str,
    dataset_cols: List[Dict[str, Any]],
    mapped_visuals: List[Dict[str, Any]],
    measures: List[Dict[str, Any]],
    raw_dataset_bytes: Optional[bytes] = None
) -> bytes:
    """
    Creates a single valid Power BI Report (.pbix) binary ZIP archive.
    """
    schema_json = build_data_model_schema_json(table_name, dataset_cols, measures, raw_dataset_bytes)
    layout_json = generate_classic_report_layout(table_name, mapped_visuals, dataset_cols, measures)

    content_types_xml = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="xml" ContentType="application/xml" />
</Types>"""

    version_str = "1.24"

    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".pbix")
    temp_zip.close()

    with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("DataModelSchema", json.dumps(schema_json, indent=2).encode('utf-16le'))
        zf.writestr("Report/Layout", json.dumps(layout_json, indent=2).encode('utf-8'))
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("Version", version_str)

    with open(temp_zip.name, 'rb') as f:
        pbix_bytes = f.read()

    try:
        os.remove(temp_zip.name)
    except Exception:
        pass

    return pbix_bytes
