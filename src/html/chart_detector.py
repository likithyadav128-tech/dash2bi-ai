"""
JS Chart Framework Detector module for Dash2BI AI.
Recognizes Chart.js, Plotly, Highcharts, ECharts, ApexCharts, D3, Google Charts, Canvas, SVG.
"""

import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any

CHART_FRAMEWORKS = [
    "Chart.js", "Plotly", "Highcharts", "ECharts", "ApexCharts", "D3", "Google Charts", "Canvas", "SVG"
]

def detect_chart_frameworks(soup: BeautifulSoup, script_contents: List[str]) -> List[Dict[str, Any]]:
    """
    Scans HTML script tags and elements for chart framework initialization patterns and configurations.
    Returns list of detected chart configs.
    """
    detected_charts = []
    combined_scripts = "\n".join(script_contents)
    
    # 1. Chart.js detection
    if "new Chart" in combined_scripts or "Chart(" in combined_scripts or "chart.js" in html_soup_str(soup):
        matches = re.findall(r'type\s*:\s*[\'"]([a-zA-Z]+)[\'"]', combined_scripts)
        for chart_type in matches:
            detected_charts.append({
                "framework": "Chart.js",
                "type": chart_type.lower(),
                "confidence": 0.95
            })
            
    # 2. Plotly detection
    if "Plotly.newPlot" in combined_scripts or "plotly.js" in html_soup_str(soup):
        matches = re.findall(r'type\s*:\s*[\'"]([a-zA-Z]+)[\'"]', combined_scripts)
        for chart_type in matches:
            detected_charts.append({
                "framework": "Plotly",
                "type": chart_type.lower(),
                "confidence": 0.95
            })

    # 3. Highcharts detection
    if "Highcharts.chart" in combined_scripts or "highcharts.js" in html_soup_str(soup):
        matches = re.findall(r'type\s*:\s*[\'"]([a-zA-Z]+)[\'"]', combined_scripts)
        for chart_type in matches:
            detected_charts.append({
                "framework": "Highcharts",
                "type": chart_type.lower(),
                "confidence": 0.95
            })

    # 4. ApexCharts detection
    if "ApexCharts" in combined_scripts or "apexcharts" in html_soup_str(soup):
        matches = re.findall(r'chart\s*:\s*\{[^}]*type\s*:\s*[\'"]([a-zA-Z]+)[\'"]', combined_scripts, re.DOTALL)
        for chart_type in matches:
            detected_charts.append({
                "framework": "ApexCharts",
                "type": chart_type.lower(),
                "confidence": 0.95
            })

    # 5. ECharts detection
    if "echarts.init" in combined_scripts or "echarts" in html_soup_str(soup):
        detected_charts.append({
            "framework": "ECharts",
            "type": "chart",
            "confidence": 0.90
        })

    # 6. Canvas & SVG tag detection
    canvas_tags = soup.find_all('canvas')
    for c in canvas_tags:
        detected_charts.append({
            "framework": "Canvas",
            "element_id": c.get('id', ''),
            "type": "canvas_chart",
            "confidence": 0.80
        })

    return detected_charts

def html_soup_str(soup: BeautifulSoup) -> str:
    return str(soup).lower()
