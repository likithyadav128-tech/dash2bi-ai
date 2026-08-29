import unittest
from src.dax.measure_generator import generate_dax_formula, generate_dax_for_mapped_visuals
from src.dax.dax_validator import validate_dax_formula

class TestDAX(unittest.TestCase):
    def test_generate_dax_sum(self):
        dax = generate_dax_formula("Total Sales", "Orders", "Sales", "SUM")
        self.assertIn("Total Sales = ", dax)
        self.assertIn("SUM('Orders'[Sales])", dax)

    def test_generate_dax_divide(self):
        dax = generate_dax_formula("Profit Margin", "Orders", None, "DIVIDE", "Profit", "Sales")
        self.assertIn("Profit Margin = ", dax)
        self.assertIn("DIVIDE(", dax)
        self.assertIn("SUM('Orders'[Profit])", dax)
        self.assertIn("SUM('Orders'[Sales])", dax)

    def test_validate_dax(self):
        dax = "Total Sales = \nSUM('Orders'[Sales])"
        valid, errors = validate_dax_formula(dax, ["Orders"], ["Sales", "Profit"])
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_validate_invalid_dax(self):
        dax = "Total Sales = \nSUM('InvalidTable'[NonExistentCol])"
        valid, errors = validate_dax_formula(dax, ["Orders"], ["Sales", "Profit"])
        self.assertFalse(valid)
        self.assertEqual(len(errors), 2)

if __name__ == '__main__':
    unittest.main()
