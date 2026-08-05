"""Governance & Disclosure Pillar Engine."""

import logging
import time
from app.calculations.efs.models.domain import (
    EFSInputVariables,
    MethodologyConfig,
    PillarExecutionMetadata,
    PillarResult,
)
from app.calculations.efs.pillars.base import BasePillarEngine

logger = logging.getLogger(__name__)


class GovernanceDisclosurePillar(BasePillarEngine):
    """Pillar 7: Governance & Disclosure Engine."""

    @property
    def name(self) -> str:
        return "Governance & Disclosure"

    @property
    def canonical_key(self) -> str:
        return "governance_disclosure"

    def calculate(
        self, variables: EFSInputVariables, weight: float, methodology: MethodologyConfig
    ) -> PillarResult:
        logger.debug("Executing pillar '%s' for analysis_id=%s", self.name, variables.analysis_id)
        start_time = time.perf_counter()

        traceability = self._build_traceability(self.canonical_key, methodology, variables)
        score = self._calculate_score_from_traceability(traceability)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

        used_vars = [t.name for t in traceability]

        metadata = PillarExecutionMetadata(
            execution_time_ms=elapsed_ms,
            variables_used=used_vars,
            variables_missing=[],
            variables_ignored=[],
            warnings=[],
        )

        return PillarResult(
            name=self.name,
            canonical_key=self.canonical_key,
            score=score,
            weight=weight,
            status="computed",
            variables_used=used_vars,
            strengths=["Standard corporate audit disclosures verified."],
            weaknesses=[],
            red_flags=[],
            execution_metadata=metadata,
            variable_traceability=traceability,
        )
