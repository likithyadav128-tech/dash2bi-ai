"""
Dataset Profiler module for Dash2BI AI.
Performs local dataset schema detection, statistical analysis, and data quality summary.
"""

import re
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from src.data.dataset_loader import load_dataset_file
from src.data.schema_detector import detect_column_role, map_pandas_dtype_to_powerbi, ROLE_MEASURE, ROLE_DIMENSION, ROLE_DATE, ROLE_IDENTIFIER, ROLE_CATEGORICAL
from src.data.statistics import compute_column_statistics
from src.utils.logging import log_event

def normalize_column_name(name: str) -> str:
    """Normalizes column names for Power BI compliance."""
    clean = str(name).strip()
    clean = re.sub(r'[\s_\-]+', ' ', clean)
    return clean.title()

class DatasetProfile:
    """Encapsulates dataset metadata, schema, and data quality summary."""
    def __init__(self, table_name: str, df: pd.DataFrame, file_meta: Dict[str, Any]):
        self.table_name = table_name
        self.df = df
        self.file_meta = file_meta
        self.row_count = len(df)
        self.col_count = len(df.columns)
        self.columns_info: List[Dict[str, Any]] = []
        self.quality_summary: Dict[str, Any] = {}
        self.measures: List[str] = []
        self.dimensions: List[str] = []
        self.date_fields: List[str] = []
        self.identifiers: List[str] = []
        
        self._profile()

    def _profile(self):
        total_cells = self.row_count * self.col_count if self.row_count > 0 else 1
        total_nulls = 0
        duplicate_rows = int(self.df.duplicated().sum())
        duplicate_cols = int(self.df.columns.duplicated().sum())

        for col in self.df.columns:
            series = self.df[col]
            original_name = str(col)
            norm_name = normalize_column_name(original_name)
            pbi_dtype = map_pandas_dtype_to_powerbi(series)
            role = detect_column_role(original_name, series)
            stats = compute_column_statistics(series)

            total_nulls += stats["null_count"]

            col_info = {
                "original_name": original_name,
                "normalized_name": norm_name,
                "data_type": pbi_dtype,
                "pandas_dtype": str(series.dtype),
                "role": role,
                "stats": stats
            }
            self.columns_info.append(col_info)

            if role == ROLE_MEASURE:
                self.measures.append(original_name)
            elif role == ROLE_DATE:
                self.date_fields.append(original_name)
            elif role == ROLE_IDENTIFIER:
                self.identifiers.append(original_name)
            else:
                self.dimensions.append(original_name)

        null_pct = round((total_nulls / total_cells) * 100, 2)
        
        # Check warnings
        warnings = []
        if duplicate_rows > 0:
            warnings.append(f"Detected {duplicate_rows} duplicate rows in dataset.")
        if duplicate_cols > 0:
            warnings.append(f"Detected {duplicate_cols} duplicate column names.")
        if null_pct > 5.0:
            warnings.append(f"Missing values account for {null_pct}% of total cells.")

        self.quality_summary = {
            "rows": self.row_count,
            "columns": self.col_count,
            "missing_values_percentage": null_pct,
            "duplicate_rows": duplicate_rows,
            "duplicate_columns": duplicate_cols,
            "measure_count": len(self.measures),
            "dimension_count": len(self.dimensions) + len(self.identifiers),
            "date_count": len(self.date_fields),
            "warnings": warnings
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_name": self.table_name,
            "row_count": self.row_count,
            "col_count": self.col_count,
            "file_meta": self.file_meta,
            "columns": self.columns_info,
            "quality_summary": self.quality_summary,
            "measures": self.measures,
            "dimensions": self.dimensions,
            "date_fields": self.date_fields,
            "identifiers": self.identifiers
        }

def profile_dataset(file_name: str, file_bytes: bytes, selected_sheet: Optional[str] = None) -> DatasetProfile:
    """Loads and profiles a dataset file into a DatasetProfile instance."""
    df, meta = load_dataset_file(file_name, file_bytes, selected_sheet)
    table_name = "Dataset"
    if meta.get("selected_sheet"):
        table_name = meta["selected_sheet"].replace(" ", "_")
    return DatasetProfile(table_name=table_name, df=df, file_meta=meta)
