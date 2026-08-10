"""Rule Loader for the Financial Forensics Rule Engine.

Dynamically loads forensic rules from JSON configuration files (efs_rules.json). No hardcoded rules.
Supports 110 frozen forensic rules from 04_EFS_FORENSIC_RULEBOOK.xlsx.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.calculations.efs.exceptions.base import EFSConfigurationError
from app.calculations.efs.models.domain import ForensicRuleFinding

logger = logging.getLogger(__name__)


class RuleLoader:
    """Loader reading forensic rules from efs_rules.json configuration on disk."""

    def __init__(self, rules_file_path: Optional[Path] = None) -> None:
        if rules_file_path is None:
            rules_file_path = Path(__file__).parent.parent / "config" / "efs_rules.json"
        self.rules_file_path = rules_file_path
        self._cache: Dict[str, List[Dict]] = {}

    def load_rules(
        self,
        version: str = "1.0",
        only_enabled: bool = True,
    ) -> List[Dict]:
        """Loads all 110 forensic rules matching specified version."""
        cache_key = f"{version}_{only_enabled}"
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
            parsed_rules: List[Dict] = []

            for item in raw_rules:
                is_enabled = item.get("enabled", True)
                if only_enabled and not is_enabled:
                    continue
                parsed_rules.append(item)

            logger.info("Successfully loaded %d forensic rules.", len(parsed_rules))
            self._cache[cache_key] = parsed_rules
            return parsed_rules

        except Exception as exc:
            logger.exception("Error loading forensic rules from '%s': %s", self.rules_file_path, exc)
            raise EFSConfigurationError(
                f"Failed to load forensic rules from '{self.rules_file_path}': {str(exc)}"
            ) from exc
