"""Main EFSEngine Orchestrator for the EFS™ Assessment Framework.

Executes the deterministic EFS assessment pipeline:
Validated Financial Data
        ↓
Variable Calculation (95 variables)
        ↓
Established Models (5 models)
        ↓
Variable Scoring (0, 25, 50, 75, 100 bands)
        ↓
Pillar Aggregation (7 pillars)
        ↓
Overall EFS Score (Calibration Pending)
        ↓
Forensic Rule Engine (110 rules)
        ↓
Confidence Engine
        ↓
Structured Assessment JSON & Audit Trail
"""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.calculations.efs.confidence_engine import ConfidenceEngine
from app.calculations.efs.explainability_engine import ExplainabilityEngine
from app.calculations.efs.interfaces.base import IEFSEngine
from app.calculations.efs.methodology_loader import MethodologyLoader
from app.calculations.efs.models.domain import (
    AuditTrail,
    EFSExecutionResult,
    EFSInputVariables,
    EFSOverallResult,
)
from app.calculations.efs.models.established_models import EstablishedModelsEvaluator
from app.calculations.efs.pillars.registry import PillarEngineRegistry
from app.calculations.efs.rules.engine import ForensicRuleEngine
from app.calculations.efs.scoring_engine import ScoringEngine
from app.calculations.efs.validation_layer import ValidationLayer
from app.calculations.efs.variable_engine import VariableCalculationEngine

logger = logging.getLogger(__name__)


class EFSEngine(IEFSEngine):
    """Main methodology-driven deterministic EFS Engine orchestrator."""

    def __init__(
        self,
        methodology_loader: Optional[MethodologyLoader] = None,
        validation_layer: Optional[ValidationLayer] = None,
        variable_engine: Optional[VariableCalculationEngine] = None,
        established_evaluator: Optional[EstablishedModelsEvaluator] = None,
        rule_engine: Optional[ForensicRuleEngine] = None,
        pillar_registry: Optional[PillarEngineRegistry] = None,
        scoring_engine: Optional[ScoringEngine] = None,
        confidence_engine: Optional[ConfidenceEngine] = None,
        explainability_engine: Optional[ExplainabilityEngine] = None,
    ) -> None:
        self.methodology_loader = methodology_loader or MethodologyLoader()
        self.validation_layer = validation_layer or ValidationLayer()
        self.variable_engine = variable_engine or VariableCalculationEngine()
        self.established_evaluator = established_evaluator or EstablishedModelsEvaluator()
        self.rule_engine = rule_engine or ForensicRuleEngine()
        self.pillar_registry = pillar_registry or PillarEngineRegistry()
        self.scoring_engine = scoring_engine or ScoringEngine()
        self.confidence_engine = confidence_engine or ConfidenceEngine()
        self.explainability_engine = explainability_engine or ExplainabilityEngine()

    def run(
        self, analysis_id: str, input_payload: Dict[str, Any]
    ) -> EFSExecutionResult:
        """Executes full methodology-driven EFS pipeline deterministically."""
        start_time = time.perf_counter()
        asm_id = f"efs_asm_{uuid.uuid4().hex[:12]}"
        target_version = input_payload.get("methodology_version", "1.0")

        logger.info("Starting deterministic EFS Engine assessment ID=%s for analysis_id=%s (methodology v%s)", asm_id, analysis_id, target_version)

        # 1. Load Methodology dynamically
        methodology = self.methodology_loader.load(version=target_version)

        # 2. Extract input flags and variables
        stmt_flags = input_payload.get(
            "statement_flags",
            {
                "has_cash_flow_statement": True,
                "has_balance_sheet": True,
                "has_income_statement": True,
            },
        )

        variables_input = EFSInputVariables(
            analysis_id=analysis_id,
            validation_data=input_payload.get("validation_output"),
            feature_data=input_payload.get("feature_output"),
            ratio_data=input_payload.get("ratio_output"),
            beneish_data=input_payload.get("beneish_output"),
            statement_flags=stmt_flags or {},
            raw_variables=input_payload.get("raw_variables", {}),
            validation_completeness=input_payload.get("validation_completeness", 100.0),
            parser_confidence=input_payload.get("parser_confidence", 100.0),
            mapping_confidence=input_payload.get("mapping_confidence", 100.0),
            missing_financial_statements_count=input_payload.get("missing_financial_statements_count", 0),
            missing_variables_count=input_payload.get("missing_variables_count", 0),
            validation_errors_count=input_payload.get("validation_errors_count", 0),
        )

        # 3. Validation Layer Check
        self.validation_layer.evaluate_eligibility(
            variables=variables_input, methodology=methodology
        )

        # 4. Variable Calculation Engine (95 Variables)
        computed_vars_map = self.variable_engine.compute_variables(
            input_data=input_payload, methodology=methodology
        )

        # 5. Variable Scoring (0, 25, 50, 75, 100 bands)
        for var_id, v_res in computed_vars_map.items():
            if v_res["data_status"] == "AVAILABLE" and v_res["raw_value"] is not None:
                score, band = self.scoring_engine.score_variable(var_id, v_res["raw_value"])
                v_res["score"] = score
                v_res["scoring_band"] = band

        # Convert dicts into domain EFSVariableResult objects
        from app.calculations.efs.models.domain import EFSVariableResult
        domain_vars = {
            vid: EFSVariableResult(
                variable_id=v["variable_id"],
                variable_name=v["variable_name"],
                pillar=v["pillar"],
                raw_value=v["raw_value"],
                unit=v["unit"],
                score=v["score"],
                scoring_band=v["scoring_band"],
                data_status=v["data_status"],
                source_fields=v["source_fields"],
                calculation_status=v["calculation_status"],
            )
            for vid, v in computed_vars_map.items()
        }

        # 6. Established Models Evaluation (5 Models)
        established_models = self.established_evaluator.evaluate_all(
            raw_variables=input_payload.get("raw_variables", {}),
            feature_data=input_payload.get("feature_output", {}).get("dataset") if isinstance(input_payload.get("feature_output"), dict) else {},
        )

        # 7. Pillar Aggregation (7 Pillars)
        pillar_results = self.pillar_registry.calculate_all(
            computed_variables=domain_vars,
            variables_input=variables_input,
            methodology=methodology,
        )

        # 8. Overall EFS Score Aggregation Layer (Calibration Pending)
        overall_score = self.scoring_engine.aggregate_score(
            pillar_results=pillar_results, methodology=methodology
        )
        risk_level = self.scoring_engine.determine_manipulation_risk(
            overall_score=overall_score, methodology=methodology
        )

        # 9. Forensic Rule Engine (110 Rules)
        forensic_findings, rules_evaluated_cnt, rules_triggered_cnt = self.rule_engine.evaluate_rules(
            computed_vars=domain_vars,
            established_models=established_models,
            version=target_version,
        )

        # Extract Red Flags and Management Questions from triggered findings
        red_flags = [
            f"{f.rule_name}: {f.forensic_finding}"
            for f in forensic_findings
            if f.triggered
        ]

        management_questions = [
            f.question_for_management
            for f in forensic_findings
            if f.triggered and f.question_for_management
        ]
        # Deduplicate management questions
        management_questions = list(dict.fromkeys(management_questions))

        # 10. Multi-Factor Confidence Engine
        total_eval = len(domain_vars)
        total_avail = sum(1 for v in domain_vars.values() if v.data_status == "AVAILABLE")
        models_avail = sum(1 for m in established_models.values() if m.get("status") == "COMPLETED")

        confidence_res = self.confidence_engine.calculate_confidence(
            variables=variables_input,
            methodology=methodology,
            total_vars_evaluated=total_eval,
            total_vars_available=total_avail,
            models_available_count=models_avail,
        )

        overall_res = EFSOverallResult(
            score=overall_score,
            score_status="CALIBRATION_PENDING" if overall_score is None else "COMPLETED",
            risk_level=risk_level,
            confidence=confidence_res.confidence_score,
        )

        # 11. Explainability Engine Synthesis
        explainability = self.explainability_engine.generate_explainability(
            pillar_results=pillar_results,
            variables=variables_input,
            rule_findings=[],
        )

        # Calculation performance
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 12. Build Immutable Regulatory Audit Trail
        audit_trail = AuditTrail(
            assessment_id=asm_id,
            analysis_id=analysis_id,
            efs_version=methodology.efs_version,
            scoring_version="1.0",
            rulebook_version="1.0",
            engine_version="1.0.0",
            timestamp=datetime.now(timezone.utc).isoformat(),
            variables_evaluated=total_eval,
            variables_available=total_avail,
            rules_evaluated=rules_evaluated_cnt,
            rules_triggered=rules_triggered_cnt,
            calculation_time_ms=total_time_ms,
        )

        logger.info(
            "EFS Engine pipeline completed for analysis_id=%s in %.2f ms. Score Status=%s, Rules Triggered=%d/%d",
            analysis_id,
            total_time_ms,
            overall_res.score_status,
            rules_triggered_cnt,
            rules_evaluated_cnt,
        )

        return EFSExecutionResult(
            assessment_id=asm_id,
            analysis_id=analysis_id,
            efs_version=methodology.efs_version,
            status="COMPLETED",
            overall=overall_res,
            pillars=pillar_results,
            established_models=established_models,
            forensic_findings=forensic_findings,
            red_flags=red_flags,
            management_questions=management_questions,
            limitations=confidence_res.limitations,
            audit_trail=audit_trail,
            explainability=explainability,
        )
