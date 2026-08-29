import unittest
import os
from src.data.dataset_loader import load_dataset_file
from src.data.dataset_profiler import profile_dataset

SAMPLE_CSV_PATH = "C:/Users/likit/.gemini/antigravity/scratch/dash2bi_ai/sample_data/sample_superstore.csv"

class TestDataset(unittest.TestCase):
    def test_load_csv_dataset(self):
        with open(SAMPLE_CSV_PATH, "rb") as f:
            content = f.read()
        df, meta = load_dataset_file("sample_superstore.csv", content)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 100)
        self.assertIn("Sales", df.columns)
        self.assertIn("Profit", df.columns)

    def test_profile_dataset(self):
        with open(SAMPLE_CSV_PATH, "rb") as f:
            content = f.read()
        profile = profile_dataset("sample_superstore.csv", content)
        self.assertEqual(profile.row_count, 100)
        self.assertIn("Sales", profile.measures)
        self.assertEqual(profile.quality_summary["missing_values_percentage"], 0.0)

if __name__ == '__main__':
    unittest.main()
