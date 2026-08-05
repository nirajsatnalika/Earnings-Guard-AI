"""Scoring Engine for the EFS™ Assessment Framework.

Aggregates individual pillar scores into an overall weighted score and determines
the manipulation risk level based on methodology configurations.
"""

import logging
from typing import List
from app.calculations.efs.interfaces.base import IScoringEngine
from app.calculations.efs.models.domain import MethodologyConfig, PillarResult

logger = logging.getLogger(__name__)


class ScoringEngine(IScoringEngine):
    """Scoring engine performing overall weighted score aggregation and risk classification."""

    def aggregate_score(
        self, pillar_results: List[PillarResult], methodology: MethodologyConfig
    ) -> float:
        """Aggregates individual pillar scores into a weighted overall score using methodology weights."""
        if not pillar_results:
            logger.warning("No pillar results provided for score aggregation.")
            return 0.0

        weights_map = methodology.pillar_weights
        weighted_sum = 0.0
        total_weight = 0.0

        for res in pillar_results:
            if res.status == "ineligible":
                logger.debug("Skipping ineligible pillar '%s' in score aggregation.", res.canonical_key)
                continue

            w = weights_map.get(res.canonical_key, res.weight)
            weighted_sum += res.score * w
            total_weight += w

        if total_weight <= 0:
            logger.warning("Total active pillar weight is zero or negative.")
            return 0.0

        overall = weighted_sum / total_weight
        final_score = round(overall, 2)
        logger.info("Calculated overall EFS score: %.2f", final_score)
        return final_score

    def determine_manipulation_risk(
        self, overall_score: float, methodology: MethodologyConfig
    ) -> str:
        """Determines risk label from overall score using methodology risk bands."""
        bands = methodology.risk_bands
        low_min = bands.get("low", {}).get("min_score", 80.0)
        mod_min = bands.get("moderate", {}).get("min_score", 60.0)
        high_min = bands.get("high", {}).get("min_score", 40.0)

        if overall_score >= low_min:
            risk = bands.get("low", {}).get("label", "Low")
        elif overall_score >= mod_min:
            risk = bands.get("moderate", {}).get("label", "Moderate")
        elif overall_score >= high_min:
            risk = bands.get("high", {}).get("label", "High")
        else:
            risk = bands.get("critical", {}).get("label", "Critical")

        logger.info("Classified manipulation risk label as '%s' for overall score %.2f", risk, overall_score)
        return risk
