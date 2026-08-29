"""
Schema and semantic role detector for dataset columns in Dash2BI AI.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, Any, List

# Semantic role constants
ROLE_MEASURE = "Measure"
ROLE_DIMENSION = "Dimension"
ROLE_DATE = "Date Dimension"
ROLE_IDENTIFIER = "Identifier"
ROLE_CATEGORICAL = "Categorical Dimension"

def detect_column_role(col_name: str, series: pd.Series) -> str:
    """
    Classifies a dataset column into a Power BI semantic role based on name and content profiling.
    """
    col_clean = str(col_name).strip().lower()
    
    # 1. Date check
    if pd.api.types.is_datetime64_any_dtype(series):
        return ROLE_DATE
    
    if any(date_word in col_clean for date_word in ['date', 'time', 'year', 'month', 'day', 'quarter', 'dt']):
        # Verify if parseable as date
        sample = series.dropna().astype(str).head(50)
        try:
            pd.to_datetime(sample, errors='raise')
            return ROLE_DATE
        except (ValueError, TypeError):
            pass

    # 2. Identifier check
    if any(id_word in col_clean for id_word in ['id', 'key', 'code', 'number', 'num', 'uuid', 'guid', 'sku', 'zip', 'postal']):
        return ROLE_IDENTIFIER
    
    n_unique = series.nunique()
    n_total = len(series.dropna())

    if n_total > 0 and (n_unique == n_total) and (pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series)):
        return ROLE_IDENTIFIER

    # 3. Numeric Measure check
    if pd.api.types.is_numeric_dtype(series):
        # Exclude year/zip binary flags if strictly 0/1 or distinct low integers unless named sales/amount/profit/etc.
        if n_unique <= 2 and col_clean.startswith(('is_', 'has_', 'flag_')):
            return ROLE_CATEGORICAL
        if 'year' in col_clean or 'zip' in col_clean:
            return ROLE_DIMENSION
        return ROLE_MEASURE

    # 4. Text / Categorical check
    if n_unique < 100 or (n_total > 0 and (n_unique / n_total) < 0.2):
        return ROLE_CATEGORICAL
    
    return ROLE_DIMENSION


def map_pandas_dtype_to_powerbi(series: pd.Series) -> str:
    """Maps pandas Series dtype to Power BI / TMDL primitive data type."""
    if pd.api.types.is_integer_dtype(series):
        return "int64"
    elif pd.api.types.is_float_dtype(series):
        return "double"
    elif pd.api.types.is_bool_dtype(series):
        return "boolean"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "dateTime"
    else:
        return "string"
