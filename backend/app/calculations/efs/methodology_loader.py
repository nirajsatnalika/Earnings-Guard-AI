"""Methodology Loader for the EFS™ Assessment Framework.

Dynamically loads methodology parameters (variables, thresholds, weights, and rules)
from JSON configuration files, separating framework execution from methodology rules.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

from app.calculations.efs.exceptions.base import EFSConfigurationError
from app.calculations.efs.interfaces.base import IMethodologyLoader
from app.calculations.efs.models.domain import MethodologyConfig

logger = logging.getLogger(__name__)


class MethodologyLoader(IMethodologyLoader):
    """Loader reading methodology configuration files dynamically from disk."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        if config_dir is None:
            config_dir = Path(__file__).parent / "config"
        self.config_dir = config_dir
        self._cache: Dict[str, MethodologyConfig] = {}

    def load(self, version: str = "1.0") -> MethodologyConfig:
        """Loads and validates methodology configuration for the given version tag."""
        if version in self._cache:
            logger.debug("Returning cached methodology config for version '%s'", version)
            return self._cache[version]

        weights_file = self.config_dir / "efs_weights.json"
        thresholds_file = self.config_dir / "efs_thresholds.json"
        variables_file = self.config_dir / "efs_variables.json"
        rules_file = self.config_dir / "efs_rules.json"

        for file_path in [weights_file, thresholds_file, variables_file, rules_file]:
            if not file_path.exists():
                logger.error("Missing required methodology configuration file: '%s'", file_path)
                raise EFSConfigurationError(
                    f"Required methodology config file missing: '{file_path}'"
                )

        try:
            logger.info("Loading EFS methodology configuration version '%s' from '%s'", version, self.config_dir)
            with open(weights_file, "r", encoding="utf-8") as f:
                weights_data = json.load(f)

            with open(thresholds_file, "r", encoding="utf-8") as f:
                thresholds_data = json.load(f)

            with open(variables_file, "r", encoding="utf-8") as f:
                variables_data = json.load(f)

            with open(rules_file, "r", encoding="utf-8") as f:
                rules_data = json.load(f)

            config = MethodologyConfig(
                efs_version=weights_data.get("efs_version", version),
                pillar_weights=weights_data.get("pillar_weights", {}),
                sub_variable_weights=weights_data.get("sub_variable_weights", {}),
                risk_bands=thresholds_data.get("risk_bands", {}),
                confidence_factors=thresholds_data.get("confidence_factors", {}),
                registered_variables=variables_data.get("registered_variables", {}),
                eligibility_rules=rules_data.get("eligibility_rules", {}),
                evaluation_rules=rules_data.get("evaluation_rules", []),
            )

            self._cache[version] = config
            return config

        except Exception as exc:
            logger.exception("Error loading methodology version '%s': %s", version, exc)
            raise EFSConfigurationError(
                f"Failed to load methodology version '{version}': {str(exc)}"
            ) from exc
