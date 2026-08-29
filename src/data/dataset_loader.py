"""
Dataset loader module for Dash2BI AI.
Supports loading CSV and Excel (.xlsx, .xls) files with encoding/delimiter detection.
"""

import io
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from src.utils.errors import DatasetValidationError
from src.utils.logging import log_event

def inspect_excel_sheets(file_bytes: bytes) -> List[str]:
    """Inspects an Excel file and returns all sheet names."""
    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        return excel_file.sheet_names
    except Exception as e:
        raise DatasetValidationError(
            message=f"Failed to inspect Excel sheets: {str(e)}",
            details="The file may be corrupted, password protected, or not a valid Excel document.",
            solution="Ensure the file opens correctly in Excel and re-upload."
        )

def load_dataset_file(file_name: str, file_bytes: bytes, selected_sheet: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads dataset file into a pandas DataFrame and returns metadata.
    """
    ext = file_name.lower().split('.')[-1]
    
    if ext in ['xlsx', 'xls']:
        try:
            excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
            sheets = excel_file.sheet_names
            sheet_to_load = selected_sheet if selected_sheet in sheets else sheets[0]
            df = pd.read_excel(excel_file, sheet_name=sheet_to_load)
            
            meta = {
                "file_type": "Excel",
                "sheets": sheets,
                "selected_sheet": sheet_to_load,
                "file_name": file_name,
            }
            log_event("data", f"Loaded Excel file '{file_name}' sheet '{sheet_to_load}' with shape {df.shape}")
            return df, meta
        except DatasetValidationError:
            raise
        except Exception as e:
            raise DatasetValidationError(
                message=f"Could not load Excel file '{file_name}': {str(e)}",
                details="Excel parser encountered an unreadable binary structure.",
                solution="Save the Excel file as standard .xlsx and try again."
            )
            
    elif ext == 'csv':
        try:
            # Try utf-8 first, fallback to latin-1
            try:
                content = file_bytes.decode('utf-8')
                encoding_used = 'utf-8'
            except UnicodeDecodeError:
                content = file_bytes.decode('latin-1')
                encoding_used = 'latin-1'
            
            # Sniff delimiter
            first_line = content.splitlines()[0] if content.splitlines() else ""
            if '\t' in first_line:
                delimiter = '\t'
            elif ';' in first_line:
                delimiter = ';'
            elif '|' in first_line:
                delimiter = '|'
            else:
                delimiter = ','

            df = pd.read_csv(io.StringIO(content), sep=delimiter)
            meta = {
                "file_type": "CSV",
                "encoding": encoding_used,
                "delimiter": delimiter,
                "file_name": file_name,
                "sheets": [file_name]
            }
            log_event("data", f"Loaded CSV file '{file_name}' ({encoding_used}, sep='{delimiter}') shape {df.shape}")
            return df, meta
        except Exception as e:
            raise DatasetValidationError(
                message=f"Could not parse CSV file '{file_name}': {str(e)}",
                details="CSV structure contains invalid delimiters or corrupted lines.",
                solution="Verify CSV delimiter and export clean CSV data."
            )
    else:
        raise DatasetValidationError(
            message=f"Unsupported file format '{ext}'.",
            solution="Upload a .csv, .xlsx, or .xls dataset."
        )
