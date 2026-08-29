"""
DAX Validator module for Dash2BI AI.
Validates DAX formula syntax and verifies that referenced table and column names exist.
"""

import re
from typing import Dict, Any, List, Tuple

def validate_dax_formula(
    dax_formula: str,
    valid_tables: List[str],
    valid_columns: List[str]
) -> Tuple[bool, List[str]]:
    """
    Validates DAX formula for syntax and schema reference integrity.
    Returns (is_valid, list_of_errors)
    """
    errors = []
    if not dax_formula or not dax_formula.strip():
        return False, ["DAX formula is empty."]

    # Extract table references: 'TableName'[ColumnName]
    table_refs = re.findall(r"'([^']+)'", dax_formula)
    for tbl in table_refs:
        if tbl not in valid_tables:
            errors.append(f"Referenced table '{tbl}' does not exist in dataset schema.")

    # Extract column references: [ColumnName]
    col_refs = re.findall(r'\[([^\]]+)\]', dax_formula)
    for col in col_refs:
        if col not in valid_columns:
            errors.append(f"Referenced column '{col}' does not exist in dataset schema.")

    # Check balanced parentheses
    if dax_formula.count('(') != dax_formula.count(')'):
        errors.append("Unbalanced parentheses in DAX formula.")

    return len(errors) == 0, errors
