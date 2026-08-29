"""
DOM Parser module using BeautifulSoup for HTML dashboard analysis.
"""

from bs4 import BeautifulSoup, Tag
import re
from typing import List, Dict, Any, Optional
from src.utils.security import sanitize_html_text

class DOMNode:
    """Represents a simplified DOM node extracted from HTML."""
    def __init__(self, tag_name: str, attributes: Dict[str, str], text: str, html_snippet: str):
        self.tag_name = tag_name
        self.attributes = attributes
        self.classes = attributes.get("class", "").split()
        self.id = attributes.get("id", "")
        self.text = sanitize_html_text(text)
        self.html_snippet = html_snippet
        self.style_str = attributes.get("style", "")

def parse_dom(html_content: str) -> BeautifulSoup:
    """Parses HTML content using BeautifulSoup."""
    return BeautifulSoup(html_content, 'html.parser')

def find_script_blocks(soup: BeautifulSoup) -> List[str]:
    """Extracts all script contents from HTML."""
    scripts = []
    for script in soup.find_all('script'):
        if script.string:
            scripts.append(script.string)
    return scripts
