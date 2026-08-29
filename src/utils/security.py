"""
Security and input sanitization helpers for Dash2BI AI.
Ensures uploaded files cannot exploit path traversal or execute arbitrary scripts.
"""

import os
import re
import html
from pathlib import Path

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit

ALLOWED_DATASET_EXTENSIONS = {".csv", ".xlsx", ".xls"}
ALLOWED_HTML_EXTENSIONS = {".html", ".htm"}

def sanitize_filename(filename: str) -> str:
    """Sanitizes filename to prevent directory traversal."""
    base = os.path.basename(filename)
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', base)

def is_safe_path(base_dir: str, target_path: str) -> bool:
    """Checks if target_path stays strictly within base_dir."""
    try:
        resolved_base = Path(base_dir).resolve()
        resolved_target = Path(target_path).resolve()
        return resolved_base in resolved_target.parents or resolved_base == resolved_target
    except Exception:
        return False

def sanitize_html_text(text: str) -> str:
    """Sanitizes text extracted from HTML elements."""
    if not text:
        return ""
    clean = html.unescape(text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean
