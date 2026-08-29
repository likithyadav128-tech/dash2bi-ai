"""
Hybrid Field Mapping Engine for Dash2BI AI.
Connects HTML Dashboard component labels with Dataset columns using multi-tier matching algorithms:
1. Exact matching
2. Case-insensitive & CamelCase normalized matching
3. Comprehensive domain synonym resolution (Business, E-commerce, Healthcare, Public Data, Finance)
4. Substring & Token/Stem similarity matching
5. Smart role-based fallback filtering (ignoring serial numbers / IDs)
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from src.mapping.confidence import get_confidence_level, build_mapping_explanation, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW

# Comprehensive Domain Synonym Dictionary
SYNONYM_MAP = {
    # Healthcare & COVID / Public Metrics
    "confirmed": ["confirmed", "cases", "total_cases", "positive", "infected", "infections", "total_confirmed", "confirmedindiannational", "confirmedforeignnational", "new_cases"],
    "active": ["active", "active_cases", "current_cases", "in_treatment", "under_treatment", "active_patients"],
    "cured": ["cured", "recovered", "discharged", "recovery", "total_cured", "cured_discharged", "recoveries"],
    "deaths": ["deaths", "deceased", "fatalities", "mortality", "death", "total_deaths", "dead"],
    "state": ["state", "province", "region", "district", "territory", "location", "area", "state_ut", "city", "country", "zone"],
    
    # E-Commerce & Retail
    "sales": ["sales", "revenue", "turnover", "income", "amount", "total_sales", "gross_sales", "billing"],
    "profit": ["profit", "net_profit", "margin", "earnings", "net_income", "gain", "profit_margin"],
    "cost": ["cost", "expense", "cogs", "total_cost", "expenditure", "outflow"],
    "quantity": ["quantity", "units", "qty", "volume", "count", "items", "ordered_units"],
    "discount": ["discount", "rebate", "markdown", "concession"],
    "category": ["category", "segment", "product_category", "type", "class", "group", "vertical"],
    "customer": ["customer", "client", "buyer", "user", "account", "customer_name", "patient"],
    "order_date": ["order_date", "date", "order_dt", "transaction_date", "sales_date", "time", "timestamp", "year", "month", "last_updated"]
}

# Common Serial Number & ID patterns to exclude from fallback selection
IGNORE_ID_PATTERNS = re.compile(r'^(sno|sn|s_no|sl_no|slno|id|index|row_id|key|uuid|guid|code|number|num)$', re.I)

def normalize_token(text: str) -> str:
    """
    Normalizes text for matching:
    1. Splits CamelCase strings (e.g. 'ConfirmedIndianNational' -> 'Confirmed Indian National')
    2. Removes special symbols
    3. Converts to lower case
    """
    if not text:
        return ""
    # CamelCase split
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', str(text))
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    clean = re.sub(r'[$€£₹%_\-\.\/\\]', ' ', s2)
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
        if label.strip().lower() == c["original_name"].strip().lower():
            reasons.append(f"Exact field name match with '{c['original_name']}'.")
            return c["original_name"], 1.00, "EXACT", reasons

    # 2. Case-insensitive & CamelCase Normalized Match
    for c in dataset_cols:
        if clean_label == norm_names[c["original_name"]]:
            reasons.append(f"Normalized match with '{c['original_name']}'.")
            return c["original_name"], 0.95, "NORMALIZED", reasons

    # 3. Domain Synonym Dictionary Match
    for key_concept, synonyms in SYNONYM_MAP.items():
        if any(syn in clean_label or syn in clean_label.replace(" ", "") for syn in synonyms):
            for c in dataset_cols:
                col_norm = norm_names[c["original_name"]]
                col_no_space = col_norm.replace(" ", "")
                if any(syn in col_norm or syn in col_no_space for syn in synonyms):
                    reasons.append(f"Domain synonym match between '{label}' and '{c['original_name']}' under concept '{key_concept}'.")
                    return c["original_name"], 0.90, "SYNONYM", reasons

    # 4. Substring & Stem Containment Match
    for c in dataset_cols:
        col_norm = norm_names[c["original_name"]]
        if col_norm and (col_norm in clean_label or clean_label in col_norm):
            reasons.append(f"Substring match between '{label}' and '{c['original_name']}'.")
            return c["original_name"], 0.88, "SUBSTRING", reasons

    # 5. Token & Stem Overlap Match
    label_tokens = set(clean_label.split())
    best_score = 0.0
    best_col = None
    for c in dataset_cols:
        col_tokens = set(norm_names[c["original_name"]].split())
        overlap = label_tokens.intersection(col_tokens)
        
        # Check stem/partial token overlap (e.g. 'confirm' in 'confirmed')
        partial_overlap = 0
        for lt in label_tokens:
            if len(lt) >= 4:
                for ct in col_tokens:
                    if len(ct) >= 4 and (lt in ct or ct in lt):
                        partial_overlap += 1

        total_overlap_cnt = len(overlap) + partial_overlap
        if total_overlap_cnt > 0:
            score = 0.60 + min(0.25, total_overlap_cnt * 0.15)
            if score > best_score:
                best_score = score
                best_col = c["original_name"]

    if best_col and best_score >= 0.65:
        reasons.append(f"Token/stem overlap match with '{best_col}'.")
        return best_col, min(0.85, best_score), "TOKEN_OVERLAP", reasons

    # 6. Smart Fallback Selection (Filter out Serial Numbers and IDs)
    non_id_cols = [
        c for c in dataset_cols 
        if not IGNORE_ID_PATTERNS.match(c["original_name"].strip()) and c.get("role") != "Identifier"
    ]
    
    candidate_list = non_id_cols if non_id_cols else dataset_cols

    # Fallback matching target role
    if target_role:
        for c in candidate_list:
            if c.get("role") == target_role:
                reasons.append(f"Selected non-ID column '{c['original_name']}' as role-based fallback for '{target_role}'.")
                return c["original_name"], 0.50, "ROLE_FALLBACK", reasons

    fallback_col = candidate_list[0]["original_name"] if candidate_list else col_names[0]
    reasons.append(f"Default fallback selected '{fallback_col}'; requires user verification.")
    return fallback_col, 0.40, "FALLBACK", reasons
