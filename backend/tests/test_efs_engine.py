"""Comprehensive unit test suite for Methodology-Driven EFS™ Engine Framework."""

import os
import sys
import unittest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.calculations.efs import (
    EFSEngine,
    EFSRequest,
    EFSResponse,
    MethodologyLoader,
    ValidationLayer,
)


class TestMethodologyDrivenEFSEngine(unittest.TestCase):
    """Test suite verifying methodology loading, variable traceability, audit trails, and execution."""

    def test_methodology_loader_json_parsing(self):
        """Verify that MethodologyLoader successfully parses JSON config files."""
        loader = MethodologyLoader()
        config = loader.load(version="1.0")

        self.assertEqual(config.efs_version, "1.0")
        self.assertEqual(len(config.pillar_weights), 7)
        self.assertAlmostEqual(sum(config.pillar_weights.values()), 1.0, places=3)
        self.assertIn("cash_flow_integrity", config.sub_variable_weights)
        self.assertIn("financial_statement_quality", config.registered_variables)

    def test_efs_engine_full_pipeline_execution(self):
        """Verify complete engine execution with audit trail, traceability, and 6 explainability categories."""
        engine = EFSEngine()

        mock_payload = {
            "methodology_version": "1.0",
            "validation_output": {"status": "success", "issues": []},
            "feature_output": {"status": "computed", "dataset": {"metric_1": 1.5}},
            "ratio_output": {"status": "computed", "ratios": []},
            "beneish_output": {"status": "computed", "m_score": -2.5},
            "statement_flags": {
                "has_cash_flow_statement": True,
                "has_balance_sheet": True,
                "has_income_statement": True,
            },
        }

        result = engine.run(analysis_id="test_analysis_123", input_payload=mock_payload)

        # 1. Audit Trail Assertions
        self.assertEqual(result.analysis_id, "test_analysis_123")
        self.assertEqual(result.efs_version, "1.0")
        self.assertTrue(result.audit_trail.execution_id.startswith("efs_exec_"))
        self.assertEqual(result.audit_trail.efs_version, "1.0")
        self.assertEqual(result.audit_trail.engine_version, "1.0.0")
        self.assertIn("validation", result.audit_trail.inputs_used)
        self.assertGreater(result.audit_trail.variables_used_count, 0)
        self.assertGreaterEqual(result.audit_trail.calculation_time_ms, 0.0)

        # 2. Overall & Confidence Assertions
        self.assertEqual(result.overall_score, 100.0)
        self.assertEqual(result.confidence, 100.0)
        self.assertEqual(result.manipulation_risk, "Low")

        # 3. Pillar Traceability Assertions
        self.assertEqual(len(result.pillar_scores), 7)
        for pillar in result.pillar_scores:
            self.assertEqual(pillar.status, "computed")
            self.assertGreater(len(pillar.variables_used), 0)
            self.assertGreater(len(pillar.variable_traceability), 0)
            for var_trace in pillar.variable_traceability:
                self.assertIsNotNone(var_trace.name)
                self.assertGreater(var_trace.weight, 0)

        # 4. Explainability 6-Category Assertions
        exp = result.explainability
        self.assertGreater(len(exp.observations), 0)
        self.assertGreater(len(exp.positive_drivers), 0)
        self.assertGreater(len(exp.negative_drivers), 0)
        self.assertIsInstance(exp.red_flags, list)
        self.assertGreater(len(exp.recommendations), 0)
        self.assertGreater(len(exp.questions_for_management), 0)

    def test_statement_ineligibility_handling(self):
        """Verify that missing Cash Flow Statement causes Cash Flow Integrity pillar to mark ineligible gracefully."""
        engine = EFSEngine()

        payload = {
            "statement_flags": {
                "has_cash_flow_statement": False,
                "has_balance_sheet": True,
                "has_income_statement": True,
            }
        }

        result = engine.run(analysis_id="missing_cfs_456", input_payload=payload)

        # Find Cash Flow Integrity pillar result
        cf_pillar = next(
            p for p in result.pillar_scores if p.canonical_key == "cash_flow_integrity"
        )

        self.assertEqual(cf_pillar.status, "ineligible")
        self.assertEqual(cf_pillar.score, 0.0)
        self.assertIn("Cash Flow Statement", cf_pillar.execution_metadata.variables_missing)
        # Confidence score should drop due to missing statement penalty
        self.assertLess(result.confidence, 100.0)

    def test_pydantic_response_schema_validation(self):
        """Verify that Pydantic EFSResponse schema validates engine output."""
        engine = EFSEngine()
        result = engine.run(analysis_id="schema_test_789", input_payload={})

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
        self.assertEqual(dump["analysis_id"], "schema_test_789")
        self.assertEqual(dump["efs_version"], "1.0")
        self.assertIn("audit_trail", dump)
        self.assertIn("variables_used_count", dump["audit_trail"])
        self.assertIn("variables_used", dump["pillar_scores"][0])
        self.assertIn("positive_drivers", dump["explainability"])


if __name__ == "__main__":
    unittest.main()
