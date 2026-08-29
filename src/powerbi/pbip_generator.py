"""
PBIP (Power BI Project) Root Generator for Dash2BI AI.
Assembles the complete Power BI Project directory structure:
ProjectName/
  ProjectName.pbip
  dataset.csv
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
    model.bim
    definition/
      model.tmdl
      tables/
        Table.tmdl
"""

import os
import json
import shutil
import tempfile
from typing import Dict, Any, List, Optional
from src.powerbi.pbir_generator import generate_definition_pbir, generate_pages_json, generate_page_json
from src.powerbi.report_generator import build_pbir_visual_json
from src.powerbi.tmdl_generator import generate_model_tmdl, generate_table_tmdl
from src.powerbi.model_bim_generator import generate_model_bim_json
from src.utils.logging import log_event

def create_pbip_project_folder(
    project_name: str,
    table_name: str,
    dataset_cols: List[Dict[str, Any]],
    mapped_visuals: List[Dict[str, Any]],
    measures: List[Dict[str, Any]],
    output_dir: str,
    raw_dataset_bytes: Optional[bytes] = None
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

    # Write dataset.csv if provided
    csv_header = ",".join(c["original_name"] for c in dataset_cols) + "\n"
    csv_content = raw_dataset_bytes if raw_dataset_bytes else csv_header.encode('utf-8')
    with open(os.path.join(root_dir, "dataset.csv"), 'wb') as f:
        f.write(csv_content)

    # 1. Write Root .pbip File (Strict Power BI Desktop Schema Regex Match)
    pbip_content = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
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

    # 3. Write Semantic Model (.SemanticModel/definition.pbism & model.bim)
    pbism_content = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "1.0",
        "settings": {}
    }
    with open(os.path.join(model_dir, "definition.pbism"), 'w', encoding='utf-8') as f:
        json.dump(pbism_content, f, indent=2)

    # Write model.bim required by Power BI Desktop
    model_bim_dict = generate_model_bim_json(table_name, dataset_cols, measures)
    with open(os.path.join(model_dir, "model.bim"), 'w', encoding='utf-8') as f:
        json.dump(model_bim_dict, f, indent=2)

    model_def_dir = os.path.join(model_dir, "definition")
    tables_dir = os.path.join(model_def_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)

    # Also place dataset.csv inside model definition
    with open(os.path.join(model_def_dir, "dataset.csv"), 'wb') as f:
        f.write(csv_content)

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

    safe_table = table_name.replace(" ", "_")
    with open(os.path.join(tables_dir, f"{safe_table}.tmdl"), 'w', encoding='utf-8') as f:
        f.write(generate_table_tmdl(table_name, tmdl_cols, tmdl_measures))

    log_event("powerbi", f"Successfully assembled PBIP project structure at '{root_dir}'")
    return root_dir
