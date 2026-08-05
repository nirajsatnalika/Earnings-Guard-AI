"""Main EFSEngine Orchestrator for the EFS™ Assessment Framework.

Executes the pipeline sequence:
Validation Layer -> Methodology Loader -> Forensic Rule Engine -> Pillar Engines -> Scoring Engine -> Confidence Engine -> Explainability Engine -> Structured Response.
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
)
from app.calculations.efs.pillars.registry import PillarEngineRegistry
from app.calculations.efs.rules.engine import ForensicRuleEngine
from app.calculations.efs.scoring_engine import ScoringEngine
from app.calculations.efs.validation_layer import ValidationLayer

logger = logging.getLogger(__name__)


class EFSEngine(IEFSEngine):
    """Main methodology-driven EFS Engine orchestrator."""

    def __init__(
        self,
        methodology_loader: Optional[MethodologyLoader] = None,
        validation_layer: Optional[ValidationLayer] = None,
        rule_engine: Optional[ForensicRuleEngine] = None,
        pillar_registry: Optional[PillarEngineRegistry] = None,
        scoring_engine: Optional[ScoringEngine] = None,
        explainability_engine: Optional[ExplainabilityEngine] = None,
        confidence_engine: Optional[ConfidenceEngine] = None,
    ) -> None:
        self.methodology_loader = methodology_loader or MethodologyLoader()
        self.validation_layer = validation_layer or ValidationLayer()
        self.rule_engine = rule_engine or ForensicRuleEngine()
        self.pillar_registry = pillar_registry or PillarEngineRegistry()
        self.scoring_engine = scoring_engine or ScoringEngine()
        self.explainability_engine = explainability_engine or ExplainabilityEngine()
        self.confidence_engine = confidence_engine or ConfidenceEngine()

    def run(
        self, analysis_id: str, input_payload: Dict[str, Any]
    ) -> EFSExecutionResult:
        """Executes full methodology-driven EFS pipeline."""
        start_time = time.perf_counter()
        exec_id = f"efs_exec_{uuid.uuid4().hex[:12]}"
        target_version = input_payload.get("methodology_version", "1.0")

        logger.info("Starting EFS Engine execution ID=%s for analysis_id=%s (methodology v%s)", exec_id, analysis_id, target_version)

        # 1. Load Methodology dynamically
        methodology = self.methodology_loader.load(version=target_version)

        # 2. Load Variables & statement flags
        stmt_flags = input_payload.get(
            "statement_flags",
            {
                "has_cash_flow_statement": True,
                "has_balance_sheet": True,
                "has_income_statement": True,
            },
        )

        variables = EFSInputVariables(
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

        # 3. Validation & Eligibility Layer
        self.validation_layer.evaluate_eligibility(
            variables=variables, methodology=methodology
        )
        inputs_used = self.validation_layer.collect_inputs_used(variables)

        # 4. Forensic Rule Engine Execution
        rule_findings, rule_summary = self.rule_engine.evaluate_rules(
            variables=variables, version=target_version
        )

        # 5. Pillar Calculation
        pillar_results = self.pillar_registry.calculate_all(
            variables=variables, methodology=methodology
        )

        # 6. Aggregate Overall Score
        overall_score = self.scoring_engine.aggregate_score(
            pillar_results=pillar_results, methodology=methodology
        )
        manipulation_risk = self.scoring_engine.determine_manipulation_risk(
            overall_score=overall_score, methodology=methodology
        )

        # 7. Multi-Factor Confidence Score
        confidence_score = self.confidence_engine.calculate_confidence(
            variables=variables, methodology=methodology
        )

        # 8. 6-Category Forensic Explainability Engine (Integrating Rule Engine Findings)
        explainability = self.explainability_engine.generate_explainability(
            pillar_results=pillar_results, variables=variables, rule_findings=rule_findings
        )

        # Calculation Performance
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        total_vars_count = sum(len(p.variables_used) for p in pillar_results)

        # Build Regulatory Audit Trail
        audit_trail = AuditTrail(
            execution_id=exec_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            efs_version=methodology.efs_version,
            engine_version="1.0.0",
            inputs_used=inputs_used,
            variables_used_count=total_vars_count,
            calculation_time_ms=total_time_ms,
            rules_evaluated_count=rule_summary.rules_evaluated_count,
            rules_triggered_count=rule_summary.rules_triggered_count,
        )

        logger.info(
            "EFS Engine pipeline completed for analysis_id=%s in %.2f ms. Score=%.2f, Risk=%s, Rules Triggered=%d/%d",
            analysis_id,
            total_time_ms,
            overall_score,
            manipulation_risk,
            rule_summary.rules_triggered_count,
            rule_summary.rules_evaluated_count,
        )

        return EFSExecutionResult(
            analysis_id=analysis_id,
            efs_version=methodology.efs_version,
            overall_score=overall_score,
            confidence=confidence_score,
            manipulation_risk=manipulation_risk,
            audit_trail=audit_trail,
            pillar_scores=pillar_results,
            explainability=explainability,
        )
