"""
Export Manager module for Dash2BI AI.
Zips PBIP project folder and generates downloadable reports.
"""

import os
import shutil
import json
import zipfile
import tempfile
from typing import Dict, Any, List, Tuple
from src.powerbi.pbip_generator import create_pbip_project_folder
from src.utils.logging import log_event

def package_pbip_as_zip(project_dir: str) -> bytes:
    """
    Compresses PBIP project directory into a ZIP archive bytes buffer.
    """
    temp_zip_path = tempfile.mktemp(suffix=".zip")
    archive_name = shutil.make_archive(temp_zip_path.replace('.zip', ''), 'zip', project_dir)
    
    with open(archive_name, 'rb') as f:
        zip_bytes = f.read()

    try:
        os.remove(archive_name)
    except Exception:
        pass

    return zip_bytes

def generate_analysis_report_markdown(
    dataset_profile_dict: Dict[str, Any],
    html_visuals: List[Dict[str, Any]],
    mapped_visuals: List[Dict[str, Any]],
    reconstruction_score: Dict[str, Any]
) -> str:
    """Generates a comprehensive markdown Dashboard Analysis Report."""
    md = f"""# Dash2BI AI — Dashboard Reconstruction & Analysis Report

## 1. Executive Summary
- **Overall Estimated Reconstruction Score:** {reconstruction_score.get('overall_score', 0)} / 100
- **Detected Visual Components:** {len(html_visuals)}
- **Mapped Power BI Visuals:** {len(mapped_visuals)}

## 2. Dataset Profile
- **Table Name:** {dataset_profile_dict.get('table_name')}
- **Row Count:** {dataset_profile_dict.get('row_count'):,}
- **Column Count:** {dataset_profile_dict.get('col_count')}
- **Measures Identified:** {len(dataset_profile_dict.get('measures', []))}
- **Dimensions Identified:** {len(dataset_profile_dict.get('dimensions', []))}

## 3. Visual Mapping Summary
| HTML Element | Detected Type | Mapped Dataset Field | Power BI Visual | Confidence | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for v in mapped_visuals:
        md += f"| {v['title']} | {v['html_type']} | {v.get('mapped_field', 'None')} | {v['powerbi_type']} | {v['score']*100:.0f}% | {v['status']} |\n"

    md += """
## 4. Power BI Desktop Workflow Instructions
1. Download the generated **Power BI Project (.pbip)** ZIP archive.
2. Extract the contents to a folder on your computer.
3. Open the folder and double-click the **.pbip** file to launch **Power BI Desktop**.
4. In Power BI Desktop, click **File → Save As** and select **Power BI Report (*.pbix)** to save as a standalone `.pbix` file.
"""
    return md
