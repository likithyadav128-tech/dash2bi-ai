import unittest
from src.mapping.field_mapper import map_label_to_dataset_field
from src.mapping.visual_mapper import map_all_visuals

class TestMapping(unittest.TestCase):
    def test_exact_field_mapping(self):
        dataset_cols = [
            {"original_name": "Sales", "role": "Measure"},
            {"original_name": "Profit", "role": "Measure"},
            {"original_name": "Region", "role": "Dimension"}
        ]
        col, score, match_type, _ = map_label_to_dataset_field("Sales", dataset_cols)
        self.assertEqual(col, "Sales")
        self.assertEqual(score, 1.00)
        self.assertEqual(match_type, "EXACT")

    def test_synonym_field_mapping(self):
        dataset_cols = [
            {"original_name": "Sales", "role": "Measure"},
            {"original_name": "Profit", "role": "Measure"}
        ]
        col, score, match_type, _ = map_label_to_dataset_field("Total Revenue", dataset_cols)
        self.assertEqual(col, "Sales")
        self.assertGreaterEqual(score, 0.85)
        self.assertEqual(match_type, "SYNONYM")

    def test_map_all_visuals(self):
        dataset_cols = [
            {"original_name": "Sales", "role": "Measure"},
            {"original_name": "Profit", "role": "Measure"},
            {"original_name": "Region", "role": "Dimension"}
        ]
        html_visuals = [
            {"visual_id": "kpi_1", "visual_type": "kpi_card", "title": "Total Sales"},
            {"visual_id": "chart_1", "visual_type": "bar_chart", "title": "Sales by Region"}
        ]
        mapped = map_all_visuals(html_visuals, dataset_cols)
        self.assertEqual(len(mapped), 2)
        self.assertEqual(mapped[0]["mapped_field"], "Sales")
        self.assertEqual(mapped[0]["powerbi_type"], "card")
        self.assertEqual(mapped[1]["powerbi_type"], "barChart")

if __name__ == '__main__':
    unittest.main()
