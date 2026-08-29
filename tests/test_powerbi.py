import unittest
import os
import tempfile
from src.powerbi.pbip_generator import create_pbip_project_folder
from src.powerbi.export_manager import package_pbip_as_zip

class TestPowerBI(unittest.TestCase):
    def test_create_pbip_folder(self):
        dataset_cols = [
            {"original_name": "Sales", "data_type": "double", "role": "Measure"},
            {"original_name": "Region", "data_type": "string", "role": "Dimension"}
        ]
        mapped_visuals = [
            {"visual_id": "kpi_1", "html_type": "kpi_card", "powerbi_type": "card", "title": "Total Sales", "mapped_field": "Sales", "layout": {"x": 20, "y": 20, "width": 200, "height": 100}}
        ]
        measures = [
            {"measure_name": "Total Sales", "table_name": "Orders", "column_name": "Sales", "aggregation": "SUM", "dax_formula": "Total Sales = SUM('Orders'[Sales])"}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = create_pbip_project_folder(
                project_name="TestReport",
                table_name="Orders",
                dataset_cols=dataset_cols,
                mapped_visuals=mapped_visuals,
                measures=measures,
                output_dir=temp_dir
            )
            
            self.assertTrue(os.path.exists(project_dir))
            self.assertTrue(os.path.exists(os.path.join(project_dir, "TestReport.pbip")))
            self.assertTrue(os.path.exists(os.path.join(project_dir, "TestReport.Report", "definition.pbir")))
            self.assertTrue(os.path.exists(os.path.join(project_dir, "TestReport.SemanticModel", "definition", "model.tmdl")))

            zip_bytes = package_pbip_as_zip(project_dir)
            self.assertGreater(len(zip_bytes), 100)

if __name__ == '__main__':
    unittest.main()
