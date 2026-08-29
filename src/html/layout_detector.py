"""
Layout Coordinate Detector for Dash2BI AI.
Maps HTML DOM positioning and flex/grid ordering into Power BI report canvas space (1280x720).
"""

from typing import Dict, Any, List

CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 720
PADDING = 15

def assign_layout_coordinates(visuals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Assigns grid-based x, y, width, height to detected visuals for Power BI canvas placement.
    Layout strategy:
    - KPIs at top row (y = 20, height = 110)
    - Filters next to KPIs or top-right
    - Charts in middle grid rows (y = 150+, height = 260)
    - Tables / Detail visuals at bottom (y = 430+, height = 260)
    """
    kpis = [v for v in visuals if v["visual_type"] in ["kpi_card", "metric_card"]]
    filters = [v for v in visuals if v["visual_type"] in ["filter", "date_filter", "slicer"]]
    charts = [v for v in visuals if "chart" in v["visual_type"]]
    tables = [v for v in visuals if v["visual_type"] in ["table", "matrix"]]
    texts = [v for v in visuals if v["visual_type"] in ["title", "subtitle", "text_box"]]

    current_y = 20

    # 1. Place Title / Header if present
    for t in texts:
        t["layout"] = {"x": 20, "y": current_y, "width": 1240, "height": 50}
        current_y += 60
        break

    # 2. Place KPI Cards in top row
    if kpis:
        num_kpis = len(kpis)
        kpi_width = max(180, min(300, (CANVAS_WIDTH - (num_kpis + 1) * PADDING) // num_kpis))
        for idx, k in enumerate(kpis):
            x = PADDING + idx * (kpi_width + PADDING)
            k["layout"] = {"x": x, "y": current_y, "width": kpi_width, "height": 110}
        current_y += 125

    # 3. Place Slicers / Filters
    if filters:
        num_filters = len(filters)
        filter_width = 220
        for idx, f in enumerate(filters):
            x = CANVAS_WIDTH - (idx + 1) * (filter_width + PADDING)
            f["layout"] = {"x": x, "y": 20, "width": filter_width, "height": 90}

    # 4. Place Charts in 2-column or 3-column grid
    if charts:
        num_charts = len(charts)
        if num_charts == 1:
            charts[0]["layout"] = {"x": PADDING, "y": current_y, "width": 1250, "height": 270}
            current_y += 285
        elif num_charts == 2:
            chart_width = (CANVAS_WIDTH - 3 * PADDING) // 2
            charts[0]["layout"] = {"x": PADDING, "y": current_y, "width": chart_width, "height": 270}
            charts[1]["layout"] = {"x": PADDING * 2 + chart_width, "y": current_y, "width": chart_width, "height": 270}
            current_y += 285
        else:
            chart_width = (CANVAS_WIDTH - 3 * PADDING) // 2
            for idx, c in enumerate(charts):
                row = idx // 2
                col = idx % 2
                x = PADDING + col * (chart_width + PADDING)
                y = current_y + row * (260 + PADDING)
                c["layout"] = {"x": x, "y": y, "width": chart_width, "height": 250}
            rows_used = (num_charts + 1) // 2
            current_y += rows_used * (250 + PADDING)

    # 5. Place Tables at bottom
    if tables:
        for idx, tbl in enumerate(tables):
            tbl["layout"] = {"x": PADDING, "y": current_y, "width": 1250, "height": 240}
            current_y += 255

    # Assign default layout for any unplaced visual
    for v in visuals:
        if "layout" not in v:
            v["layout"] = {"x": 20, "y": 20, "width": 300, "height": 200}

    return visuals
