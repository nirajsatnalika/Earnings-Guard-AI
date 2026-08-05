"""Enhanced Multi-Factor Confidence Engine for the EFS™ Assessment Framework.

Evaluates data confidence taking into account:
- validation completeness
- parser confidence
- mapping confidence
- missing financial statements
- missing variables
- validation errors
"""

import logging
from app.calculations.efs.interfaces.base import IConfidenceEngine
from app.calculations.efs.models.domain import EFSInputVariables, MethodologyConfig

logger = logging.getLogger(__name__)


class ConfidenceEngine(IConfidenceEngine):
    """Engine calculating multi-factor data confidence for forensic earnings quality assessment."""

    def calculate_confidence(
        self, variables: EFSInputVariables, methodology: MethodologyConfig
    ) -> float:
        """Calculates confidence score (0 to 100) incorporating all input quality factors."""
        logger.debug("Calculating EFS multi-factor confidence score for analysis_id=%s", variables.analysis_id)
        factors = methodology.confidence_factors
        confidence = 100.0

        # 1. Validation Completeness & Module Presence
        missing_modules = 0
        if variables.validation_data is None:
            missing_modules += 1
        if variables.feature_data is None:
            missing_modules += 1
        if variables.ratio_data is None:
            missing_modules += 1
        if variables.beneish_data is None:
            missing_modules += 1

        module_penalty = missing_modules * factors.get("missing_variable_penalty", 5.0)
        confidence -= module_penalty

        # 2. Missing Financial Statements
        if variables.missing_financial_statements_count > 0:
            confidence -= (
                variables.missing_financial_statements_count
                * factors.get("missing_statement_penalty", 20.0)
            )

        # 3. Missing Variables Count
        if variables.missing_variables_count > 0:
            confidence -= variables.missing_variables_count * 2.0

        # 4. Validation Errors Count
        if variables.validation_errors_count > 0:
            confidence -= (
                variables.validation_errors_count
                * factors.get("validation_error_penalty", 10.0)
            )

        # 5. Parser Confidence Deficit
        if variables.parser_confidence < 100.0:
            deficit = (100.0 - variables.parser_confidence) / 100.0
            confidence -= deficit * factors.get("low_parser_confidence_penalty", 15.0)

        # 6. Mapping Confidence Deficit
        if variables.mapping_confidence < 100.0:
            deficit = (100.0 - variables.mapping_confidence) / 100.0
            confidence -= deficit * 10.0

        final_score = round(max(min(confidence, 100.0), 0.0), 2)
        logger.info(
            "Confidence Engine evaluated score %.2f for analysis_id=%s",
            final_score,
            variables.analysis_id,
        )
        return final_score
