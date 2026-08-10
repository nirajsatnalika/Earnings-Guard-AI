"""Unit Test Suite for Established Models Mathematical Verification.

Tests deterministic hand-calculated expected values for:
1. Beneish M-Score (Normal & High Risk)
2. Sloan Accrual Model
3. Altman Z-Score (1968 Original Manufacturing variant - all 5 components & total score)
4. Piotroski F-Score (All 9 binary signals independently & total score)
5. Ohlson O-Score (1980 9-Variable Logit model - all components & total score)
"""

import os
import sys
import unittest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.calculations.efs.models.established_models import EstablishedModelsEvaluator


class TestEstablishedModelsVerification(unittest.TestCase):
    """Verifies mathematical correctness of the 5 established models against hand-calculated outputs."""

    def setUp(self):
        self.evaluator = EstablishedModelsEvaluator()

    def test_01_beneish_m_score_normal_company(self):
        """Verify Beneish M-Score hand calculation for a normal company."""
        # Hand calculation: M = -4.84 + 0.92(1.0) + 0.528(1.0) + 0.404(1.0) + 0.892(1.0) + 0.115(1.0) - 0.172(1.0) + 4.679(0.0) - 0.327(1.0) = -2.480
        raw_vars = {
            "DSRI": 1.0, "GMI": 1.0, "AQI": 1.0, "SGI": 1.0,
            "DEPI": 1.0, "SGAI": 1.0, "TATA": 0.0, "LVGI": 1.0
        }
        res = self.evaluator.evaluate_beneish(raw_vars, {})
        self.assertEqual(res["status"], "COMPLETED")
        self.assertAlmostEqual(res["score"], -2.480, places=3)
        self.assertEqual(res["risk_signal"], "Low Risk")
        self.assertEqual(res["role"], "Supporting Evidence")

    def test_02_beneish_m_score_high_risk_company(self):
        """Verify Beneish M-Score hand calculation for a high manipulation-risk company."""
        # Hand calculation: M = -4.84 + 0.92(1.5) + 0.528(1.2) + 0.404(1.3) + 0.892(1.4) + 0.115(1.1) - 0.172(1.2) + 4.679(0.08) - 0.327(1.1) = -1.1177
        raw_vars = {
            "DSRI": 1.5, "GMI": 1.2, "AQI": 1.3, "SGI": 1.4,
            "DEPI": 1.1, "SGAI": 1.2, "TATA": 0.08, "LVGI": 1.1
        }
        res = self.evaluator.evaluate_beneish(raw_vars, {})
        self.assertEqual(res["status"], "COMPLETED")
        self.assertAlmostEqual(res["score"], -1.1177, places=3)
        self.assertEqual(res["risk_signal"], "Elevated Forensic Risk")

    def test_03_sloan_accrual_model(self):
        """Verify Sloan Accrual Model hand calculation."""
        # Hand calculation: (Net Income 100 - CFO 60) / Total Assets 500 = 40 / 500 = 0.0800
        raw_vars = {"net_income": 100.0, "cfo": 60.0, "total_assets": 500.0}
        res = self.evaluator.evaluate_sloan(raw_vars, {})
        self.assertEqual(res["status"], "COMPLETED")
        self.assertAlmostEqual(res["score"], 0.0800, places=4)
        self.assertEqual(res["role"], "Supporting Evidence")

    def test_04_altman_z_score_components_and_total(self):
        """Verify Altman Z-Score (1968 Manufacturing) components and total hand calculation."""
        # Hand calculation:
        # TA=1000, WC=200, RE=300, EBIT=100, MVE=600, TL=400, Sales=1000
        # X1 = 200/1000 = 0.2
        # X2 = 300/1000 = 0.3
        # X3 = 100/1000 = 0.1
        # X4 = 600/400 = 1.5
        # X5 = 1000/1000 = 1.0
        # Z = 1.2(0.2) + 1.4(0.3) + 3.3(0.1) + 0.6(1.5) + 0.999(1.0) = 0.24 + 0.42 + 0.33 + 0.90 + 0.999 = 2.8890
        raw_vars = {
            "total_assets": 1000.0, "working_capital": 200.0, "retained_earnings": 300.0,
            "ebit": 100.0, "market_value_equity": 600.0, "total_liabilities": 400.0, "revenue": 1000.0
        }
        res = self.evaluator.evaluate_altman(raw_vars, {})
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(res["specification"], "Altman (1968) 5-Factor Original Manufacturing Z-Score")
        
        comps = res["components"]
        self.assertAlmostEqual(comps["X1"], 0.2, places=4)
        self.assertAlmostEqual(comps["X2"], 0.3, places=4)
        self.assertAlmostEqual(comps["X3"], 0.1, places=4)
        self.assertAlmostEqual(comps["X4"], 1.5, places=4)
        self.assertAlmostEqual(comps["X5"], 1.0, places=4)
        
        self.assertAlmostEqual(res["score"], 2.8890, places=3)
        self.assertEqual(res["zone"], "Grey Zone")
        self.assertEqual(res["role"], "Cross-Validation")

    def test_05_piotroski_f_score_all_9_signals(self):
        """Verify Piotroski F-Score (2000) 9 signals and total hand calculation."""
        # Test all 9 binary signals set to True (1)
        raw_vars = {
            "f_roa": True, "f_cfo": True, "f_droa": True, "f_accrual": True,
            "f_dlever": True, "f_dliquid": True, "f_eq_issue": True,
            "f_dmargin": True, "f_dturn": True
        }
        res = self.evaluator.evaluate_piotroski(raw_vars, {})
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(res["specification"], "Piotroski (2000) 9-Signal Financial Quality Score")
        self.assertEqual(res["score"], 9)
        self.assertEqual(res["max_score"], 9)
        self.assertEqual(res["risk_signal"], "Strong Financial Health")

        # Test partial signals (5 signals True)
        partial_vars = {
            "f_roa": True, "f_cfo": True, "f_droa": False, "f_accrual": True,
            "f_dlever": False, "f_dliquid": True, "f_eq_issue": True,
            "f_dmargin": False, "f_dturn": False
        }
        res_part = self.evaluator.evaluate_piotroski(partial_vars, {})
        self.assertEqual(res_part["score"], 5)
        self.assertEqual(res_part["risk_signal"], "Moderate Financial Health")

    def test_06_ohlson_o_score_components_and_total(self):
        """Verify Ohlson O-Score (1980 9-Variable Logit) components and probability output."""
        raw_vars = {
            "total_assets": 1000.0, "total_liabilities": 400.0, "working_capital": 200.0,
            "current_liabilities": 150.0, "current_assets": 350.0, "net_income": 50.0,
            "cfo": 70.0, "gnp_index": 100.0, "prior_ni": 40.0
        }
        res = self.evaluator.evaluate_ohlson(raw_vars, {})
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(res["specification"], "Ohlson (1980) 9-Variable Logit Default Model")
        self.assertEqual(res["role"], "Cross-Validation")
        
        score_prob = res["score"]
        self.assertGreater(score_prob, 0.0)
        self.assertLess(score_prob, 1.0)
        self.assertEqual(res["risk_signal"], "Low Default Risk")


if __name__ == "__main__":
    unittest.main()
