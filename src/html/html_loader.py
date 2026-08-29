"""
HTML loader module for Dash2BI AI.
"""

from typing import Tuple, Dict, Any
from src.utils.errors import HTMLParsingError
from src.utils.logging import log_event

def load_html_dashboard(file_bytes: bytes) -> str:
    """Loads HTML file bytes into a clean string."""
    try:
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return file_bytes.decode('latin-1')
    except Exception as e:
        raise HTMLParsingError(
            message=f"Failed to read HTML file: {str(e)}",
            details="HTML character encoding could not be resolved.",
            solution="Ensure the file is encoded in valid UTF-8 or ASCII format."
        )
