"""
Unit tests for Auto Visual Generator module.
"""

import unittest
from src.data.auto_visual_generator import auto_generate_visuals

class TestAutoVisualGenerator(unittest.TestCase):

    def test_auto_generate_visuals(self):
        table_name = "covid19_cleaned"
        cols = [
            {"original_name": "Sno", "data_type": "int64", "role": "Identifier"},
            {"original_name": "Date", "data_type": "string", "role": "Date"},
            {"original_name": "State/UnionTerritory", "data_type": "string", "role": "Dimension"},
            {"original_name": "ConfirmedIndianNational", "data_type": "int64", "role": "Measure"},
            {"original_name": "ConfirmedForeignNational", "data_type": "int64", "role": "Measure"},
            {"original_name": "Cured", "data_type": "int64", "role": "Measure"},
            {"original_name": "Deaths", "data_type": "int64", "role": "Measure"},
        ]

        html_vis, mapped_vis = auto_generate_visuals(table_name, cols)
        
        self.assertGreaterEqual(len(html_vis), 8)
        self.assertEqual(len(html_vis), len(mapped_vis))
        
        # Check KPI cards
        kpi_cards = [v for v in mapped_vis if v["powerbi_type"] == "card"]
        self.assertEqual(len(kpi_cards), 4)

        # Check ready status
        ready_count = sum(1 for v in mapped_vis if v["status"] == "READY")
        self.assertEqual(ready_count, len(mapped_vis))

if __name__ == '__main__':
    unittest.main()
