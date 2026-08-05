"""Base Pillar Engine implementation with variable traceability and execution metadata tracking."""

import logging
from typing import List, Optional
from app.calculations.efs.interfaces.base import IPillarEngine
from app.calculations.efs.models.domain import (
    EFSInputVariables,
    MethodologyConfig,
    VariableTraceability,
)

logger = logging.getLogger(__name__)


class BasePillarEngine(IPillarEngine):
    """Base class for all EFS Pillar Engines."""

    def _build_traceability(
        self,
        pillar_key: str,
        methodology: MethodologyConfig,
        variables: EFSInputVariables,
    ) -> List[VariableTraceability]:
        """Utility building sub-variable traceability entries based on methodology sub-variable weights."""
        traceability: List[VariableTraceability] = []
        registered_vars = methodology.registered_variables.get(pillar_key, [])
        sub_weights = methodology.sub_variable_weights.get(pillar_key, {})

        default_weight = 1.0 / max(len(registered_vars), 1)

        for var_name in registered_vars:
            weight = sub_weights.get(var_name, round(default_weight, 4))
            val: Optional[float] = 100.0  # Placeholder framework resolution
            contrib = round(val * weight, 4) if val is not None else 0.0

            traceability.append(
                VariableTraceability(
                    name=var_name,
                    value=val,
                    weight=weight,
                    contribution=contrib,
                    status="computed",
                )
            )
        return traceability

    def _calculate_score_from_traceability(
        self, traceability: List[VariableTraceability]
    ) -> float:
        """Calculates aggregate pillar score from variable contributions."""
        if not traceability:
            return 100.0
        total_weight = sum(t.weight for t in traceability)
        if total_weight <= 0:
            return 100.0
        weighted_sum = sum(t.contribution for t in traceability)
        return round(min(max(weighted_sum / total_weight, 0.0), 100.0), 2)
