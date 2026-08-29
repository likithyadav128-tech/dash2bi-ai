"""
File validation routines for dataset and HTML uploads in Dash2BI AI.
"""

import os
from typing import Tuple, Dict, Any
from src.utils.security import ALLOWED_DATASET_EXTENSIONS, ALLOWED_HTML_EXTENSIONS, MAX_FILE_SIZE_BYTES
from src.utils.errors import DatasetValidationError, HTMLParsingError

def validate_dataset_file(file_name: str, file_bytes: bytes) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates uploaded dataset file.
    Returns (is_valid, error_message, metadata)
    """
    if not file_name or not file_bytes:
        return False, "File is empty or invalid.", {}
    
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ALLOWED_DATASET_EXTENSIONS:
        return False, f"Unsupported dataset extension '{ext}'. Allowed extensions: .csv, .xlsx, .xls", {}

    size = len(file_bytes)
    if size > MAX_FILE_SIZE_BYTES:
        return False, f"File size ({size / (1024*1024):.1f} MB) exceeds maximum limit of 50 MB.", {}

    if size == 0:
        return False, "Uploaded file contains 0 bytes.", {}

    metadata = {
        "file_name": file_name,
        "extension": ext,
        "size_bytes": size,
        "size_formatted": f"{size / 1024:.1f} KB" if size < 1024*1024 else f"{size / (1024*1024):.2f} MB"
    }
    return True, "", metadata


def validate_html_file(file_name: str, file_bytes: bytes) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates uploaded HTML dashboard file.
    Returns (is_valid, error_message, metadata)
    """
    if not file_name or not file_bytes:
        return False, "HTML file is empty or invalid.", {}

    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ALLOWED_HTML_EXTENSIONS:
        return False, f"Unsupported HTML extension '{ext}'. Allowed extensions: .html, .htm", {}

    size = len(file_bytes)
    if size > MAX_FILE_SIZE_BYTES:
        return False, f"HTML file size ({size / (1024*1024):.1f} MB) exceeds limit of 50 MB.", {}

    if size == 0:
        return False, "Uploaded HTML file is empty.", {}

    # Basic content sanity check
    try:
        content_snippet = file_bytes[:1000].decode('utf-8', errors='ignore').lower()
        if not ("<html" in content_snippet or "<div" in content_snippet or "<body" in content_snippet or "<svg" in content_snippet or "<table" in content_snippet or "<script" in content_snippet or "<!doctype" in content_snippet):
            return False, "File does not appear to be a valid HTML document.", {}
    except Exception as e:
        return False, f"Failed to read HTML file content: {str(e)}", {}

    metadata = {
        "file_name": file_name,
        "extension": ext,
        "size_bytes": size,
        "size_formatted": f"{size / 1024:.1f} KB" if size < 1024*1024 else f"{size / (1024*1024):.2f} MB"
    }
    return True, "", metadata
