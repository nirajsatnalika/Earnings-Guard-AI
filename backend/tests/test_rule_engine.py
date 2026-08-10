"""Unit test suite for the Financial Forensics Rule Engine."""

import os
import sys
import unittest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.calculations.efs.engine import EFSEngine
from app.calculations.efs.rules import ForensicRuleEngine, RuleLoader


class TestFinancialForensicsRuleEngine(unittest.TestCase):
    """Test suite verifying forensic rule loading and evaluation logic."""

    def test_rule_loader_json_parsing(self):
        """Verify that RuleLoader loads all 110 forensic rules from efs_rules.json."""
        loader = RuleLoader()
        rules = loader.load_rules(version="1.0", only_enabled=True)

        self.assertEqual(len(rules), 110)
        rule_ids = [r["rule_id"] for r in rules]
        self.assertIn("FR-FSQ01", rule_ids)
        self.assertIn("FR-MODEL01", rule_ids)
        self.assertIn("FR-C001", rule_ids)

    def test_rule_executor_condition_evaluation(self):
        """Verify ForensicRuleEngine evaluation against computed variables."""
        engine = EFSEngine()

        payload = {
            "raw_variables": {
                "FSQ03": 1.45,  # DSRI elevated (>1.40)
                "FSQ01": 0.05,
            }
        }

        result = engine.run(analysis_id="rule_eval_test_01", input_payload=payload)

        self.assertGreater(result.audit_trail.rules_evaluated, 0)
        self.assertGreater(result.audit_trail.rules_triggered, 0)

        triggered = [f for f in result.forensic_findings if f.triggered]
        triggered_ids = [t.rule_id for t in triggered]
        self.assertIn("FR-FSQ03", triggered_ids)

        dsri_finding = next(f for f in triggered if f.rule_id == "FR-FSQ03")
        self.assertEqual(dsri_finding.severity, "Critical")
        self.assertEqual(dsri_finding.evidence_state, "Triggered")
        self.assertIn("DSRI", dsri_finding.rule_name)


if __name__ == "__main__":
    unittest.main()
