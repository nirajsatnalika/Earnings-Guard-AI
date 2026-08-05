"""Validation Layer for the EFS™ Assessment Framework.

Evaluates incoming inputs, statement availability, and eligibility rules
prior to executing pillar calculations.
"""

import logging
from typing import Dict, List
from app.calculations.efs.models.domain import EFSInputVariables, MethodologyConfig

logger = logging.getLogger(__name__)


class ValidationLayer:
    """Evaluates input data validity and statement eligibility rules."""

    def evaluate_eligibility(
        self, variables: EFSInputVariables, methodology: MethodologyConfig
    ) -> Dict[str, bool]:
        """Determines pillar eligibility status based on methodology eligibility rules."""
        logger.debug("Evaluating statement eligibility for analysis_id=%s", variables.analysis_id)
        rules = methodology.eligibility_rules
        statement_flags = variables.statement_flags

        eligibility: Dict[str, bool] = {
            "financial_statement_quality": True,
            "accrual_quality": True,
            "working_capital_health": True,
            "balance_sheet_integrity": True,
            "growth_sustainability": True,
            "governance_disclosure": True,
        }

        # Check Cash Flow Integrity eligibility rule
        if rules.get("require_cash_flow_statement", True):
            has_cfs = statement_flags.get("has_cash_flow_statement", True)
            eligibility["cash_flow_integrity"] = has_cfs
            if not has_cfs:
                logger.warning(
                    "Cash Flow Statement unavailable for analysis_id=%s. Marking cash_flow_integrity pillar as ineligible.",
                    variables.analysis_id,
                )
        else:
            eligibility["cash_flow_integrity"] = True

        return eligibility

    def collect_inputs_used(self, variables: EFSInputVariables) -> List[str]:
        """Identifies active upstream engine input sources present in the payload."""
        inputs_used: List[str] = []
        if variables.validation_data is not None:
            inputs_used.append("validation")
        if variables.feature_data is not None:
            inputs_used.append("features")
        if variables.ratio_data is not None:
            inputs_used.append("ratios")
        if variables.beneish_data is not None:
            inputs_used.append("beneish")
        return inputs_used
