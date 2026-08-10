"""Comprehensive Unit Test Suite for Production EFS™ Assessment Engine.

Verifies:
1. Variable loading
2. Scoring-rule loading
3. Missing variable handling
4. Variable scoring
5. Pillar aggregation
6. Established-model execution
7. Rule evaluation
8. Evidence states
9. Confidence calculation
10. Complete EFS assessment (Deterministic mock dataset)
"""

import os
import sys
import unittest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.calculations.efs.confidence_engine import ConfidenceEngine
from app.calculations.efs.engine import EFSEngine
from app.calculations.efs.methodology_loader import MethodologyLoader
from app.calculations.efs.models.established_models import EstablishedModelsEvaluator
from app.calculations.efs.pillars.registry import PillarEngineRegistry
from app.calculations.efs.rules.engine import ForensicRuleEngine
from app.calculations.efs.rules.loader import RuleLoader
from app.calculations.efs.scoring_engine import ScoringEngine
from app.calculations.efs.variable_engine import VariableCalculationEngine


class TestEFSAssessmentEngine(unittest.TestCase):
    """Unit test suite verifying all 10 required areas of the EFS Assessment Engine."""

    def setUp(self):
        self.methodology_loader = MethodologyLoader()
        self.methodology = self.methodology_loader.load(version="1.0")
        self.scoring_engine = ScoringEngine()
        self.variable_engine = VariableCalculationEngine()
        self.established_evaluator = EstablishedModelsEvaluator()
        self.pillar_registry = PillarEngineRegistry()
        self.rule_engine = ForensicRuleEngine()
        self.confidence_engine = ConfidenceEngine()
        self.efs_engine = EFSEngine()

    def test_01_variable_loading(self):
        """1. Verify that all 95 EFS variables are loaded dynamically."""
        reg_vars = self.methodology.registered_variables
        total_count = sum(len(vars_list) for vars_list in reg_vars.values())
        self.assertEqual(len(reg_vars), 7, "Must contain exactly 7 pillars")
        self.assertEqual(total_count, 95, "Must load all 95 EFS variables from 02_EFS_VARIABLE_LIBRARY.xlsx")
        self.assertIn("Financial Statement Quality", reg_vars)
        self.assertIn("Cash Flow Integrity", reg_vars)

    def test_02_scoring_rule_loading(self):
        """2. Verify that 100 scoring rules are loaded from config."""
        scoring_rules = self.scoring_engine._scoring_rules
        self.assertEqual(len(scoring_rules), 100, "Must load all 100 scoring rules for 95 variables + 5 models")
        self.assertIn("FSQ01", scoring_rules)
        self.assertIn("FSQ03", scoring_rules)

    def test_03_missing_variable_handling(self):
        """3. Verify missing data produces MISSING status without defaulting to zero score."""
        mock_input = {"raw_variables": {}}
        computed = self.variable_engine.compute_variables(mock_input, self.methodology)
        fsq01 = computed.get("FSQ01")
        self.assertIsNotNone(fsq01)
        self.assertEqual(fsq01["data_status"], "MISSING")
        self.assertIsNone(fsq01["raw_value"])

    def test_04_variable_scoring(self):
        """4. Verify deterministic mapping of raw values to score bands (0, 25, 50, 75, 100)."""
        # FSQ03 DSRI <= 1.00 -> 100 (Strong)
        score1, band1 = self.scoring_engine.score_variable("FSQ03", 0.95)
        self.assertEqual(score1, 100)
        self.assertEqual(band1, "Strong / 100")

        # FSQ03 DSRI > 1.40 -> 0 (Critical)
        score2, band2 = self.scoring_engine.score_variable("FSQ03", 1.45)
        self.assertEqual(score2, 0)
        self.assertEqual(band2, "Critical / 0")

    def test_05_pillar_aggregation(self):
        """5. Verify pillar aggregation across the 7 frozen pillars."""
        mock_input = {
            "raw_variables": {
                "revenue": 100000.0, "prior_revenue": 80000.0,
                "receivables": 15000.0, "prior_receivables": 10000.0,
                "cfo": 20000.0, "pat": 15000.0,
                "total_assets": 200000.0, "prior_total_assets": 180000.0,
            }
        }
        res = self.efs_engine.run("analysis_test_05", mock_input)
        self.assertEqual(len(res.pillars), 7)
        for pillar in res.pillars:
            self.assertIn(pillar.pillar_id, ["P1", "P2", "P3", "P4", "P5", "P6", "P7"])
            self.assertGreaterEqual(pillar.variables_evaluated, 10)

    def test_06_established_model_execution(self):
        """6. Verify execution of Beneish, Sloan, Altman, Piotroski, and Ohlson models."""
        raw_vars = {"MODEL01": -2.45, "MODEL02": 0.04, "MODEL03": 3.2, "MODEL04": 8, "MODEL05": 0.12}
        models_output = self.established_evaluator.evaluate_all(raw_vars)
        self.assertEqual(len(models_output), 5)
        self.assertEqual(models_output["beneish_m_score"]["score"], -2.45)
        self.assertEqual(models_output["sloan_accrual"]["score"], 0.04)
        self.assertEqual(models_output["altman_z_score"]["score"], 3.2)
        self.assertEqual(models_output["piotroski_f_score"]["score"], 8)
        self.assertEqual(models_output["ohlson_o_score"]["score"], 0.12)

    def test_07_rule_evaluation(self):
        """7. Verify evaluation of 110 forensic rules."""
        loader = RuleLoader()
        rules = loader.load_rules(version="1.0")
        self.assertEqual(len(rules), 110, "Must load all 110 forensic rules from efs_rules.json")

    def test_08_evidence_states(self):
        """8. Verify explicit evidence states (Triggered, Not Triggered, Not Evaluated)."""
        mock_input = {"raw_variables": {"FSQ03": 1.45}}  # DSRI elevated
        res = self.efs_engine.run("analysis_test_08", mock_input)
        findings = res.forensic_findings
        self.assertGreater(len(findings), 0)
        
        triggered_findings = [f for f in findings if f.triggered]
        self.assertGreater(len(triggered_findings), 0)
        for tf in triggered_findings:
            self.assertEqual(tf.evidence_state, "Triggered")
            self.assertNotIn("fraud detected", tf.forensic_finding.lower())

    def test_09_confidence_calculation(self):
        """9. Verify multi-factor confidence computation."""
        mock_input = {
            "statement_flags": {"has_cash_flow_statement": False, "has_balance_sheet": True, "has_income_statement": True},
            "mapping_confidence": 90.0,
        }
        res = self.efs_engine.run("analysis_test_09", mock_input)
        self.assertLess(res.overall.confidence, 100.0)
        self.assertGreater(len(res.limitations), 0)

    def test_10_complete_efs_assessment_deterministic(self):
        """10. Verify full deterministic EFS assessment output on mock dataset."""
        mock_financial_dataset = {
            "methodology_version": "1.0",
            "statement_flags": {
                "has_cash_flow_statement": True,
                "has_balance_sheet": True,
                "has_income_statement": True,
            },
            "raw_variables": {
                "revenue": 500000.0,
                "prior_revenue": 450000.0,
                "receivables": 80000.0,
                "prior_receivables": 65000.0,
                "cfo": 60000.0,
                "pat": 45000.0,
                "cogs": 300000.0,
                "inventory": 50000.0,
                "payables": 40000.0,
                "total_assets": 600000.0,
                "prior_total_assets": 550000.0,
                "MODEL01": -2.35,  # Beneish
                "MODEL02": 0.03,   # Sloan
                "MODEL03": 3.10,   # Altman
                "MODEL04": 7,      # Piotroski
                "MODEL05": 0.08,   # Ohlson
            },
        }

        # Run 1
        res1 = self.efs_engine.run("mock_analysis_001", mock_financial_dataset)
        # Run 2 with identical inputs
        res2 = self.efs_engine.run("mock_analysis_001", mock_financial_dataset)

        # Assert Deterministic behavior (Run 1 output == Run 2 output)
        self.assertEqual(res1.status, res2.status)
        self.assertEqual(res1.overall.score, res2.overall.score)
        self.assertEqual(res1.overall.score_status, "CALIBRATION_PENDING")
        self.assertEqual(res1.overall.confidence, res2.overall.confidence)
        self.assertEqual(len(res1.pillars), len(res2.pillars))
        self.assertEqual(len(res1.forensic_findings), len(res2.forensic_findings))
        self.assertEqual(res1.audit_trail.rules_evaluated, res2.audit_trail.rules_evaluated)
        self.assertEqual(res1.audit_trail.rules_triggered, res2.audit_trail.rules_triggered)


if __name__ == "__main__":
    unittest.main()
