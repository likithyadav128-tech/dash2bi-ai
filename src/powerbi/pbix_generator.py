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
from src.powerbi.pbip_generator import generate_classic_report_layout

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
