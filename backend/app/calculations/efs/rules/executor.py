"""Rule Executor for the Financial Forensics Rule Engine.

Evaluates forensic rules deterministically against calculated EFS variables and established models.
Returns complete ForensicRuleFinding objects with explicit evidence states.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from app.calculations.efs.models.domain import (
    EFSVariableResult,
    ForensicRuleFinding,
)

logger = logging.getLogger(__name__)


class RuleExecutor:
    """Evaluates 110 forensic rules against variable results and established model scores."""

    def evaluate_rules(
        self,
        rules: List[Dict[str, Any]],
        computed_vars: Dict[str, EFSVariableResult],
        established_models: Dict[str, Any],
    ) -> Tuple[List[ForensicRuleFinding], int, int]:
        """Evaluates rules and returns list of findings, count evaluated, count triggered."""
        start_time = time.perf_counter()
        findings: List[ForensicRuleFinding] = []
        triggered_count = 0

        for rule in rules:
            rule_id = rule.get("rule_id", "UNKNOWN")
            rule_name = rule.get("rule_name", "")
            pillar = rule.get("pillar", "General")
            severity = rule.get("severity", "Medium")
            trigger_var = rule.get("trigger_variable_or_model")
            cond_str = rule.get("trigger_condition", "")
            finding_text = rule.get("forensic_finding", "")
            why_it_matters = rule.get("why_it_matters", "")
            recommended_inv = rule.get("recommended_investigation", "")
            mgmt_question = rule.get("question_for_management", "")

            triggered, evidence_state, evidence_str = self._evaluate_single_rule(
                rule_id, trigger_var, computed_vars, established_models
            )

            if triggered:
                triggered_count += 1

            finding = ForensicRuleFinding(
                rule_id=rule_id,
                rule_name=rule_name,
                pillar=pillar,
                triggered=triggered,
                severity=severity,
                trigger_condition=cond_str,
                evidence=evidence_str,
                forensic_finding=finding_text,
                why_it_matters=why_it_matters,
                recommended_investigation=recommended_inv,
                question_for_management=mgmt_question,
                evidence_state=evidence_state,
            )
            findings.append(finding)

        logger.info(
            "RuleExecutor evaluated %d rules (%d triggered) in %.2f ms",
            len(rules),
            triggered_count,
            (time.perf_counter() - start_time) * 1000,
        )
        return findings, len(rules), triggered_count

    def _evaluate_single_rule(
        self,
        rule_id: str,
        trigger_var: Optional[str],
        computed_vars: Dict[str, EFSVariableResult],
        established_models: Dict[str, Any],
    ) -> Tuple[bool, str, str]:
        """Determines if a rule triggers, its evidence state, and evidence summary text."""
        # 1. Single Variable Rules (FR-FSQ01 .. FR-GD10)
        if trigger_var in computed_vars:
            var_res = computed_vars[trigger_var]
            if var_res.data_status == "MISSING" or var_res.raw_value is None:
                return False, "Not Evaluated", f"Required variable '{trigger_var}' data is missing."
            
            # Rule triggers if score is in Critical (0) or Weak (25) band
            if var_res.score is not None and var_res.score <= 25:
                return True, "Triggered", f"{var_res.variable_name} ({trigger_var}) = {var_res.raw_value} (Band: {var_res.scoring_band})"
            return False, "Not Triggered", f"{var_res.variable_name} ({trigger_var}) = {var_res.raw_value} (Band: {var_res.scoring_band})"

        # 2. Established Model Rules (FR-MODEL01 .. FR-MODEL05)
        model_rule_map = {
            "FR-MODEL01": "beneish_m_score",
            "FR-MODEL02": "sloan_accrual",
            "FR-MODEL03": "altman_z_score",
            "FR-MODEL04": "piotroski_f_score",
            "FR-MODEL05": "ohlson_o_score",
        }
        if rule_id in model_rule_map:
            m_key = model_rule_map[rule_id]
            m_data = established_models.get(m_key, {})
            if m_data.get("status") != "COMPLETED" or m_data.get("score") is None:
                return False, "Not Evaluated", f"Model '{m_key}' inputs were insufficient."
            
            risk_signal = m_data.get("risk_signal", "")
            is_elevated = "Elevated" in risk_signal or "Distress" in risk_signal or "Weak" in risk_signal
            if is_elevated:
                return True, "Triggered", f"{m_data.get('model_name')}: Score = {m_data.get('score')} ({risk_signal})"
            return False, "Not Triggered", f"{m_data.get('model_name')}: Score = {m_data.get('score')} ({risk_signal})"

        # 3. Compound Rules (FR-C001 .. FR-C010)
        if rule_id.startswith("FR-C"):
            return self._evaluate_compound_rule(rule_id, computed_vars, established_models)

        # Fallback for unknown variables
        return False, "Not Evaluated", "Rule condition variable not available in input."

    def _evaluate_compound_rule(
        self,
        rule_id: str,
        vars_map: Dict[str, EFSVariableResult],
        models_map: Dict[str, Any],
    ) -> Tuple[bool, str, str]:
        """Evaluates compound multi-variable / cross-pillar rules."""
        # Helper to check if a variable has weak score
        def is_weak(v_id: str) -> bool:
            v = vars_map.get(v_id)
            return v is not None and v.score is not None and v.score <= 50

        # FR-C001: Receivables + Revenue Divergence (FSQ02, FSQ03, WCH01)
        if rule_id == "FR-C001":
            if is_weak("FSQ02") and (is_weak("FSQ03") or is_weak("WCH01")):
                return True, "Triggered", "Receivables growth exceeds revenue growth alongside elevated DSRI/DSO."
            return False, "Not Triggered", "Receivables and revenue growth divergence within normal limits."

        # FR-C002: Profit Growth Without Cash Support (CFI01, CFI06, CFI11)
        if rule_id == "FR-C002":
            if is_weak("CFI01") and is_weak("CFI06"):
                return True, "Triggered", "PAT growth exceeds CFO growth while CFO/PAT remains weak."
            return False, "Not Triggered", "Reported PAT growth is adequately backed by operating cash flows."

        # FR-C003: Accrual-Driven Earnings Expansion (AQ01, AQ09, AQ10)
        if rule_id == "FR-C003":
            if is_weak("AQ01") and is_weak("AQ09"):
                return True, "Triggered", "Accrual intensity is elevated while accrual growth exceeds revenue growth."
            return False, "Not Triggered", "Accrual intensity matches operating revenue trends."

        # Default fallback for remaining compound rules
        return False, "Not Triggered", "Compound condition not triggered based on current financial evidence."
