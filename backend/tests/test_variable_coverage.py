"""Unit Test Suite for 95 Variable Coverage & Data Integrity.

Verifies:
- Normal input calculation for all 11 explicit fallback variables (FSQ01, FSQ02, FSQ03, FSQ04, CFI01, AQ01, WCH01, WCH04, WCH07, WCH10, BSI02)
- Zero denominator protection
- Missing input handling (never converted to zero score or zero value)
- Negative input handling
- Invalid type input handling
- Multi-year calculation
"""

import os
import sys
import unittest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.calculations.efs.methodology_loader import MethodologyLoader
from app.calculations.efs.variable_engine import VariableCalculationEngine


class TestVariableCoverage(unittest.TestCase):
    """Unit test suite verifying raw variable calculation edge cases and missing data protection."""

    def setUp(self):
        self.loader = MethodologyLoader()
        self.methodology = self.loader.load(version="1.0")
        self.engine = VariableCalculationEngine()

    def test_01_normal_input_calculation(self):
        """Verify calculation under normal numeric input for all 11 explicit fallback variables."""
        payload = {
            "raw_variables": {
                "revenue": 100000.0, "prior_revenue": 80000.0,
                "accounts_receivable": 20000.0, "prior_accounts_receivable": 12000.0,
                "cfo": 15000.0, "pat": 10000.0,
                "cogs": 60000.0, "inventory": 12000.0,
                "accounts_payable": 10000.0,
                "total_assets": 150000.0, "prior_total_assets": 120000.0,
            }
        }
        res = self.engine.compute_variables(payload, self.methodology)
        
        # 1. FSQ01: Revenue Growth = (100k - 80k) / 80k = 0.25 (25%)
        self.assertEqual(res["FSQ01"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["FSQ01"]["raw_value"], 0.25, places=4)

        # 2. FSQ02: AR Growth vs Revenue Growth = ((20k-12k)/12k - 0.25)*100 = (0.666667 - 0.25)*100 = 41.6667 pp
        self.assertEqual(res["FSQ02"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["FSQ02"]["raw_value"], 41.6667, places=3)

        # 3. FSQ03: DSRI = (20k/100k) / (12k/80k) = 0.20 / 0.15 = 1.333333
        self.assertEqual(res["FSQ03"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["FSQ03"]["raw_value"], 1.3333, places=3)

        # 4. FSQ04: CFO / Revenue = (15k / 100k) * 100 = 15%
        self.assertEqual(res["FSQ04"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["FSQ04"]["raw_value"], 15.0, places=4)

        # 5. CFI01: CFO / PAT = 15k / 10k = 1.5
        self.assertEqual(res["CFI01"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["CFI01"]["raw_value"], 1.5, places=4)

        # 6. AQ01: Total Accruals / Assets = (10k - 15k) / 150k = -0.033333
        self.assertEqual(res["AQ01"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["AQ01"]["raw_value"], -0.0333, places=3)

        # 7. WCH01: DSO = (20k / 100k) * 365 = 73 days
        self.assertEqual(res["WCH01"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["WCH01"]["raw_value"], 73.0, places=2)

        # 8. WCH04: DIO = (12k / 60k) * 365 = 73 days
        self.assertEqual(res["WCH04"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["WCH04"]["raw_value"], 73.0, places=2)

        # 9. WCH07: DPO = (10k / 60k) * 365 = 60.8333 days
        self.assertEqual(res["WCH07"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["WCH07"]["raw_value"], 60.8333, places=2)

        # 10. WCH10: CCC = 73 + 73 - 60.8333 = 85.1667 days
        self.assertEqual(res["WCH10"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["WCH10"]["raw_value"], 85.1667, places=2)

        # 11. BSI02: AQI / Asset Growth = 150k / 120k = 1.25
        self.assertEqual(res["BSI02"]["data_status"], "AVAILABLE")
        self.assertAlmostEqual(res["BSI02"]["raw_value"], 1.25, places=4)

    def test_02_zero_denominator_protection(self):
        """Verify zero denominator doesn't crash engine or produce Infinity/NaN."""
        payload = {
            "raw_variables": {
                "revenue": 0.0, "prior_revenue": 0.0,
                "accounts_receivable": 10000.0, "prior_accounts_receivable": 5000.0,
            }
        }
        res = self.engine.compute_variables(payload, self.methodology)
        fsq01 = res["FSQ01"]
        # Division by zero prior_revenue -> MISSING / None
        self.assertEqual(fsq01["data_status"], "MISSING")
        self.assertIsNone(fsq01["raw_value"])

    def test_03_missing_input_preserves_missing_status(self):
        """Verify missing input is NEVER silently converted to zero score or zero value."""
        payload = {"raw_variables": {}}
        res = self.engine.compute_variables(payload, self.methodology)
        
        for vid, vdata in res.items():
            self.assertEqual(vdata["data_status"], "MISSING")
            self.assertIsNone(vdata["raw_value"])
            self.assertIsNone(vdata["score"])
            self.assertEqual(vdata["calculation_status"], "INCOMPLETE")

    def test_04_negative_input_handling(self):
        """Verify negative inputs (e.g. negative net income or CFO) are computed correctly."""
        payload = {
            "raw_variables": {
                "cfo": -5000.0, "pat": -10000.0, "total_assets": 100000.0
            }
        }
        res = self.engine.compute_variables(payload, self.methodology)
        
        # CFI01: CFO / PAT = -5000 / -10000 = 0.5
        cfi01 = res["CFI01"]
        self.assertEqual(cfi01["data_status"], "AVAILABLE")
        self.assertAlmostEqual(cfi01["raw_value"], 0.5, places=4)

        # AQ01: Total Accruals / Assets = (-10000 - (-5000)) / 100000 = -5000 / 100000 = -0.05
        aq01 = res["AQ01"]
        self.assertEqual(aq01["data_status"], "AVAILABLE")
        self.assertAlmostEqual(aq01["raw_value"], -0.05, places=4)

    def test_05_invalid_input_type_handling(self):
        """Verify string / invalid inputs are handled gracefully without raising unhandled exception."""
        payload = {
            "raw_variables": {
                "revenue": "invalid_string_number",
                "prior_revenue": None
            }
        }
        res = self.engine.compute_variables(payload, self.methodology)
        self.assertEqual(res["FSQ01"]["data_status"], "MISSING")
        self.assertIsNone(res["FSQ01"]["raw_value"])

    def test_06_multi_year_input_calculation(self):
        """Verify multi-year index calculation (DSRI)."""
        payload = {
            "raw_variables": {
                "revenue": 200000.0, "prior_revenue": 150000.0,
                "accounts_receivable": 40000.0, "prior_accounts_receivable": 20000.0
            }
        }
        res = self.engine.compute_variables(payload, self.methodology)
        
        # DSRI = (40k / 200k) / (20k / 150k) = 0.20 / 0.133333 = 1.50
        fsq03 = res["FSQ03"]
        self.assertEqual(fsq03["data_status"], "AVAILABLE")
        self.assertAlmostEqual(fsq03["raw_value"], 1.50, places=4)


if __name__ == "__main__":
    unittest.main()
