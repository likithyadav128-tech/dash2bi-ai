"""
DAX Measure Generator module for Dash2BI AI.
Synthesizes DAX formulas for KPIs, aggregations, counts, distinct counts, and ratios.
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
    Generates DAX measure expression.
    """
    clean_measure = re.sub(r'[^a-zA-Z0-9_\s]', '', measure_name).strip()
    agg = aggregation.upper() if aggregation else "SUM"

    if agg == "DIVIDE":
        num = numerator_col or column_name or "Profit"
        den = denominator_col or "Sales"
        dax = f"{clean_measure} = \nDIVIDE(\n    SUM('{table_name}'[{num}]),\n    SUM('{table_name}'[{den}])\n)"
    elif agg == "COUNT":
        dax = f"{clean_measure} = \nCOUNTROWS('{table_name}')"
    elif agg == "DISTINCTCOUNT":
        col = column_name or "ID"
        dax = f"{clean_measure} = \nDISTINCTCOUNT('{table_name}'[{col}])"
    elif agg == "AVERAGE":
        col = column_name or "Sales"
        dax = f"{clean_measure} = \nAVERAGE('{table_name}'[{col}])"
    elif agg == "MIN":
        col = column_name or "Sales"
        dax = f"{clean_measure} = \nMIN('{table_name}'[{col}])"
    elif agg == "MAX":
        col = column_name or "Sales"
        dax = f"{clean_measure} = \nMAX('{table_name}'[{col}])"
    else:  # SUM default
        col = column_name or "Sales"
        dax = f"{clean_measure} = \nSUM('{table_name}'[{col}])"

    return dax.strip()

def generate_dax_for_mapped_visuals(
    table_name: str,
    mapped_visuals: List[Dict[str, Any]],
    dataset_cols: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generates DAX measures for all relevant mapped visual components.
    Ensures measure names are strictly unique and do not collide with column or existing measure names.
    """
    measures = []
    existing_col_names = [c["original_name"] for c in dataset_cols]
    
    # Track used names (columns + measures) to prevent duplicate key errors in Analysis Services
    seen_names = set(c["original_name"].strip().lower() for c in dataset_cols)

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

            if matched_field and matched_field in existing_col_names:
                formula = generate_dax_formula(measure_name, table_name, matched_field, agg)
                measures.append({
                    "measure_name": measure_name,
                    "table_name": table_name,
                    "column_name": matched_field,
                    "aggregation": agg,
                    "dax_formula": formula,
                    "visual_id": v["visual_id"]
                })
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

    log_event("dax", f"Generated {len(measures)} unique DAX measures for Power BI semantic model.")
    return measures
