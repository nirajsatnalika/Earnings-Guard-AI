"""Unit Test Suite for Calibration-Pending Architecture, Determinism, and Audit Trail.

Verifies:
1. Calibration-Pending architecture (overall score == null, risk_level == null, pillar score == null while component data exists)
2. 10-run Determinism (identical output across 10 runs with identical inputs)
3. Regulatory Audit Trail metadata consistency
"""

import os
import sys
import unittest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.calculations.efs.engine import EFSEngine


class TestCalibrationAndDeterminism(unittest.TestCase):
    """Unit test suite for Calibration-Pending, Determinism, and Audit Trail validation."""

    def setUp(self):
        self.engine = EFSEngine()
        self.mock_dataset = {
            "methodology_version": "1.0",
            "statement_flags": {
                "has_cash_flow_statement": True,
                "has_balance_sheet": True,
                "has_income_statement": True,
            },
            "raw_variables": {
                "revenue": 1000000.0,
                "prior_revenue": 800000.0,
                "receivables": 200000.0,
                "prior_receivables": 120000.0,
                "cfo": 120000.0,
                "pat": 90000.0,
                "cogs": 600000.0,
                "inventory": 140000.0,
                "payables": 80000.0,
                "total_assets": 1200000.0,
                "prior_total_assets": 1000000.0,
                "MODEL01": -2.15,
                "MODEL02": 0.03,
                "MODEL03": 3.10,
                "MODEL04": 8,
                "MODEL05": 0.05,
            },
        }

    def test_01_calibration_pending_architecture(self):
        """1. Verify overall.score == null, overall.risk_level == null, pillar.score == null when weights are TBD."""
        res = self.engine.run("calib_test_01", self.mock_dataset)

        # Overall level checks
        self.assertIsNone(res.overall.score, "overall score must be null while calibration is pending")
        self.assertIsNone(res.overall.risk_level, "overall risk_level must be null while calibration is pending")
        self.assertEqual(res.overall.score_status, "CALIBRATION_PENDING")

        # Pillar level checks
        for pillar in res.pillars:
            self.assertIsNone(pillar.pillar_score, "pillar_score must be null while calibration is pending")
            self.assertEqual(pillar.status, "CALIBRATION_PENDING")

        # Assert sub-components exist and are populated
        self.assertGreater(len(res.pillars), 0)
        self.assertIsNotNone(res.established_models)
        self.assertIn("beneish_m_score", res.established_models)
        self.assertGreater(len(res.forensic_findings), 0)
        self.assertGreater(res.overall.confidence, 0.0)
        self.assertIsNotNone(res.audit_trail)

    def test_02_10_run_determinism(self):
        """2. Run identical input 10 times and assert identical numerical outputs."""
        results = []
        for i in range(10):
            res = self.engine.run("determinism_analysis_100", self.mock_dataset)
            results.append(res)

        first = results[0]

        for idx, current in enumerate(results[1:], start=2):
            self.assertEqual(first.status, current.status, f"Status mismatch on run {idx}")
            self.assertEqual(first.overall.score, current.overall.score, f"Overall score mismatch on run {idx}")
            self.assertEqual(first.overall.score_status, current.overall.score_status, f"Score status mismatch on run {idx}")
            self.assertEqual(first.overall.confidence, current.overall.confidence, f"Confidence mismatch on run {idx}")

            # Models check
            self.assertEqual(
                first.established_models["beneish_m_score"]["score"],
                current.established_models["beneish_m_score"]["score"],
                f"Beneish M-Score mismatch on run {idx}"
            )
            self.assertEqual(
                first.established_models["altman_z_score"]["score"],
                current.established_models["altman_z_score"]["score"],
                f"Altman Z-Score mismatch on run {idx}"
            )

            # Rule findings check
            self.assertEqual(
                len(first.forensic_findings),
                len(current.forensic_findings),
                f"Rule findings count mismatch on run {idx}"
            )
            first_triggered = [f.rule_id for f in first.forensic_findings if f.triggered]
            curr_triggered = [f.rule_id for f in current.forensic_findings if f.triggered]
            self.assertEqual(first_triggered, curr_triggered, f"Triggered rules mismatch on run {idx}")

    def test_03_audit_trail_consistency(self):
        """3. Verify presence and internal consistency of all audit trail metadata."""
        res = self.engine.run("audit_test_03", self.mock_dataset)
        audit = res.audit_trail

        self.assertIsNotNone(audit.assessment_id)
        self.assertTrue(audit.assessment_id.startswith("efs_asm_"))
        self.assertEqual(audit.analysis_id, "audit_test_03")
        self.assertEqual(audit.efs_version, "1.0")
        self.assertEqual(audit.scoring_version, "1.0")
        self.assertEqual(audit.rulebook_version, "1.0")
        self.assertEqual(audit.engine_version, "1.0.0")
        self.assertIsNotNone(audit.timestamp)

        self.assertEqual(audit.variables_evaluated, 95)
        self.assertGreater(audit.variables_available, 0)
        self.assertLessEqual(audit.variables_available, 95)
        self.assertEqual(audit.rules_evaluated, 110)
        self.assertGreaterEqual(audit.rules_triggered, 0)
        self.assertGreaterEqual(audit.calculation_time_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
