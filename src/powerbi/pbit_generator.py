"""
PBIT (Power BI Template) Generator for Dash2BI AI.
Generates single-file Power BI Report Templates (.pbit) containing DataModelSchema and Report Layout JSON.
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
    columns = []
    for col in dataset_cols:
        columns.append({
            "name": col["original_name"],
            "dataType": col["data_type"],
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
        "name": "Dash2BI_Model",
        "compatibilityLevel": 1550,
        "model": {
            "culture": "en-US",
            "tables": [
                {
                    "name": table_name,
                    "columns": columns,
                    "measures": model_measures,
                    "partitions": [
                        {
                            "name": table_name,
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
    Creates a single valid Power BI Template (.pbit) binary ZIP archive.
    """
    schema_json = build_data_model_schema_json(table_name, dataset_cols, measures)
    
    # Layout JSON
    layout_json = {
        "id": 0,
        "resourcePackage": { "items": [] },
        "sections": [
            {
                "name": "ReportSection1",
                "displayName": "Reconstructed Dashboard",
                "width": 1280,
                "height": 720,
                "visualContainers": []
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
