"""Unit test suite for the Financial Forensics Rule Engine."""

import os
import sys
import unittest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.calculations.efs import EFSEngine, EFSInputVariables, EFSResponse
from app.calculations.efs.rules import ForensicRuleEngine, RuleExecutor, RuleLoader


class TestFinancialForensicsRuleEngine(unittest.TestCase):
    """Test suite verifying forensic rule loading, evaluation logic, and pipeline integration."""

    def test_rule_loader_json_parsing(self):
        """Verify that RuleLoader loads forensic rules from efs_rules.json sorted by priority."""
        loader = RuleLoader()
        rules = loader.load_rules(version="1.0", only_enabled=True)

        self.assertGreater(len(rules), 0)
        # Verify priority sorting (descending)
        for i in range(len(rules) - 1):
            self.assertGreaterEqual(rules[i].priority, rules[i + 1].priority)

        # Check expected rule presence
        rule_ids = [r.rule_id for r in rules]
        self.assertIn("RULE_REV_REC_01", rule_ids)
        self.assertIn("RULE_CFO_PAT_01", rule_ids)

    def test_rule_executor_condition_evaluation(self):
        """Verify RuleExecutor condition evaluation logic against variable dataset."""
        rule_engine = ForensicRuleEngine()

        # Variable state triggering Receivables > Revenue Growth rule
        variables = EFSInputVariables(
            analysis_id="test_rule_01",
            raw_variables={
                "receivables_growth": 25.0,
                "revenue_growth": 8.0,
                "cfo_to_pat_ratio": 0.60,  # triggers RULE_CFO_PAT_01 (< 0.8)
            },
        )

        findings, summary = rule_engine.evaluate_rules(variables=variables, version="1.0")

        self.assertGreater(summary.rules_evaluated_count, 0)
        self.assertGreater(summary.rules_triggered_count, 0)

        triggered_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_REV_REC_01", triggered_ids)
        self.assertIn("RULE_CFO_PAT_01", triggered_ids)

        # Inspect finding attributes
        rev_finding = next(f for f in findings if f.rule_id == "RULE_REV_REC_01")
        self.assertEqual(rev_finding.category, "Revenue Recognition")
        self.assertEqual(rev_finding.severity, "Medium")
        self.assertIn("Receivables are increasing faster than revenue.", rev_finding.message)
        self.assertIsNotNone(rev_finding.recommendation)
        self.assertIsNotNone(rev_finding.question_for_management)
        self.assertIn("receivables_growth", rev_finding.variables_used)

    def test_efs_pipeline_integration_with_rules(self):
        """Verify EFSEngine integrates Rule Engine findings into 6-category Explainability and AuditTrail."""
        engine = EFSEngine()

        payload = {
            "raw_variables": {
                "receivables_growth": 30.0,
                "revenue_growth": 5.0,
            }
        }

        result = engine.run(analysis_id="pipeline_rule_test", input_payload=payload)

        # Audit trail assertions
        self.assertGreater(result.audit_trail.rules_evaluated_count, 0)
        self.assertGreater(result.audit_trail.rules_triggered_count, 0)

        # Explainability assertions
        exp = result.explainability
        self.assertGreater(len(exp.observations), 1)  # Includes rule observations
        self.assertGreater(len(exp.recommendations), 0)
        self.assertGreater(len(exp.questions_for_management), 0)

        # Verify Pydantic schema validation
        response = EFSResponse(
            analysis_id=result.analysis_id,
            efs_version=result.efs_version,
            overall_score=result.overall_score,
            confidence=result.confidence,
            manipulation_risk=result.manipulation_risk,
            audit_trail={
                "execution_id": result.audit_trail.execution_id,
                "timestamp": result.audit_trail.timestamp,
                "efs_version": result.audit_trail.efs_version,
                "engine_version": result.audit_trail.engine_version,
                "inputs_used": result.audit_trail.inputs_used,
                "variables_used_count": result.audit_trail.variables_used_count,
                "calculation_time_ms": result.audit_trail.calculation_time_ms,
                "rules_evaluated_count": result.audit_trail.rules_evaluated_count,
                "rules_triggered_count": result.audit_trail.rules_triggered_count,
            },
            pillar_scores=[
                {
                    "name": p.name,
                    "canonical_key": p.canonical_key,
                    "score": p.score,
                    "weight": p.weight,
                    "status": p.status,
                    "variables_used": p.variables_used,
                    "strengths": p.strengths,
                    "weaknesses": p.weaknesses,
                    "red_flags": p.red_flags,
                    "execution_metadata": {
                        "execution_time_ms": p.execution_metadata.execution_time_ms,
                        "variables_used": p.execution_metadata.variables_used,
                        "variables_missing": p.execution_metadata.variables_missing,
                        "variables_ignored": p.execution_metadata.variables_ignored,
                        "warnings": p.execution_metadata.warnings,
                    },
                    "variable_traceability": [
                        {
                            "name": vt.name,
                            "value": vt.value,
                            "weight": vt.weight,
                            "contribution": vt.contribution,
                            "status": vt.status,
                        }
                        for vt in p.variable_traceability
                    ],
                }
                for p in result.pillar_scores
            ],
            explainability={
                "observations": result.explainability.observations,
                "positive_drivers": result.explainability.positive_drivers,
                "negative_drivers": result.explainability.negative_drivers,
                "red_flags": result.explainability.red_flags,
                "recommendations": result.explainability.recommendations,
                "questions_for_management": result.explainability.questions_for_management,
            },
        )

        dump = response.model_dump()
        self.assertEqual(dump["analysis_id"], "pipeline_rule_test")
        self.assertGreater(dump["audit_trail"]["rules_triggered_count"], 0)


if __name__ == "__main__":
    unittest.main()
