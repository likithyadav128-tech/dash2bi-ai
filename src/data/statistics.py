"""
Statistics computation utility for dataset columns.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

def compute_column_statistics(series: pd.Series) -> Dict[str, Any]:
    """Computes summary statistics for a dataset column."""
    null_count = int(series.isnull().sum())
    total_count = len(series)
    unique_count = int(series.nunique())
    
    clean_series = series.dropna()
    examples = [str(val) for val in clean_series.head(5).tolist()]
    
    stats: Dict[str, Any] = {
        "null_count": null_count,
        "null_percentage": round((null_count / total_count) * 100, 2) if total_count > 0 else 0,
        "unique_count": unique_count,
        "examples": examples,
        "min": None,
        "max": None,
        "mean": None,
        "median": None
    }
    
    if pd.api.types.is_numeric_dtype(series) and not clean_series.empty:
        try:
            stats["min"] = float(clean_series.min())
            stats["max"] = float(clean_series.max())
            stats["mean"] = round(float(clean_series.mean()), 2)
            stats["median"] = round(float(clean_series.median()), 2)
        except Exception:
            pass
    elif pd.api.types.is_datetime64_any_dtype(series) and not clean_series.empty:
        try:
            stats["min"] = str(clean_series.min())
            stats["max"] = str(clean_series.max())
        except Exception:
            pass
            
    return stats
