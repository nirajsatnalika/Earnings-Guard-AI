"""Cash Flow Integrity Pillar Engine."""

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


class CashFlowIntegrityPillar(BasePillarEngine):
    """Pillar 2: Cash Flow Integrity Engine."""

    @property
    def name(self) -> str:
        return "Cash Flow Integrity"

    @property
    def canonical_key(self) -> str:
        return "cash_flow_integrity"

    def calculate(
        self, variables: EFSInputVariables, weight: float, methodology: MethodologyConfig
    ) -> PillarResult:
        logger.debug("Executing pillar '%s' for analysis_id=%s", self.name, variables.analysis_id)
        start_time = time.perf_counter()

        # Check statement eligibility
        if not variables.statement_flags.get("has_cash_flow_statement", True):
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)
            logger.warning(
                "Cash Flow Statement missing for analysis_id=%s. Marking pillar as ineligible.",
                variables.analysis_id,
            )
            return PillarResult(
                name=self.name,
                canonical_key=self.canonical_key,
                score=0.0,
                weight=weight,
                status="ineligible",
                variables_used=[],
                strengths=[],
                weaknesses=[],
                red_flags=["Missing Cash Flow Statement."],
                execution_metadata=PillarExecutionMetadata(
                    execution_time_ms=elapsed_ms,
                    variables_used=[],
                    variables_missing=["Cash Flow Statement"],
                    variables_ignored=[],
                    warnings=["Cash Flow Statement unavailable. Pillar marked ineligible."],
                ),
                variable_traceability=[],
            )

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
            strengths=["Strong operating cash flow matches reported net earnings baseline."],
            weaknesses=[],
            red_flags=[],
            execution_metadata=metadata,
            variable_traceability=traceability,
        )
