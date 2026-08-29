"""
PBIP (Power BI Project) Root Generator for Dash2BI AI.
Assembles complete standard Power BI Project directory structure:
ProjectName/
  ProjectName.pbip
  dataset.csv
  ProjectName.Report/
    definition.pbir
    Layout
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
from src.powerbi.pbir_generator import generate_definition_pbir
from src.powerbi.model_bim_generator import generate_model_bim_json
from src.powerbi.tmdl_generator import generate_model_tmdl, generate_table_tmdl
from src.utils.logging import log_event

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
    Creates the complete valid standard Power BI Project (.pbip) folder layout inside output_dir.
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

    # 1. Write Root .pbip File
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

    # 2. Write Report Definition (.Report/definition.pbir & .Report/Layout in UTF-8)
    with open(os.path.join(report_dir, "definition.pbir"), 'w', encoding='utf-8') as f:
        f.write(generate_definition_pbir(model_folder_name))

    classic_layout_dict = generate_classic_report_layout(table_name, mapped_visuals, dataset_cols, measures)
    with open(os.path.join(report_dir, "Layout"), 'w', encoding='utf-8') as f:
        json.dump(classic_layout_dict, f, indent=2)

    # 3. Write Semantic Model (.SemanticModel/definition.pbism, model.bim, & TMDL)
    pbism_content = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "1.0",
        "settings": {}
    }
    with open(os.path.join(model_dir, "definition.pbism"), 'w', encoding='utf-8') as f:
        json.dump(pbism_content, f, indent=2)

    model_bim_dict = generate_model_bim_json(table_name, dataset_cols, measures, csv_content)
    with open(os.path.join(model_dir, "model.bim"), 'w', encoding='utf-8') as f:
        json.dump(model_bim_dict, f, indent=2)

    # TMDL definitions
    model_def_dir = os.path.join(model_dir, "definition")
    tables_dir = os.path.join(model_def_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)

    with open(os.path.join(model_def_dir, "dataset.csv"), 'wb') as f:
        f.write(csv_content)

    with open(os.path.join(model_def_dir, "model.tmdl"), 'w', encoding='utf-8') as f:
        f.write(generate_model_tmdl(safe_name + "_Model", table_name))

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
        f.write(generate_table_tmdl(table_name, tmdl_cols, tmdl_measures, csv_content))

    log_event("powerbi", f"Successfully assembled standard PBIP project structure at '{root_dir}'")
    return root_dir
