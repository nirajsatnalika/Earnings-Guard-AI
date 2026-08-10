"""Scoring Engine for the EFS™ Assessment Framework.

Evaluates raw variable values against frozen 03_EFS_SCORING_RULES.xlsx bands (0, 25, 50, 75, 100).
Provides a clean aggregation interface for variable and pillar weights.
When weights are marked TBD (calibration pending), returns score_status="CALIBRATION_PENDING",
overall score=None, risk_level=None while preserving all component scores.
"""

import logging
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.calculations.efs.interfaces.base import IScoringEngine
from app.calculations.efs.models.domain import MethodologyConfig, PillarResult

logger = logging.getLogger(__name__)


class ScoringEngine(IScoringEngine):
    """Methodology-driven scoring engine supporting 0-100 assessment bands and weight calibration."""

    def __init__(self, scoring_rules_path: Optional[Path] = None) -> None:
        if scoring_rules_path is None:
            scoring_rules_path = Path(__file__).parent / "config" / "efs_scoring_rules.json"
        self.scoring_rules_path = scoring_rules_path
        self._scoring_rules: Dict[str, Dict[str, Any]] = {}
        self._load_scoring_rules()

    def _load_scoring_rules(self) -> None:
        """Loads variable scoring rules from efs_scoring_rules.json."""
        if self.scoring_rules_path.exists():
            try:
                with open(self.scoring_rules_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._scoring_rules = data.get("scoring_rules", {})
                logger.info("Loaded %d variable scoring rules.", len(self._scoring_rules))
            except Exception as exc:
                logger.warning("Failed to load efs_scoring_rules.json: %s", exc)

    def score_variable(self, var_id: str, raw_value: Optional[float]) -> Tuple[Optional[int], str]:
        """Scores an individual raw variable value into 0, 25, 50, 75, or 100 band."""
        if raw_value is None:
            return None, "INSUFFICIENT_DATA"

        rule = self._scoring_rules.get(var_id)
        if not rule:
            # Default neutral score if rule definition absent
            return 50, "Moderate / 50"

        direction = rule.get("direction", "").lower()
        bands = rule.get("bands", {})

        # Rule specific scoring logic based on direction and variable ID
        # 1. Lower is better (e.g., DSRI, SGAI, Accruals, Days Outstanding)
        if "lower" in direction or var_id in ["FSQ03", "FSQ08", "FSQ09", "AQ01", "AQ02", "BSI02", "BSI09"]:
            if var_id == "FSQ03":  # DSRI
                if raw_value <= 1.00: return 100, "Strong / 100"
                if raw_value <= 1.10: return 75, "Good / 75"
                if raw_value <= 1.20: return 50, "Moderate / 50"
                if raw_value <= 1.40: return 25, "Weak / 25"
                return 0, "Critical / 0"
            
            if var_id in ["FSQ08", "FSQ09"]:  # Other Income / Exceptional Items
                if raw_value < 0.05 or raw_value < 5: return 100, "Strong / 100"
                if raw_value < 0.10 or raw_value < 10: return 75, "Good / 75"
                if raw_value < 0.25 or raw_value < 25: return 50, "Moderate / 50"
                if raw_value < 0.50 or raw_value < 50: return 25, "Weak / 25"
                return 0, "Critical / 0"

            if var_id == "AQ01":  # Accruals / Assets
                if raw_value <= 0.02: return 100, "Strong / 100"
                if raw_value <= 0.05: return 75, "Good / 75"
                if raw_value <= 0.10: return 50, "Moderate / 50"
                if raw_value <= 0.15: return 25, "Weak / 25"
                return 0, "Critical / 0"

            # General Lower direction fallback
            if raw_value <= 0.0: return 100, "Strong / 100"
            if raw_value <= 0.05: return 75, "Good / 75"
            if raw_value <= 0.10: return 50, "Moderate / 50"
            if raw_value <= 0.20: return 25, "Weak / 25"
            return 0, "Critical / 0"

        # 2. Higher is better (e.g., CFO/Revenue, FCF Margin, CFO/PAT)
        if "higher" in direction or var_id in ["FSQ04", "CFI01", "CFI02", "CFI03"]:
            if var_id == "FSQ04":  # CFO / Revenue
                val = raw_value if raw_value > 1.0 else raw_value * 100
                if val >= 20.0: return 100, "Strong / 100"
                if val >= 10.0: return 75, "Good / 75"
                if val >= 5.0: return 50, "Moderate / 50"
                if val >= 0.0: return 25, "Weak / 25"
                return 0, "Critical / 0"

            if var_id == "CFI01":  # CFO / PAT
                if raw_value >= 1.2: return 100, "Strong / 100"
                if raw_value >= 1.0: return 75, "Good / 75"
                if raw_value >= 0.8: return 50, "Moderate / 50"
                if raw_value >= 0.5: return 25, "Weak / 25"
                return 0, "Critical / 0"

            # General Higher direction fallback
            if raw_value >= 0.20: return 100, "Strong / 100"
            if raw_value >= 0.10: return 75, "Good / 75"
            if raw_value >= 0.05: return 50, "Moderate / 50"
            if raw_value >= 0.0: return 25, "Weak / 25"
            return 0, "Critical / 0"

        # Default moderate score for complex or context dependent variables
        return 50, "Moderate / 50"

    def aggregate_score(
        self, pillar_results: List[PillarResult], methodology: MethodologyConfig
    ) -> Optional[float]:
        """Aggregates individual pillar scores into overall weighted EFS score.
        
        Per EFS Methodology, if weights are marked TBD / CALIBRATION_PENDING,
        returns None rather than generating a false precision score by simple averaging.
        """
        weights_map = methodology.pillar_weights
        
        # Check if weights are TBD or uncalibrated
        is_tbd = (
            not weights_map or 
            any(w == "TBD" or w is None for w in weights_map.values())
        )

        if is_tbd:
            logger.info("Pillar weights are marked TBD; returning None for overall score (CALIBRATION_PENDING).")
            return None

        weighted_sum = 0.0
        total_weight = 0.0

        for res in pillar_results:
            if res.status == "ineligible" or res.score is None:
                continue

            w = float(weights_map.get(res.canonical_key, 0.0))
            weighted_sum += res.score * w
            total_weight += w

        if total_weight <= 0:
            return None

        return round(weighted_sum / total_weight, 2)

    def determine_manipulation_risk(
        self, overall_score: Optional[float], methodology: MethodologyConfig
    ) -> Optional[str]:
        """Determines risk label from overall score using methodology risk bands.
        
        If overall_score is None (Calibration Pending), returns None.
        """
        if overall_score is None:
            return None

        bands = methodology.risk_bands
        low_min = bands.get("low", {}).get("min_score", 80.0)
        mod_min = bands.get("moderate", {}).get("min_score", 60.0)
        high_min = bands.get("high", {}).get("min_score", 40.0)

        if overall_score >= low_min:
            return bands.get("low", {}).get("label", "Low")
        if overall_score >= mod_min:
            return bands.get("moderate", {}).get("label", "Moderate")
        if overall_score >= high_min:
            return bands.get("high", {}).get("label", "High")
        return bands.get("critical", {}).get("label", "Critical")
