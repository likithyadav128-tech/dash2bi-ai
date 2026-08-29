import unittest
from src.html.html_loader import load_html_dashboard
from src.html.visual_detector import analyze_html_dashboard

SAMPLE_HTML_PATH = "C:/Users/likit/.gemini/antigravity/scratch/dash2bi_ai/sample_data/sample_dashboard.html"

class TestHTML(unittest.TestCase):
    def test_parse_html_dashboard(self):
        with open(SAMPLE_HTML_PATH, "rb") as f:
            content = f.read()
        html_str = load_html_dashboard(content)
        visuals = analyze_html_dashboard(html_str)
        
        self.assertGreater(len(visuals), 0)
        kpis = [v for v in visuals if v["visual_type"] in ["kpi_card", "metric_card"]]
        charts = [v for v in visuals if "chart" in v["visual_type"]]
        tables = [v for v in visuals if v["visual_type"] == "table"]
        filters = [v for v in visuals if "filter" in v["visual_type"] or "slicer" in v["visual_type"]]
        
        self.assertGreaterEqual(len(kpis), 4)
        self.assertGreaterEqual(len(charts), 3)
        self.assertGreaterEqual(len(tables), 1)
        self.assertGreaterEqual(len(filters), 2)

if __name__ == '__main__':
    unittest.main()
