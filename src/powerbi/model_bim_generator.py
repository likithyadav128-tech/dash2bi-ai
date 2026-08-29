"""
Model BIM Generator for Dash2BI AI.
Generates model.bim (Tabular Object Model JSON) required by Power BI Desktop for Semantic Models.
"""

import json
from typing import Dict, Any, List

def generate_model_bim_json(
    table_name: str,
    dataset_cols: List[Dict[str, Any]],
    measures: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates complete model.bim JSON structure."""
    safe_table = table_name.replace(" ", "_")
    columns = []
    for col in dataset_cols:
        columns.append({
            "name": col["original_name"],
            "dataType": col.get("data_type", "string"),
            "sourceColumn": col["original_name"],
            "summarizeBy": "sum" if col["role"] == "Measure" else "none"
        })

    model_measures = []
    for m in measures:
        expr = m["dax_formula"].split("\n") if "\n" in m["dax_formula"] else [m["dax_formula"]]
        model_measures.append({
            "name": m["measure_name"],
            "expression": expr,
            "formatString": "$#,##0.00" if "Sales" in m["measure_name"] or "Profit" in m["measure_name"] else ("0.0%" if "Margin" in m["measure_name"] else "#,##0")
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
