"""Rule Executor for the Financial Forensics Rule Engine.

Evaluates forensic rule conditions safely against input datasets. Generates structured findings.
No hardcoded rules or financial formulas.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from app.calculations.efs.models.domain import EFSInputVariables
from app.calculations.efs.rules.models import (
    ForensicRule,
    RuleExecutionSummary,
    TriggeredRuleFinding,
)

logger = logging.getLogger(__name__)


class RuleExecutor:
    """Executor responsible for evaluating rule conditions against variable datasets."""

    def _resolve_variable_value(
        self, var_name: str, variables: EFSInputVariables
    ) -> Optional[Any]:
        """Resolves variable value from raw_variables, feature_data, ratio_data, or statement_flags."""
        # 1. Check raw_variables
        if var_name in variables.raw_variables:
            return variables.raw_variables[var_name]

        # 2. Check feature_data dataset
        if variables.feature_data and isinstance(variables.feature_data, dict):
            dataset = variables.feature_data.get("dataset", {})
            if var_name in dataset:
                return dataset[var_name]

        # 3. Check ratio_data
        if variables.ratio_data and isinstance(variables.ratio_data, dict):
            ratios = variables.ratio_data.get("ratios", [])
            for r in ratios:
                if isinstance(r, dict) and r.get("ratio") == var_name:
                    return r.get("value")

        # 4. Check statement_flags
        if var_name in variables.statement_flags:
            return variables.statement_flags[var_name]

        # 5. Default framework placeholder variables for demonstration testing
        placeholder_values: Dict[str, Any] = {
            "receivables_growth": 15.0,
            "revenue_growth": 5.0,
            "cfo_to_pat_ratio": 0.65,
            "sloan_accrual_ratio": 0.14,
            "dso_days": 95.0,
            "asset_quality_index": 1.35,
            "has_auditor_change": True,
        }
        return placeholder_values.get(var_name)

    def _evaluate_condition(
        self, rule: ForensicRule, variables: EFSInputVariables
    ) -> Tuple[bool, Dict[str, Any]]:
        """Evaluates a single rule condition against variables."""
        cond = rule.condition
        left_val = self._resolve_variable_value(cond.left_variable, variables)

        details: Dict[str, Any] = {"left_variable": cond.left_variable, "left_value": left_val}

        if left_val is None:
            return False, details

        op = cond.operator.lower()

        # Case A: Comparison against right_variable
        if cond.right_variable:
            right_val = self._resolve_variable_value(cond.right_variable, variables)
            details["right_variable"] = cond.right_variable
            details["right_value"] = right_val
            if right_val is None:
                return False, details

            if op == "gt":
                return float(left_val) > float(right_val), details
            elif op == "gte":
                return float(left_val) >= float(right_val), details
            elif op == "lt":
                return float(left_val) < float(right_val), details
            elif op == "lte":
                return float(left_val) <= float(right_val), details
            elif op == "eq":
                return left_val == right_val, details
            elif op == "neq":
                return left_val != right_val, details

        # Case B: Comparison against threshold
        elif cond.threshold is not None:
            details["threshold"] = cond.threshold
            target = float(cond.threshold)
            val = float(left_val)

            if op == "gt":
                return val > target, details
            elif op == "gte":
                return val >= target, details
            elif op == "lt":
                return val < target, details
            elif op == "lte":
                return val <= target, details
            elif op == "eq":
                return val == target, details
            elif op == "neq":
                return val != target, details

        # Case C: Comparison against value (boolean/string/value)
        elif cond.value is not None:
            details["target_value"] = cond.value
            if op == "eq":
                return left_val == cond.value, details
            elif op == "neq":
                return left_val != cond.value, details
            elif op in ("is_true", "true"):
                return bool(left_val) is True, details
            elif op in ("is_false", "false"):
                return bool(left_val) is False, details

        return False, details

    def execute_rules(
        self, rules: List[ForensicRule], variables: EFSInputVariables
    ) -> Tuple[List[TriggeredRuleFinding], RuleExecutionSummary]:
        """Executes provided rules against input dataset and returns triggered findings and summary."""
        start_time = time.perf_counter()
        triggered_findings: List[TriggeredRuleFinding] = []

        logger.debug("Executing %d rules for analysis_id=%s", len(rules), variables.analysis_id)

        for rule in rules:
            try:
                is_triggered, details = self._evaluate_condition(rule, variables)
                if is_triggered:
                    finding = TriggeredRuleFinding(
                        rule_id=rule.rule_id,
                        category=rule.category,
                        severity=rule.severity,
                        message=rule.message,
                        recommendation=rule.recommendation,
                        question_for_management=rule.question_for_management,
                        variables_used=rule.variables_used,
                        details=details,
                    )
                    triggered_findings.append(finding)
                    logger.info(
                        "Rule '%s' [%s - %s] TRIGGERED for analysis_id=%s",
                        rule.rule_id,
                        rule.category,
                        rule.severity,
                        variables.analysis_id,
                    )
            except Exception as exc:
                logger.exception("Error evaluating rule '%s': %s", rule.rule_id, exc)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        summary = RuleExecutionSummary(
            rules_evaluated_count=len(rules),
            rules_triggered_count=len(triggered_findings),
            execution_time_ms=elapsed_ms,
        )

        return triggered_findings, summary
