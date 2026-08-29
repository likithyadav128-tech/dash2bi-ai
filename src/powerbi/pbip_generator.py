"""
PBIP (Power BI Project) Root Generator for Dash2BI AI.
Assembles the complete Power BI Project directory structure:
ProjectName/
  ProjectName.pbip
  ProjectName.Report/
    definition.pbir
    definition/
      pages/
        pages.json
        ReportSection1/
          page.json
          visuals/
            visual_1/visual.json
  ProjectName.SemanticModel/
    definition.pbism
    definition/
      model.tmdl
      tables/
        Table.tmdl
"""

import os
import json
import shutil
import tempfile
from typing import Dict, Any, List
from src.powerbi.pbir_generator import generate_definition_pbir, generate_pages_json, generate_page_json
from src.powerbi.report_generator import build_pbir_visual_json
from src.powerbi.tmdl_generator import generate_model_tmdl, generate_table_tmdl
from src.utils.logging import log_event

def create_pbip_project_folder(
    project_name: str,
    table_name: str,
    dataset_cols: List[Dict[str, Any]],
    mapped_visuals: List[Dict[str, Any]],
    measures: List[Dict[str, Any]],
    output_dir: str
) -> str:
    """
    Creates the complete valid Power BI Project (.pbip) folder layout inside output_dir.
    Returns path to the created root project directory.
    """
    safe_name = "".join(c for c in project_name if c.isalnum() or c in ('_', '-')).strip() or "Dash2BI_Project"
    
    root_dir = os.path.join(output_dir, safe_name)
    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)
        
    report_folder_name = f"{safe_name}.Report"
    model_folder_name = f"{safe_name}.SemanticModel"
    
    report_dir = os.path.join(root_dir, report_folder_name)
    model_dir = os.path.join(root_dir, model_folder_name)
    
    # Create directory tree
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)

    # 1. Write Root .pbip File (Strict Power BI Project Schema)
    pbip_content = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/pbip/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": report_folder_name
                }
            }
        ]
    }
    with open(os.path.join(root_dir, f"{safe_name}.pbip"), 'w', encoding='utf-8') as f:
        json.dump(pbip_content, f, indent=2)

    # 2. Write Report Definition (.Report/definition.pbir)
    with open(os.path.join(report_dir, "definition.pbir"), 'w', encoding='utf-8') as f:
        f.write(generate_definition_pbir(model_folder_name))

    # Pages structure
    pages_dir = os.path.join(report_dir, "definition", "pages")
    sec1_dir = os.path.join(pages_dir, "ReportSection1")
    visuals_dir = os.path.join(sec1_dir, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)

    with open(os.path.join(pages_dir, "pages.json"), 'w', encoding='utf-8') as f:
        f.write(generate_pages_json())

    with open(os.path.join(sec1_dir, "page.json"), 'w', encoding='utf-8') as f:
        f.write(generate_page_json("Reconstructed Dashboard"))

    # Write each visual.json
    for v in mapped_visuals:
        v_id = v["visual_id"]
        v_folder = os.path.join(visuals_dir, v_id)
        os.makedirs(v_folder, exist_ok=True)
        v_json = build_pbir_visual_json(v, table_name)
        with open(os.path.join(v_folder, "visual.json"), 'w', encoding='utf-8') as f:
            json.dump(v_json, f, indent=2)

    # 3. Write Semantic Model (.SemanticModel/definition.pbism)
    pbism_content = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definition/pbism/1.0.0/schema.json",
        "version": "1.0",
        "settings": {}
    }
    with open(os.path.join(model_dir, "definition.pbism"), 'w', encoding='utf-8') as f:
        json.dump(pbism_content, f, indent=2)

    model_def_dir = os.path.join(model_dir, "definition")
    tables_dir = os.path.join(model_def_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)

    with open(os.path.join(model_def_dir, "model.tmdl"), 'w', encoding='utf-8') as f:
        f.write(generate_model_tmdl(safe_name + "_Model", table_name))

    # Build TMDL columns & measures
    tmdl_cols = []
    for c in dataset_cols:
        tmdl_cols.append({
            "name": c["original_name"],
            "dataType": c["data_type"],
            "summarizeBy": "sum" if c["role"] == "Measure" else "none"
        })

    tmdl_measures = []
    for m in measures:
        tmdl_measures.append({
            "name": m["measure_name"],
            "expression": m["dax_formula"],
            "formatString": "$#,##0.00" if "Sales" in m["measure_name"] or "Profit" in m["measure_name"] else ("0.0%" if "Margin" in m["measure_name"] else "#,##0")
        })

    with open(os.path.join(tables_dir, f"{table_name}.tmdl"), 'w', encoding='utf-8') as f:
        f.write(generate_table_tmdl(table_name, tmdl_cols, tmdl_measures))

    log_event("powerbi", f"Successfully assembled PBIP project structure at '{root_dir}'")
    return root_dir
