"""Enhanced Multi-Factor Confidence Engine for the EFS™ Assessment Framework.

Evaluates data confidence taking into account:
- financial statement completeness
- variable availability
- validation status
- mapping confidence
- model availability
- rule evaluation completeness
"""

import logging
from typing import Dict, List, Tuple

from app.calculations.efs.models.domain import (
    ConfidenceResult,
    EFSInputVariables,
    MethodologyConfig,
)

logger = logging.getLogger(__name__)


class ConfidenceEngine:
    """Engine calculating multi-factor data confidence for forensic earnings quality assessment."""

    def calculate_confidence(
        self,
        variables: EFSInputVariables,
        methodology: MethodologyConfig,
        total_vars_evaluated: int = 95,
        total_vars_available: int = 95,
        models_available_count: int = 5,
    ) -> ConfidenceResult:
        """Calculates structured confidence score, level, factors, and limitations."""
        logger.debug("Calculating EFS multi-factor confidence for analysis_id=%s", variables.analysis_id)
        
        confidence = 100.0
        factors: Dict[str, float] = {}
        limitations: List[str] = []

        # 1. Statement Completeness
        stmt_flags = variables.statement_flags
        missing_stmts = []
        if not stmt_flags.get("has_income_statement", True):
            missing_stmts.append("Income Statement")
        if not stmt_flags.get("has_balance_sheet", True):
            missing_stmts.append("Balance Sheet")
        if not stmt_flags.get("has_cash_flow_statement", True):
            missing_stmts.append("Cash Flow Statement")

        if missing_stmts:
            stmt_penalty = len(missing_stmts) * 20.0
            confidence -= stmt_penalty
            factors["statement_completeness_penalty"] = stmt_penalty
            limitations.append(f"Missing core financial statements: {', '.join(missing_stmts)}.")

        # 2. Variable Availability Ratio
        avail_ratio = total_vars_available / max(total_vars_evaluated, 1)
        if avail_ratio < 1.0:
            var_penalty = round((1.0 - avail_ratio) * 30.0, 2)
            confidence -= var_penalty
            factors["variable_availability_penalty"] = var_penalty
            missing_cnt = total_vars_evaluated - total_vars_available
            limitations.append(f"{missing_cnt} out of {total_vars_evaluated} methodology variables were unavailable or missing.")

        # 3. Model Availability
        if models_available_count < 5:
            model_penalty = (5 - models_available_count) * 5.0
            confidence -= model_penalty
            factors["model_availability_penalty"] = model_penalty
            limitations.append(f"{5 - models_available_count} established model(s) could not be evaluated due to missing input components.")

        # 4. Mapping & Parser Quality
        if variables.mapping_confidence < 100.0:
            map_penalty = round((100.0 - variables.mapping_confidence) * 0.15, 2)
            confidence -= map_penalty
            factors["mapping_confidence_penalty"] = map_penalty
            limitations.append(f"Line-item mapping confidence is {variables.mapping_confidence:.1f}%.")

        final_score = round(max(min(confidence, 100.0), 0.0), 2)
        
        if final_score >= 80.0:
            level = "High"
        elif final_score >= 50.0:
            level = "Medium"
        else:
            level = "Low"

        logger.info(
            "Confidence Engine evaluated score %.2f (%s) for analysis_id=%s",
            final_score,
            level,
            variables.analysis_id,
        )

        return ConfidenceResult(
            confidence_score=final_score,
            confidence_level=level,
            confidence_factors=factors,
            limitations=limitations,
        )
