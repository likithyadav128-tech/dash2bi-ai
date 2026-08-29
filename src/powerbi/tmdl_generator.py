"""
TMDL (Tabular Model Definition Language) Generator for Dash2BI AI.
Generates Microsoft TMDL files for Power BI Project semantic models with optional embedded Base64 dataset partitions.
Guarantees unique column and measure names.
"""

import base64
from typing import Dict, Any, List, Optional

def generate_model_tmdl(model_name: str, table_name: str) -> str:
    """Generates root model.tmdl file content."""
    safe_table = table_name.replace(" ", "_")
    return f"""model {model_name}
	culture: en-US
	defaultPowerBIDataSourceVersion: powerBI_V3

ref table {safe_table}
"""

def generate_table_tmdl(
    table_name: str,
    columns: List[Dict[str, Any]],
    measures: List[Dict[str, Any]],
    raw_dataset_bytes: Optional[bytes] = None
) -> str:
    """Generates TMDL table definition file content with M query partition and unique measure collections."""
    safe_table = table_name.replace(" ", "_")
    lines = [f"table {safe_table}"]
    lines.append("\tlineageTag: 00000000-0000-0000-0000-000000000001\n")

    # Track seen names to prevent duplicate TMDL entities
    seen_col_names = set()
    valid_cols = []
    for col in columns:
        col_name = col["name"].strip()
        if col_name.lower() in seen_col_names:
            continue
        seen_col_names.add(col_name.lower())
        valid_cols.append(col)

    # M Query Source Partition
    num_cols = len(valid_cols)
    lines.append(f"\tpartition {safe_table} = m")
    lines.append("\t\tmode: import")
    lines.append("\t\tsource =")
    lines.append("\t\t\tlet")

    if raw_dataset_bytes:
        b64_data = base64.b64encode(raw_dataset_bytes).decode('utf-8')
        lines.append(f'\t\t\t    Source = Csv.Document(Binary.FromText("{b64_data}", BinaryEncoding.Base64), [Delimiter=",", Columns={num_cols}, Encoding=65001, QuoteStyle=QuoteStyle.None]),')
    else:
        lines.append(f'\t\t\t    Source = Csv.Document(File.Contents("dataset.csv"), [Delimiter=",", Columns={num_cols}, Encoding=65001, QuoteStyle=QuoteStyle.None]),')

    lines.append('\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])')
    lines.append("\t\t\tin")
    lines.append('\t\t\t    #"Promoted Headers"\n')

    # Columns
    for col in valid_cols:
        col_name = col["name"].strip()
        d_type = col.get("dataType", "string")
        lines.append(f"\tcolumn '{col_name}'")
        lines.append(f"\t\tdataType: {d_type}")
        lines.append(f"\t\tlineageTag: col-{col_name.replace(' ', '_')}")
        lines.append(f"\t\tsummarizeBy: {col.get('summarizeBy', 'none')}")
        lines.append(f"\t\tsourceColumn: {col_name}\n")

    # Measures
    seen_m_names = set()
    for m in measures:
        m_name = m["name"].strip()
        if m_name.lower() in seen_m_names or m_name.lower() in seen_col_names:
            continue
        seen_m_names.add(m_name.lower())

        expr = m["expression"].replace("\n", "\n\t\t\t")
        lines.append(f"\tmeasure '{m_name}' = \n\t\t\t{expr}")
        lines.append(f"\t\tlineageTag: measure-{m_name.replace(' ', '_')}")
        if "formatString" in m:
            lines.append(f"\t\tformatString: {m['formatString']}")
        lines.append("")

    return "\n".join(lines)
