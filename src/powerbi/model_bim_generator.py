"""
Model BIM Generator for Dash2BI AI.
Generates model.bim (Tabular Object Model JSON) required by Power BI Desktop for Semantic Models.
Guarantees unique column and measure collections.
"""

import json
from typing import Dict, Any, List

def generate_model_bim_json(
    table_name: str,
    dataset_cols: List[Dict[str, Any]],
    measures: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates complete model.bim JSON structure with unique measure collections."""
    safe_table = table_name.replace(" ", "_")
    columns = []
    seen_col_names = set()
    
    for col in dataset_cols:
        col_name = col["original_name"].strip()
        if col_name.lower() in seen_col_names:
            continue
        seen_col_names.add(col_name.lower())
        columns.append({
            "name": col_name,
            "dataType": col.get("data_type", "string"),
            "sourceColumn": col_name,
            "summarizeBy": "sum" if col["role"] == "Measure" else "none"
        })

    model_measures = []
    seen_m_names = set()
    for m in measures:
        m_name = m["measure_name"].strip()
        if m_name.lower() in seen_m_names or m_name.lower() in seen_col_names:
            continue
        seen_m_names.add(m_name.lower())

        expr = m["dax_formula"].split("\n") if "\n" in m["dax_formula"] else [m["dax_formula"]]
        model_measures.append({
            "name": m_name,
            "expression": expr,
            "formatString": "$#,##0.00" if "Sales" in m_name or "Profit" in m_name else ("0.0%" if "Margin" in m_name else "#,##0")
        })

    m_partition_expression = [
        "let",
        f'    Source = Csv.Document(File.Contents("dataset.csv"), [Delimiter=",", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
        '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])',
        "in",
        '    #"Promoted Headers"'
    ]

    return {
        "name": f"{safe_table}_Model",
        "compatibilityLevel": 1550,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True
            },
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "tables": [
                {
                    "name": safe_table,
                    "lineageTag": "00000000-0000-0000-0000-000000000001",
                    "columns": columns,
                    "partitions": [
                        {
                            "name": safe_table,
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": m_partition_expression
                            }
                        }
                    ],
                    "measures": model_measures
                }
            ]
        }
    }
