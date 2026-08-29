"""
Power BI package initialization.
"""
from src.powerbi.model_generator import build_semantic_model_spec
from src.powerbi.tmdl_generator import generate_model_tmdl, generate_table_tmdl
from src.powerbi.report_generator import build_pbir_visual_json
from src.powerbi.pbir_generator import generate_definition_pbir, generate_pages_json, generate_page_json
from src.powerbi.pbip_generator import create_pbip_project_folder
from src.powerbi.pbit_generator import create_pbit_file
from src.powerbi.pbix_generator import create_pbix_file
from src.powerbi.validation import validate_project_before_export
from src.powerbi.export_manager import package_pbip_as_zip, generate_analysis_report_markdown

__all__ = [
    "build_semantic_model_spec",
    "generate_model_tmdl",
    "generate_table_tmdl",
    "build_pbir_visual_json",
    "generate_definition_pbir",
    "generate_pages_json",
    "generate_page_json",
    "create_pbip_project_folder",
    "create_pbit_file",
    "create_pbix_file",
    "validate_project_before_export",
    "package_pbip_as_zip",
    "generate_analysis_report_markdown",
]
