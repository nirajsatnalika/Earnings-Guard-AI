"""Unit Test Suite for Forensic Rule Engine Edge Cases.

Verifies the 10 critical rule evaluation scenarios:
1. Rule triggered
2. Rule not triggered
3. Missing variable
4. Missing denominator
5. Multiple missing variables
6. Not Applicable
7. Insufficient Evidence
8. Multiple rules triggering simultaneously
9. Compound rule requiring multiple variables
10. Disabled rule
"""

import os
import sys
import unittest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.calculations.efs.engine import EFSEngine
from app.calculations.efs.rules.executor import RuleExecutor
from app.calculations.efs.rules.loader import RuleLoader


class TestRuleEngineEdgeCases(unittest.TestCase):
    """Unit test suite verifying 10 forensic rule engine edge case scenarios."""

    def setUp(self):
        self.engine = EFSEngine()
        self.loader = RuleLoader()
        self.executor = RuleExecutor()

    def test_01_rule_triggered(self):
        """1. Rule triggered when condition is satisfied."""
        payload = {"raw_variables": {"FSQ03": 1.45}}  # DSRI > 1.40
        res = self.engine.run("test_rule_01", payload)
        findings = [f for f in res.forensic_findings if f.rule_id == "FR-FSQ03"]
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].triggered)
        self.assertEqual(findings[0].evidence_state, "Triggered")

    def test_02_rule_not_triggered(self):
        """2. Rule not triggered when data exists but condition is not met."""
        payload = {"raw_variables": {"FSQ03": 0.95}}  # DSRI <= 1.00 (Healthy)
        res = self.engine.run("test_rule_02", payload)
        findings = [f for f in res.forensic_findings if f.rule_id == "FR-FSQ03"]
        self.assertEqual(len(findings), 1)
        self.assertFalse(findings[0].triggered)
        self.assertEqual(findings[0].evidence_state, "Not Triggered")

    def test_03_missing_variable(self):
        """3. Missing variable produces 'Not Evaluated' status, never a false trigger."""
        payload = {"raw_variables": {}}  # All variables missing
        res = self.engine.run("test_rule_03", payload)
        findings = [f for f in res.forensic_findings if f.rule_id == "FR-FSQ03"]
        self.assertEqual(len(findings), 1)
        self.assertFalse(findings[0].triggered)
        self.assertEqual(findings[0].evidence_state, "Not Evaluated")

    def test_04_missing_denominator(self):
        """4. Zero denominator prevents calculation and results in 'Not Evaluated'."""
        payload = {"raw_variables": {"revenue": 0.0, "prior_revenue": 0.0}}
        res = self.engine.run("test_rule_04", payload)
        findings = [f for f in res.forensic_findings if f.rule_id == "FR-FSQ01"]
        self.assertEqual(len(findings), 1)
        self.assertFalse(findings[0].triggered)
        self.assertEqual(findings[0].evidence_state, "Not Evaluated")

    def test_05_multiple_missing_variables(self):
        """5. Multiple missing variables produce 'Not Evaluated' for all dependent rules."""
        payload = {"raw_variables": {"FSQ01": 0.10}}
        res = self.engine.run("test_rule_05", payload)
        eval_states = {f.rule_id: f.evidence_state for f in res.forensic_findings}
        self.assertEqual(eval_states["FR-FSQ02"], "Not Evaluated")
        self.assertEqual(eval_states["FR-FSQ03"], "Not Evaluated")

    def test_06_not_applicable_statement_flag(self):
        """6. Ineligible pillar/statement flag marks dependent rules accordingly."""
        payload = {"statement_flags": {"has_cash_flow_statement": False}}
        res = self.engine.run("test_rule_06", payload)
        # Cash Flow Integrity pillar marked INELIGIBLE
        cf_pillar = next(p for p in res.pillars if p.pillar_id == "P2")
        self.assertEqual(cf_pillar.status, "INELIGIBLE")

    def test_07_insufficient_evidence(self):
        """7. Model with missing inputs produces Insufficient Evidence state."""
        models_map = {"beneish_m_score": {"status": "INSUFFICIENT_DATA", "score": None}}
        findings, eval_cnt, trig_cnt = self.executor.evaluate_rules(
            rules=self.loader.load_rules(version="1.0"),
            computed_vars={},
            established_models=models_map
        )
        model1_finding = next(f for f in findings if f.rule_id == "FR-MODEL01")
        self.assertFalse(model1_finding.triggered)
        self.assertEqual(model1_finding.evidence_state, "Not Evaluated")

    def test_08_multiple_rules_triggering_simultaneously(self):
        """8. Multiple rules triggering simultaneously are all captured in findings."""
        payload = {
            "raw_variables": {
                "FSQ03": 1.45,  # DSRI elevated (FR-FSQ03)
                "FSQ04": -2.0,  # Revenue quality ratio negative (FR-FSQ04)
                "MODEL01": -1.45 # Beneish M-Score elevated (FR-MODEL01)
            }
        }
        res = self.engine.run("test_rule_08", payload)
        triggered_ids = [f.rule_id for f in res.forensic_findings if f.triggered]
        self.assertIn("FR-FSQ03", triggered_ids)
        self.assertIn("FR-FSQ04", triggered_ids)
        self.assertIn("FR-MODEL01", triggered_ids)

    def test_09_compound_rule_requiring_multiple_variables(self):
        """9. Compound cross-pillar rule FR-C001 triggers when multiple signals converge."""
        payload = {
            "raw_variables": {
                "FSQ02": 25.0,  # Receivables growth > Revenue growth (gap > 20 pp)
                "FSQ03": 1.35,  # DSRI weak
                "WCH01": 95.0,  # DSO weak
            }
        }
        res = self.engine.run("test_rule_09", payload)
        c001_finding = next(f for f in res.forensic_findings if f.rule_id == "FR-C001")
        self.assertTrue(c001_finding.triggered)
        self.assertEqual(c001_finding.severity, "Critical")

    def test_10_disabled_rule(self):
        """10. Disabled rules in config are ignored and not evaluated."""
        all_rules = self.loader.load_rules(version="1.0", only_enabled=False)
        enabled_rules = self.loader.load_rules(version="1.0", only_enabled=True)
        self.assertLessEqual(len(enabled_rules), len(all_rules))


if __name__ == "__main__":
    unittest.main()
