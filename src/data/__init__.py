"""
Data package initialization.
"""
from src.data.dataset_loader import load_dataset_file, inspect_excel_sheets
from src.data.dataset_profiler import profile_dataset, DatasetProfile, normalize_column_name
from src.data.schema_detector import (
    detect_column_role,
    map_pandas_dtype_to_powerbi,
    ROLE_MEASURE,
    ROLE_DIMENSION,
    ROLE_DATE,
    ROLE_IDENTIFIER,
    ROLE_CATEGORICAL,
)
from src.data.auto_visual_generator import auto_generate_visuals

__all__ = [
    "load_dataset_file",
    "inspect_excel_sheets",
    "profile_dataset",
    "DatasetProfile",
    "normalize_column_name",
    "detect_column_role",
    "map_pandas_dtype_to_powerbi",
    "ROLE_MEASURE",
    "ROLE_DIMENSION",
    "ROLE_DATE",
    "ROLE_IDENTIFIER",
    "ROLE_CATEGORICAL",
    "auto_generate_visuals",
]
