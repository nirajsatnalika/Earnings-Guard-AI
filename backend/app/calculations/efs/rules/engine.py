"""Forensic Rule Engine Orchestrator.

Orchestrates loading and execution of all 110 forensic rules against calculated EFS variables
and established model outputs.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.calculations.efs.models.domain import EFSVariableResult, ForensicRuleFinding
from app.calculations.efs.rules.executor import RuleExecutor
from app.calculations.efs.rules.loader import RuleLoader

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
        computed_vars: Dict[str, EFSVariableResult],
        established_models: Dict[str, Any],
        version: str = "1.0",
    ) -> Tuple[List[ForensicRuleFinding], int, int]:
        """Evaluates all active forensic rules and returns list of findings, count evaluated, count triggered."""
        logger.info("Evaluating forensic rules (version=%s)...", version)

        # 1. Load active rules dynamically
        rules = self.loader.load_rules(version=version, only_enabled=True)

        # 2. Execute rules against input variables and established models
        findings, evaluated_cnt, triggered_cnt = self.executor.evaluate_rules(
            rules=rules,
            computed_vars=computed_vars,
            established_models=established_models,
        )

        logger.info(
            "Forensic Rule Engine finished: %d rules evaluated, %d rules triggered",
            evaluated_cnt,
            triggered_cnt,
        )

        return findings, evaluated_cnt, triggered_cnt
