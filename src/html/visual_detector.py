"""
Visual Component Detector module for Dash2BI AI.
Extracts KPI Cards, Charts, Tables, Filters, Text Boxes, and Layout metadata from HTML DOM.
"""

import re
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional
from src.html.dom_parser import parse_dom, find_script_blocks
from src.html.css_parser import parse_inline_styles
from src.html.chart_detector import detect_chart_frameworks
from src.html.layout_detector import assign_layout_coordinates
from src.utils.security import sanitize_html_text
from src.utils.logging import log_event

def parse_kpi_value(raw_val: str) -> Dict[str, Any]:
    """
    Parses raw KPI value string to extract numeric scalar, currency symbol, percentage, and unit suffix.
    Examples:
    "$2.3M" -> currency="$", unit="M", value=2.3
    "450K" -> unit="K", value=450
    "18%" -> unit="%", percentage=True, value=18
    """
    clean = raw_val.strip()
    currency = "$" if "$" in clean else ("€" if "€" in clean else ("£" if "£" in clean else ("₹" if "₹" in clean else None)))
    is_percentage = "%" in clean
    
    # Extract unit suffix
    unit = None
    if re.search(r'[MKBmkb]$', clean):
        unit = clean[-1].upper()
        
    num_match = re.search(r'[\d,]+(?:\.\d+)?', clean)
    num_val = float(num_match.group(0).replace(',', '')) if num_match else None
    
    return {
        "raw": clean,
        "numeric_value": num_val,
        "currency": currency,
        "unit": unit,
        "is_percentage": is_percentage
    }

def detect_kpi_cards(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Detects KPI Cards and Metric Cards in the DOM.
    Looks for elements containing metric labels, formatted numbers, card classes, or flex boxes.
    """
    kpi_visuals = []
    card_candidates = soup.find_all(class_=re.compile(r'kpi|card|metric|stat|widget|tile|box|summary|indicator', re.I))
    
    if not card_candidates:
        # Fallback to div containers with strong text + number
        card_candidates = soup.find_all('div')

    seen_texts = set()

    for idx, card in enumerate(card_candidates):
        text_content = card.get_text(" ", strip=True)
        if not text_content or text_content in seen_texts or len(text_content) > 180:
            continue

        # Look for a number inside card
        numbers = re.findall(r'[$€£₹]?\s*\d+(?:\.\d+)?[MKBmkb%]?\b', text_content)
        if not numbers:
            continue

        # Extract title and value lines
        lines = [line.strip() for line in card.stripped_strings if line.strip()]
        if len(lines) >= 1:
            title = ""
            val_str = ""
            for line in lines:
                if re.search(r'[\d,]+(?:\.\d+)?', line) and not val_str:
                    val_str = line
                elif not title and not re.search(r'^\d+$', line):
                    title = line
            
            if not title:
                title = lines[0]
            if not val_str:
                val_str = lines[1] if len(lines) > 1 else lines[0]

            # Clean up duplicate titles or tag artifacts
            title = re.sub(r'\s+', ' ', title).strip()

            kpi_data = parse_kpi_value(val_str)
            seen_texts.add(text_content)

            kpi_visuals.append({
                "visual_id": f"kpi_{idx+1}",
                "visual_type": "kpi_card",
                "title": title,
                "subtitle": "",
                "raw_value": val_str,
                "parsed_value": kpi_data,
                "confidence": 0.92,
                "source_html": str(card)[:200]
            })

    return kpi_visuals

def detect_charts(soup: BeautifulSoup, script_contents: List[str]) -> List[Dict[str, Any]]:
    """
    Detects Chart visuals (Bar, Column, Line, Area, Pie, Donut, Scatter, Gauge, Treemap, Histogram).
    Integrates JS chart framework detector and SVG/Canvas DOM inspection.
    """
    charts = []
    js_charts = detect_chart_frameworks(soup, script_contents)
    
    # Also find containers labeled chart
    chart_containers = soup.find_all(class_=re.compile(r'chart|graph|plot|viz|canvas-container', re.I))
    
    for idx, container in enumerate(chart_containers):
        title_el = container.find(re.compile(r'h[1-6]|span|header|title|p|label|div', re.I))
        if not title_el:
            title_el = container.find_previous(re.compile(r'h[1-6]|header|title', re.I))
        
        title = title_el.get_text(strip=True) if title_el else f"Chart Visual {idx+1}"
        if len(title) > 60:
            title = f"Chart Visual {idx+1}"
        
        # Detect chart type hint from class or script
        class_str = " ".join(container.get("class", [])).lower()
        chart_type = "bar_chart"
        if "pie" in class_str or "donut" in class_str:
            chart_type = "pie_chart" if "pie" in class_str else "donut_chart"
        elif "line" in class_str or "trend" in class_str:
            chart_type = "line_chart"
        elif "area" in class_str:
            chart_type = "area_chart"
        elif "column" in class_str:
            chart_type = "column_chart"
        elif "scatter" in class_str:
            chart_type = "scatter_chart"
        elif "gauge" in class_str:
            chart_type = "gauge"

        charts.append({
            "visual_id": f"chart_{idx+1}",
            "visual_type": chart_type,
            "title": title,
            "subtitle": "",
            "confidence": 0.88,
            "source_html": str(container)[:200]
        })

    # If JS frameworks were detected without explicit container elements
    if not charts and js_charts:
        for idx, jsc in enumerate(js_charts):
            raw_t = jsc.get("type", "bar")
            c_type = "bar_chart"
            if "line" in raw_t:
                c_type = "line_chart"
            elif "pie" in raw_t:
                c_type = "pie_chart"
            elif "doughnut" in raw_t or "donut" in raw_t:
                c_type = "donut_chart"
            elif "area" in raw_t:
                c_type = "area_chart"
            elif "scatter" in raw_t:
                c_type = "scatter_chart"

            charts.append({
                "visual_id": f"js_chart_{idx+1}",
                "visual_type": c_type,
                "title": f"{c_type.replace('_', ' ').title()} ({jsc['framework']})",
                "subtitle": "",
                "confidence": jsc.get("confidence", 0.85),
                "source_html": f"Framework: {jsc['framework']}"
            })

    return charts

def detect_tables(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Detects HTML Table and Matrix components."""
    tables = []
    tbl_elements = soup.find_all('table')
    for idx, tbl in enumerate(tbl_elements):
        headers = [th.get_text(strip=True) for th in tbl.find_all('th')]
        title_el = tbl.find_previous(re.compile(r'h[1-6]|div|span', re.I))
        title = title_el.get_text(strip=True) if title_el and len(title_el.get_text(strip=True)) < 50 else f"Table Visual {idx+1}"
        
        tables.append({
            "visual_id": f"table_{idx+1}",
            "visual_type": "table",
            "title": title,
            "headers": headers,
            "column_count": len(headers),
            "confidence": 0.95,
            "source_html": str(tbl)[:200]
        })
    return tables

def detect_filters(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Detects Slicers, Dropdowns, Date Selectors, and Checkbox Filters."""
    filters = []
    
    # 1. Dropdown Select tags
    selects = soup.find_all('select')
    for idx, s in enumerate(selects):
        name = s.get('name') or s.get('id') or f"Slicer {idx+1}"
        label_el = soup.find('label', {'for': s.get('id')})
        title = label_el.get_text(strip=True) if label_el else name.replace('_', ' ').title()
        
        filters.append({
            "visual_id": f"filter_{idx+1}",
            "visual_type": "slicer",
            "title": title,
            "filter_type": "dropdown",
            "confidence": 0.90,
            "source_html": str(s)[:150]
        })
        
    # 2. Date inputs
    date_inputs = soup.find_all('input', {'type': 'date'})
    for idx, d in enumerate(date_inputs):
        name = d.get('name') or d.get('id') or f"Date Filter {idx+1}"
        label_el = soup.find('label', {'for': d.get('id')})
        title = label_el.get_text(strip=True) if label_el else "Order Date"
        
        filters.append({
            "visual_id": f"date_filter_{idx+1}",
            "visual_type": "date_slicer",
            "title": title,
            "filter_type": "date_range",
            "confidence": 0.92,
            "source_html": str(d)[:150]
        })
        
    return filters

def detect_text_boxes(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Detects Dashboard Titles, Subtitles, and Text Blocks."""
    text_visuals = []
    h1_tags = soup.find_all('h1')
    for idx, h1 in enumerate(h1_tags):
        text_visuals.append({
            "visual_id": f"title_{idx+1}",
            "visual_type": "title",
            "title": h1.get_text(strip=True),
            "text": h1.get_text(strip=True),
            "confidence": 0.98,
            "source_html": str(h1)[:150]
        })
    return text_visuals

def analyze_html_dashboard(html_content: str) -> List[Dict[str, Any]]:
    """
    Main entry point for HTML Dashboard analysis.
    Extracts all visual components (KPIs, Charts, Tables, Filters, Text) and assigns layout coordinates.
    """
    soup = parse_dom(html_content)
    script_contents = find_script_blocks(soup)

    kpis = detect_kpi_cards(soup)
    charts = detect_charts(soup, script_contents)
    tables = detect_tables(soup)
    filters = detect_filters(soup)
    texts = detect_text_boxes(soup)

    all_visuals = kpis + charts + tables + filters + texts
    
    # If no visuals detected at all, create fallback general visual
    if not all_visuals:
        log_event("html", "No explicit visuals detected; creating fallback overview visual", "WARNING")
        all_visuals.append({
            "visual_id": "overview_visual_1",
            "visual_type": "table",
            "title": "Dashboard Overview",
            "confidence": 0.50,
            "source_html": "Fallback visual"
        })

    all_visuals_with_layout = assign_layout_coordinates(all_visuals)
    log_event("html", f"Detected {len(all_visuals_with_layout)} visual components in HTML dashboard.")
    return all_visuals_with_layout
