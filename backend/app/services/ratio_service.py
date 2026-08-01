"""Ratio service — orchestrates ratio calculations for an analysis.

Reads the parsed DataFrames and canonical-to-label mapping from the Parser and
Mapping engines, builds a ValueStore, executes every registered ratio function,
and returns a structured response. Results are held in an in-memory store for
downstream engines.
"""

from __future__ import annotations

from app.calculations.ratios.calculation_utils import ValueStore
from app.calculations.ratios.formula_library import RATIO_FUNCTIONS
from app.core.exceptions import AnalysisNotFoundError
from app.core.logging import get_logger
from app.schemas.ratios import RatioResponse, RatioResult
from app.services.mapping_service import MappingService
from app.services.parser_service import ParserService

logger = get_logger(__name__)

# In-memory store: analysis_id -> RatioResponse
_ratio_store: dict[str, RatioResponse] = {}


class RatioService:
    """Computes all financial ratios for a validated analysis."""

    @staticmethod
    def calculate(analysis_id: str) -> RatioResponse:
        frames = ParserService.get_frames(analysis_id)
        mappings = MappingService.get_mappings(analysis_id)

        if frames is None or mappings is None:
            logger.warning("Ratios requested for unprocessed analysis %s", analysis_id)
            raise AnalysisNotFoundError(analysis_id)

        # Build canonical-to-label mapping from the mapping store.
        canonical_to_labels: dict[str, list[str]] = {}
        for statement_mappings in mappings.values():
            for sheet_mappings in statement_mappings.values():
                for raw_label, mapped in sheet_mappings.items():
                    canonical_to_labels.setdefault(mapped.mapped, []).append(raw_label)

        value_store = ValueStore(frames, canonical_to_labels)

        results: list[RatioResult] = []
        summary = {"computed": 0, "missing_input": 0, "division_by_zero": 0}

        for ratio_fn in RATIO_FUNCTIONS:
            try:
                result = ratio_fn(value_store)
                results.append(result)
                summary[result.status] = summary.get(result.status, 0) + 1
                logger.info(
                    "Analysis %s: %s (%s) = %s [%s]",
                    analysis_id,
                    result.ratio,
                    result.category,
                    result.value if result.value is not None else "N/A",
                    result.status,
                )
            except Exception:
                logger.exception(
                    "Analysis %s: ratio function '%s' raised an unexpected error",
                    analysis_id,
                    getattr(ratio_fn, "__name__", str(ratio_fn)),
                )
                result = RatioResult(
                    ratio=getattr(ratio_fn, "__name__", "unknown"),
                    category="Unknown",
                    value=None,
                    status="missing_input",
                    interpretation="Unexpected error during calculation.",
                )
                results.append(result)
                summary["missing_input"] = summary.get("missing_input", 0) + 1

        response = RatioResponse(
            analysis_id=analysis_id,
            status="computed",
            ratios=results,
            summary=summary,
        )

        _ratio_store[analysis_id] = response
        logger.info(
            "Analysis %s: ratios complete — %d computed, %d missing, %d div-by-zero",
            analysis_id,
            summary["computed"],
            summary["missing_input"],
            summary["division_by_zero"],
        )
        return response

    @staticmethod
    def get_ratios(analysis_id: str) -> RatioResponse | None:
        """Access the in-memory ratio results for an analysis, if present."""
        return _ratio_store.get(analysis_id)
