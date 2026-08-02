"""Beneish service — orchestrates the Beneish M-Score calculation for an analysis.

Reads the parsed DataFrames and canonical-to-label mapping from the Parser
and Mapping engines, builds a ValueStore, computes all 8 Beneish components,
combines them into the M-Score, and returns a structured, explainable response.
Results are held in an in-memory store for downstream engines.
"""

from __future__ import annotations

from app.calculations.beneish.components import COMPONENT_FUNCTIONS
from app.calculations.beneish.model import (
    MANIPULATOR_THRESHOLD,
    compute_m_score,
    interpret_m_score,
)
from app.calculations.ratios.calculation_utils import ValueStore
from app.core.exceptions import AnalysisNotFoundError
from app.core.logging import get_logger
from app.schemas.beneish import BeneishComponentResult, BeneishResponse
from app.services.mapping_service import MappingService
from app.services.parser_service import ParserService

logger = get_logger(__name__)

# In-memory store: analysis_id -> BeneishResponse
_beneish_store: dict[str, BeneishResponse] = {}


class BeneishService:
    """Computes the Beneish M-Score for a validated analysis."""

    @staticmethod
    def calculate(analysis_id: str) -> BeneishResponse:
        frames = ParserService.get_frames(analysis_id)
        mappings = MappingService.get_mappings(analysis_id)

        if frames is None or mappings is None:
            logger.warning("Beneish requested for unprocessed analysis %s", analysis_id)
            raise AnalysisNotFoundError(analysis_id)

        # Build canonical-to-label mapping from the mapping store.
        canonical_to_labels: dict[str, list[str]] = {}
        for statement_mappings in mappings.values():
            for sheet_mappings in statement_mappings.values():
                for raw_label, mapped in sheet_mappings.items():
                    canonical_to_labels.setdefault(mapped.mapped, []).append(raw_label)

        value_store = ValueStore(frames, canonical_to_labels)

        component_results: list[BeneishComponentResult] = []
        component_values: dict[str, float] = {}
        summary: dict[str, int] = {"computed": 0, "missing_input": 0, "division_by_zero": 0}

        for name, fn in COMPONENT_FUNCTIONS:
            try:
                value, formula, inputs, interp = fn(value_store)
            except Exception:
                logger.exception(
                    "Analysis %s: Beneish component '%s' raised an unexpected error",
                    analysis_id,
                    name,
                )
                component_results.append(
                    BeneishComponentResult(
                        component=name,
                        value=None,
                        status="missing_input",
                        formula=formula,
                        inputs=inputs,
                        interpretation="Unexpected error during calculation.",
                    )
                )
                summary["missing_input"] += 1
                continue

            if value is None:
                status = "missing_input"
            else:
                status = "computed"
                component_values[name] = value

            summary[status] += 1
            component_results.append(
                BeneishComponentResult(
                    component=name,
                    value=value,
                    status=status,
                    formula=formula,
                    inputs=inputs,
                    interpretation=interp,
                )
            )
            logger.info(
                "Analysis %s: Beneish %s = %s [%s]",
                analysis_id,
                name,
                value if value is not None else "N/A",
                status,
            )

        m_score = compute_m_score(component_values)
        is_manipulator = m_score is not None and m_score > MANIPULATOR_THRESHOLD
        overall_status = "computed" if m_score is not None else "missing_input"

        response = BeneishResponse(
            analysis_id=analysis_id,
            status=overall_status,
            m_score=m_score,
            threshold=MANIPULATOR_THRESHOLD,
            is_manipulator=is_manipulator if m_score is not None else None,
            components=component_results,
            summary=summary,
            interpretation=interpret_m_score(m_score),
        )

        _beneish_store[analysis_id] = response
        logger.info(
            "Analysis %s: Beneish M-Score = %s (threshold %s, manipulator=%s)",
            analysis_id,
            f"{m_score:.4f}" if m_score is not None else "N/A",
            MANIPULATOR_THRESHOLD,
            is_manipulator if m_score is not None else "N/A",
        )
        return response

    @staticmethod
    def get_result(analysis_id: str) -> BeneishResponse | None:
        """Access the in-memory Beneish results for an analysis, if present."""
        return _beneish_store.get(analysis_id)
