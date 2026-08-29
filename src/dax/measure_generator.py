"""
DAX Measure Generator module for Dash2BI AI.
Synthesizes clean DAX formula expressions for KPIs, aggregations, counts, distinct counts, ratios, and multi-column domain formulas.
Guarantees unique measure names preventing Analysis Services collection deserialization collisions.
"""

import re
from typing import Dict, Any, List, Optional
from src.utils.logging import log_event

def generate_dax_formula(
    measure_name: str,
    table_name: str,
    column_name: Optional[str],
    aggregation: str,
    numerator_col: Optional[str] = None,
    denominator_col: Optional[str] = None
) -> str:
    """
    Generates DAX measure expression (Right-Hand Side only for TMDL/BIM compatibility).
    """
    agg = aggregation.upper() if aggregation else "SUM"

    if agg == "DIVIDE":
        num = numerator_col or column_name or "Profit"
        den = denominator_col or "Sales"
        dax = f"DIVIDE(\n    SUM('{table_name}'[{num}]),\n    SUM('{table_name}'[{den}])\n)"
    elif agg == "COUNT":
        dax = f"COUNTROWS('{table_name}')"
    elif agg == "DISTINCTCOUNT":
        col = column_name or "ID"
        dax = f"DISTINCTCOUNT('{table_name}'[{col}])"
    elif agg == "AVERAGE":
        col = column_name or "Sales"
        dax = f"AVERAGE('{table_name}'[{col}])"
    elif agg == "MIN":
        col = column_name or "Sales"
        dax = f"MIN('{table_name}'[{col}])"
    elif agg == "MAX":
        col = column_name or "Sales"
        dax = f"MAX('{table_name}'[{col}])"
    else:  # SUM default
        col = column_name or "Sales"
        dax = f"SUM('{table_name}'[{col}])"

    return dax.strip()

def generate_dax_for_mapped_visuals(
    table_name: str,
    mapped_visuals: List[Dict[str, Any]],
    dataset_cols: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generates DAX measures for all relevant mapped visual components.
    Ensures measure names are strictly unique and do not collide with column or existing measure names.
    Supports multi-column COVID/Healthcare metric calculations (ConfirmedIndianNational + ConfirmedForeignNational).
    """
    measures = []
    existing_col_names = [c["original_name"] for c in dataset_cols]
    
    # Track used names (columns + measures) to prevent duplicate key errors in Analysis Services
    seen_names = set(c["original_name"].strip().lower() for c in dataset_cols)

    has_indian = "ConfirmedIndianNational" in existing_col_names
    has_foreign = "ConfirmedForeignNational" in existing_col_names
    has_cured = "Cured" in existing_col_names
    has_deaths = "Deaths" in existing_col_names

    for v in mapped_visuals:
        if v["html_type"] in ["kpi_card", "metric_card"]:
            raw_title = v.get("title", "KPI Measure").strip() or "KPI Measure"
            matched_field = v.get("mapped_field")
            agg = v.get("aggregation", "SUM")

            # Deduplicate measure name
            measure_name = raw_title
            counter = 2
            while measure_name.lower() in seen_names:
                measure_name = f"{raw_title} {counter}"
                counter += 1
            
            seen_names.add(measure_name.lower())

            # Domain specific multi-column composite DAX formulas
            raw_title_upper = raw_title.upper()
            if "CONFIRMED" in raw_title_upper and has_indian and has_foreign:
                formula = f"SUM('{table_name}'[ConfirmedIndianNational]) + SUM('{table_name}'[ConfirmedForeignNational])"
                measures.append({
                    "measure_name": measure_name,
                    "table_name": table_name,
                    "column_name": "ConfirmedIndianNational",
                    "aggregation": "SUM",
                    "dax_formula": formula,
                    "visual_id": v["visual_id"]
                })
                v["measure_name"] = measure_name
            elif "ACTIVE" in raw_title_upper and has_indian and has_foreign and has_cured and has_deaths:
                formula = f"(SUM('{table_name}'[ConfirmedIndianNational]) + SUM('{table_name}'[ConfirmedForeignNational])) - SUM('{table_name}'[Cured]) - SUM('{table_name}'[Deaths])"
                measures.append({
                    "measure_name": measure_name,
                    "table_name": table_name,
                    "column_name": "ConfirmedIndianNational",
                    "aggregation": "SUM",
                    "dax_formula": formula,
                    "visual_id": v["visual_id"]
                })
                v["measure_name"] = measure_name
            elif matched_field and matched_field in existing_col_names:
                formula = generate_dax_formula(measure_name, table_name, matched_field, agg)
                measures.append({
                    "measure_name": measure_name,
                    "table_name": table_name,
                    "column_name": matched_field,
                    "aggregation": agg,
                    "dax_formula": formula,
                    "visual_id": v["visual_id"]
                })
                v["measure_name"] = measure_name
            elif agg == "DIVIDE":
                num = "Profit" if "Profit" in existing_col_names else (existing_col_names[0] if existing_col_names else "Field1")
                den = "Sales" if "Sales" in existing_col_names else (existing_col_names[1] if len(existing_col_names) > 1 else "Field2")
                formula = generate_dax_formula(measure_name, table_name, None, "DIVIDE", num, den)
                measures.append({
                    "measure_name": measure_name,
                    "table_name": table_name,
                    "column_name": num,
                    "aggregation": "DIVIDE",
                    "dax_formula": formula,
                    "visual_id": v["visual_id"]
                })
                v["measure_name"] = measure_name

    log_event("dax", f"Generated {len(measures)} unique DAX measures for Power BI semantic model.")
    return measures
