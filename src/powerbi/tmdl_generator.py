"""
TMDL (Tabular Model Definition Language) Generator for Dash2BI AI.
Generates Microsoft TMDL files for Power BI Project semantic models.
"""

from typing import Dict, Any, List

def generate_model_tmdl(model_name: str, table_name: str) -> str:
    """Generates root model.tmdl file content."""
    return f"""model {model_name}
	culture: en-US
	defaultPowerBIDataSourceVersion: powerBI_V3

ref table {table_name}
"""

def generate_table_tmdl(table_name: str, columns: List[Dict[str, Any]], measures: List[Dict[str, Any]]) -> str:
    """Generates TMDL table definition file content."""
    lines = [f"table {table_name}"]
    lines.append("\tlineageTag: 00000000-0000-0000-0000-000000000001\n")

    # Columns
    for col in columns:
        col_name = col["name"]
        d_type = col.get("dataType", "string")
        lines.append(f"\tcolumn '{col_name}'")
        lines.append(f"\t\tdataType: {d_type}")
        lines.append(f"\t\tlineageTag: col-{col_name.replace(' ', '_')}")
        lines.append(f"\t\tsummarizeBy: {col.get('summarizeBy', 'none')}")
        lines.append(f"\t\tsourceColumn: {col_name}\n")

    # Measures
    for m in measures:
        m_name = m["name"]
        expr = m["expression"].replace("\n", "\n\t\t\t")
        lines.append(f"\tmeasure '{m_name}' = \n\t\t\t{expr}")
        lines.append(f"\t\tlineageTag: measure-{m_name.replace(' ', '_')}")
        if "formatString" in m:
            lines.append(f"\t\tformatString: {m['formatString']}")
        lines.append("")

    return "\n".join(lines)
