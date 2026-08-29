"""
Hybrid Field Mapping Engine for Dash2BI AI.
Connects HTML Dashboard component labels with Dataset columns using multi-tier matching algorithms:
1. Exact matching
2. Case-insensitive & normalized matching
3. Synonym dictionary resolution
4. Substring & Token similarity
5. Data type compatibility
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from src.mapping.confidence import get_confidence_level, build_mapping_explanation, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW

# Domain Synonym Dictionary for Business & Analytics Dashboards
SYNONYM_MAP = {
    "sales": ["sales", "revenue", "turnover", "income", "amount", "total_sales", "gross_sales"],
    "profit": ["profit", "net_profit", "margin", "earnings", "net_income", "gain"],
    "cost": ["cost", "expense", "cogs", "total_cost", "expenditure"],
    "quantity": ["quantity", "units", "qty", "volume", "count", "items"],
    "discount": ["discount", "rebate", "markdown"],
    "region": ["region", "territory", "zone", "area", "location", "country", "state"],
    "category": ["category", "segment", "product_category", "type", "class", "group"],
    "customer": ["customer", "client", "buyer", "user", "account", "customer_name"],
    "order_date": ["order_date", "date", "order_dt", "transaction_date", "sales_date", "time"],
}

def normalize_token(text: str) -> str:
    """Removes special characters, currencies, and extra whitespace."""
    clean = re.sub(r'[$€£₹%_\-\.]', ' ', text)
    clean = re.sub(r'\s+', ' ', clean).strip().lower()
    return clean

def map_label_to_dataset_field(
    label: str,
    dataset_cols: List[Dict[str, Any]],
    target_role: Optional[str] = None
) -> Tuple[Optional[str], float, str, List[str]]:
    """
    Maps a visual title/label to the best matching dataset column.
    Returns (matched_col_name, score, match_type, reasons)
    """
    if not label or not dataset_cols:
        return None, 0.0, "NONE", ["Label or dataset columns missing."]

    clean_label = normalize_token(label)
    reasons = []

    col_names = [c["original_name"] for c in dataset_cols]
    norm_names = {c["original_name"]: normalize_token(c["original_name"]) for c in dataset_cols}

    # 1. Exact Match
    for c in dataset_cols:
        if label.strip() == c["original_name"].strip():
            reasons.append(f"Exact field name match with '{c['original_name']}'.")
            return c["original_name"], 1.00, "EXACT", reasons

    # 2. Case-insensitive / Normalized Match
    for c in dataset_cols:
        if clean_label == norm_names[c["original_name"]]:
            reasons.append(f"Case-insensitive normalized match with '{c['original_name']}'.")
            return c["original_name"], 0.95, "NORMALIZED", reasons

    # 3. Substring Containment Match
    for c in dataset_cols:
        col_norm = norm_names[c["original_name"]]
        if col_norm in clean_label or clean_label in col_norm:
            reasons.append(f"Field name '{c['original_name']}' is contained within title '{label}'.")
            return c["original_name"], 0.88, "SUBSTRING", reasons

    # 4. Synonym Dictionary Match
    for key_concept, synonyms in SYNONYM_MAP.items():
        if any(syn in clean_label for syn in synonyms):
            for c in dataset_cols:
                col_norm = norm_names[c["original_name"]]
                if any(syn in col_norm for syn in synonyms):
                    reasons.append(f"Semantic synonym match between '{label}' and '{c['original_name']}' under concept '{key_concept}'.")
                    return c["original_name"], 0.85, "SYNONYM", reasons

    # 5. Token Overlap Match
    label_tokens = set(clean_label.split())
    best_score = 0.0
    best_col = None
    for c in dataset_cols:
        col_tokens = set(norm_names[c["original_name"]].split())
        overlap = label_tokens.intersection(col_tokens)
        if overlap:
            score = 0.50 + (len(overlap) * 0.15)
            if score > best_score:
                best_score = min(0.80, score)
                best_col = c["original_name"]

    if best_col and best_score >= 0.60:
        reasons.append(f"Token overlap match with '{best_col}'.")
        return best_col, best_score, "TOKEN_OVERLAP", reasons

    # Fallback to first available numeric/categorical column matching target role
    for c in dataset_cols:
        if target_role and c.get("role") == target_role:
            reasons.append(f"Selected '{c['original_name']}' as fallback for target role '{target_role}'.")
            return c["original_name"], 0.45, "FALLBACK", reasons

    first_col = col_names[0] if col_names else None
    reasons.append("Weak similarity match; requires user review.")
    return first_col, 0.35, "WEAK", reasons
