"""Rule Loader for the Financial Forensics Rule Engine.

Dynamically loads forensic rules from JSON configuration files. No hardcoded rules in Python.
Supports rule priorities, rule groups, enable/disable switches, and versioning.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.calculations.efs.exceptions.base import EFSConfigurationError
from app.calculations.efs.rules.models import ForensicRule, RuleCondition

logger = logging.getLogger(__name__)


class RuleLoader:
    """Loader reading forensic rules from JSON configurations on disk."""

    def __init__(self, rules_file_path: Optional[Path] = None) -> None:
        if rules_file_path is None:
            rules_file_path = Path(__file__).parent.parent / "config" / "efs_rules.json"
        self.rules_file_path = rules_file_path
        self._cache: Dict[str, List[ForensicRule]] = {}

    def load_rules(
        self,
        version: str = "1.0",
        group: Optional[str] = None,
        only_enabled: bool = True,
    ) -> List[ForensicRule]:
        """Loads and parses rules matching specified version and optional group filters."""
        cache_key = f"{version}_{group}_{only_enabled}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self.rules_file_path.exists():
            logger.error("Missing forensic rules configuration file: '%s'", self.rules_file_path)
            raise EFSConfigurationError(
                f"Required rules config file missing: '{self.rules_file_path}'"
            )

        try:
            logger.info("Loading forensic rules from '%s' (version='%s')", self.rules_file_path, version)
            with open(self.rules_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            raw_rules = data.get("rules", [])
            parsed_rules: List[ForensicRule] = []

            for item in raw_rules:
                rule_ver = item.get("version", "1.0")
                is_enabled = item.get("enabled", True)
                rule_group = item.get("group", "general")

                # Filter checks
                if only_enabled and not is_enabled:
                    continue
                if version and rule_ver != version:
                    continue
                if group and rule_group != group:
                    continue

                cond_dict = item.get("condition", {})
                condition = RuleCondition(
                    operator=cond_dict.get("operator", "eq"),
                    left_variable=cond_dict.get("left_variable", ""),
                    right_variable=cond_dict.get("right_variable"),
                    threshold=cond_dict.get("threshold"),
                    value=cond_dict.get("value"),
                )

                rule = ForensicRule(
                    rule_id=item.get("rule_id", "UNKNOWN"),
                    category=item.get("category", "General"),
                    severity=item.get("severity", "Info"),
                    condition=condition,
                    message=item.get("message", ""),
                    recommendation=item.get("recommendation", ""),
                    question_for_management=item.get("question_for_management", ""),
                    priority=item.get("priority", 10),
                    group=rule_group,
                    enabled=is_enabled,
                    version=rule_ver,
                    variables_used=item.get("variables_used", []),
                )
                parsed_rules.append(rule)

            # Sort rules by priority descending (higher priority runs first)
            parsed_rules.sort(key=lambda r: r.priority, reverse=True)

            logger.info("Successfully loaded and parsed %d active forensic rules.", len(parsed_rules))
            self._cache[cache_key] = parsed_rules
            return parsed_rules

        except Exception as exc:
            logger.exception("Error loading forensic rules from '%s': %s", self.rules_file_path, exc)
            raise EFSConfigurationError(
                f"Failed to load forensic rules from '{self.rules_file_path}': {str(exc)}"
            ) from exc
