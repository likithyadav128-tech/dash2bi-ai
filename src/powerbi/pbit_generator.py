"""
PBIT (Power BI Template) Generator for Dash2BI AI.
Generates single-file Power BI Report Templates (.pbit) containing DataModelSchema and Report Layout JSON with visual containers.
"""

import os
import json
import zipfile
import tempfile
from typing import Dict, Any, List

def build_data_model_schema_json(
    table_name: str,
    dataset_cols: List[Dict[str, Any]],
    measures: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates DataModelSchema JSON for .pbit file."""
    safe_table = table_name.replace(" ", "_")
    columns = []
    for col in dataset_cols:
        columns.append({
            "name": col["original_name"],
            "dataType": col.get("data_type", "string"),
            "sourceColumn": col["original_name"]
        })

    model_measures = []
    for m in measures:
        model_measures.append({
            "name": m["measure_name"],
            "expression": m["dax_formula"],
            "formatString": "$#,##0.00" if "Sales" in m["measure_name"] or "Profit" in m["measure_name"] else ("0.0%" if "Margin" in m["measure_name"] else "#,##0")
        })

    return {
        "name": f"{safe_table}_Model",
        "compatibilityLevel": 1550,
        "model": {
            "culture": "en-US",
            "tables": [
                {
                    "name": safe_table,
                    "columns": columns,
                    "measures": model_measures,
                    "partitions": [
                        {
                            "name": safe_table,
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": f'let Source = Csv.Document(File.Contents("dataset.csv"), [Delimiter=",", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.None]), #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]) in #"Promoted Headers"'
                            }
                        }
                    ]
                }
            ]
        }
    }

def create_pbit_file(
    project_name: str,
    table_name: str,
    dataset_cols: List[Dict[str, Any]],
    mapped_visuals: List[Dict[str, Any]],
    measures: List[Dict[str, Any]]
) -> bytes:
    """
    Creates a single valid Power BI Template (.pbit) binary ZIP archive with visual containers.
    """
    safe_table = table_name.replace(" ", "_")
    schema_json = build_data_model_schema_json(table_name, dataset_cols, measures)
    
    visual_containers = []
    for idx, v in enumerate(mapped_visuals):
        v_id = v["visual_id"]
        pbi_type = v.get("powerbi_type", "card")
        layout = v.get("layout", {"x": 20, "y": 20, "width": 300, "height": 110})
        title = v.get("title", "")
        mapped_field = v.get("mapped_field", "")
        measure_name = v.get("measure_name", title)

        prop_name = measure_name if measure_name else (mapped_field or "Confirmed")

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
            "singleVisual": {
                "visualType": pbi_type,
                "projections": {
                    "Fields" if pbi_type == "card" else ("Values" if pbi_type in ["slicer", "tableEx"] else "Y"): [
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
        }

        visual_containers.append({
            "x": layout.get("x", 20),
            "y": layout.get("y", 20),
            "z": 1000 + idx,
            "width": layout.get("width", 300),
            "height": layout.get("height", 110),
            "config": json.dumps(config_obj)
        })

    layout_json = {
        "id": 0,
        "resourcePackage": { "items": [] },
        "sections": [
            {
                "name": "ReportSection1",
                "displayName": "Reconstructed Dashboard",
                "width": 1280,
                "height": 720,
                "visualContainers": visual_containers
            }
        ]
    }

    content_types_xml = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="xml" ContentType="application/xml" />
</Types>"""

    version_str = "1.24"

    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".pbit")
    temp_zip.close()

    with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("DataModelSchema", json.dumps(schema_json, indent=2).encode('utf-16le'))
        zf.writestr("Report/Layout", json.dumps(layout_json, indent=2).encode('utf-16le'))
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("Version", version_str)

    with open(temp_zip.name, 'rb') as f:
        pbit_bytes = f.read()

    try:
        os.remove(temp_zip.name)
    except Exception:
        pass

    return pbit_bytes
