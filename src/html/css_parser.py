"""
CSS and Layout parser module for Dash2BI AI.
"""

import re
from typing import Dict, Any, Optional

def parse_inline_styles(style_str: str) -> Dict[str, str]:
    """Parses a CSS style attribute string into a key-value dictionary."""
    styles = {}
    if not style_str:
        return styles
    
    rules = style_str.split(';')
    for rule in rules:
        if ':' in rule:
            key, val = rule.split(':', 1)
            styles[key.strip().lower()] = val.strip().lower()
    return styles

def extract_color_from_style(style_dict: Dict[str, str]) -> Optional[str]:
    """Extracts background-color or text color from inline styles."""
    for key in ['background-color', 'background', 'color']:
        if key in style_dict:
            val = style_dict[key]
            if val.startswith('#') or val.startswith('rgb'):
                return val
    return None
