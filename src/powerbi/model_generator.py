"""
Power BI Semantic Model Representation Generator for Dash2BI AI.
"""

from typing import Dict, Any, List

def build_semantic_model_spec(
    table_name: str,
    dataset_cols: List[Dict[str, Any]],
    measures: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Builds an in-memory representation of the Power BI Semantic Model.
    """
    columns = []
    for col in dataset_cols:
        columns.append({
            "name": col["original_name"],
            "dataType": col["data_type"],
            "sourceColumn": col["original_name"],
            "summarizeBy": "sum" if col["role"] == "Measure" else "none"
        })

    model_measures = []
    for m in measures:
        model_measures.append({
            "name": m["measure_name"],
            "expression": m["dax_formula"],
            "formatString": "$#,##0.00" if "Sales" in m["measure_name"] or "Profit" in m["measure_name"] else ("0.0%" if "Margin" in m["measure_name"] else "#,##0")
        })

    return {
        "model_name": "Dash2BI_Model",
        "tables": [
            {
                "name": table_name,
                "columns": columns,
                "measures": model_measures
            }
        ]
    }
