"""
PBIR (Report Definition) Generator for Dash2BI AI.
Builds definition.pbir, pages.json, page.json, and visual definitions.
"""

import json
from typing import Dict, Any, List
from src.powerbi.report_generator import build_pbir_visual_json

def generate_definition_pbir(semantic_model_folder_name: str) -> str:
    """Generates content for definition.pbir."""
    data = {
        "version": "4.0",
        "datasetReference": {
            "byPath": {
                "path": f"../{semantic_model_folder_name}"
            }
        }
    }
    return json.dumps(data, indent=2)

def generate_pages_json() -> str:
    """Generates content for pages.json."""
    data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pages/1.0.0/schema.json",
        "pageOrder": ["ReportSection1"],
        "activePageName": "ReportSection1"
    }
    return json.dumps(data, indent=2)

def generate_page_json(page_name: str = "Dashboard Reconstructed") -> str:
    """Generates content for page.json."""
    data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.0.0/schema.json",
        "name": "ReportSection1",
        "displayName": page_name,
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280
    }
    return json.dumps(data, indent=2)
