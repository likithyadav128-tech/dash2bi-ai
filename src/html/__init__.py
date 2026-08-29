"""
HTML package initialization.
"""
from src.html.html_loader import load_html_dashboard
from src.html.dom_parser import parse_dom, find_script_blocks
from src.html.css_parser import parse_inline_styles, extract_color_from_style
from src.html.chart_detector import detect_chart_frameworks
from src.html.visual_detector import analyze_html_dashboard, detect_kpi_cards, detect_charts, detect_tables, detect_filters
from src.html.layout_detector import assign_layout_coordinates

__all__ = [
    "load_html_dashboard",
    "parse_dom",
    "find_script_blocks",
    "parse_inline_styles",
    "extract_color_from_style",
    "detect_chart_frameworks",
    "analyze_html_dashboard",
    "detect_kpi_cards",
    "detect_charts",
    "detect_tables",
    "detect_filters",
    "assign_layout_coordinates",
]
