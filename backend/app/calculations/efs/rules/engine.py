"""Forensic Rule Engine Orchestrator.

Orchestrates rule loading and rule execution for financial forensic evaluation.
"""

import logging
from typing import List, Optional, Tuple

from app.calculations.efs.models.domain import EFSInputVariables
from app.calculations.efs.rules.executor import RuleExecutor
from app.calculations.efs.rules.loader import RuleLoader
from app.calculations.efs.rules.models import RuleExecutionSummary, TriggeredRuleFinding

logger = logging.getLogger(__name__)


class ForensicRuleEngine:
    """Orchestrator loading and executing financial forensics rules dynamically."""

    def __init__(
        self,
        loader: Optional[RuleLoader] = None,
        executor: Optional[RuleExecutor] = None,
    ) -> None:
        self.loader = loader or RuleLoader()
        self.executor = executor or RuleExecutor()

    def evaluate_rules(
        self,
        variables: EFSInputVariables,
        version: str = "1.0",
        group: Optional[str] = None,
    ) -> Tuple[List[TriggeredRuleFinding], RuleExecutionSummary]:
        """Evaluates active forensic rules for a given analysis input and returns findings and execution summary."""
        logger.info("Evaluating forensic rules for analysis_id=%s (version=%s)", variables.analysis_id, version)

        # 1. Load active rules dynamically
        rules = self.loader.load_rules(version=version, group=group, only_enabled=True)

        # 2. Execute rules against input variables
        findings, summary = self.executor.execute_rules(rules=rules, variables=variables)

        logger.info(
            "Forensic Rule Engine finished: %d rules evaluated, %d rules triggered in %.2f ms",
            summary.rules_evaluated_count,
            summary.rules_triggered_count,
            summary.execution_time_ms,
        )

        return findings, summary
