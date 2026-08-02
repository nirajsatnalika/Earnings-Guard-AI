"""Normalizer service — orchestrates financial data normalization for an analysis.

Reads parsed DataFrames from the Parser Engine's in-memory store, runs the
Normalizer to produce structured numeric grids with currency, unit, and sign
metadata, and returns a structured response. Results are held in an in-memory
store for downstream engines.
"""

from __future__ import annotations

from app.calculations.normalizer import Normalizer
from app.core.exceptions import AnalysisNotFoundError
from app.core.logging import get_logger
from app.schemas.normalize import NormalizeResponse, NormalizedStatementResult
from app.services.parser_service import ParserService

logger = get_logger(__name__)

# In-memory store: analysis_id -> NormalizeResponse
_normalize_store: dict[str, NormalizeResponse] = {}


class NormalizerService:
    """Normalizes parsed financial statements for an analysis."""

    @staticmethod
    def normalize(analysis_id: str) -> NormalizeResponse:
        frames = ParserService.get_frames(analysis_id)
        if frames is None:
            logger.warning("Normalize requested for unparsed analysis %s", analysis_id)
            raise AnalysisNotFoundError(analysis_id)

        statement_results: list[NormalizedStatementResult] = Normalizer.normalize(frames)

        total_cells = 0
        normalized_cells = 0
        unparseable_cells = 0

        for stmt in statement_results:
            for sheet in stmt.sheets:
                for row in sheet.cells:
                    for cell in row:
                        total_cells += 1
                        if cell.is_parseable:
                            normalized_cells += 1
                        else:
                            unparseable_cells += 1

        response = NormalizeResponse(
            analysis_id=analysis_id,
            status="normalized",
            total_cells=total_cells,
            normalized_cells=normalized_cells,
            unparseable_cells=unparseable_cells,
            statements=statement_results,
        )

        _normalize_store[analysis_id] = response
        logger.info(
            "Analysis %s: normalized %d/%d cells (%d unparseable)",
            analysis_id,
            normalized_cells,
            total_cells,
            unparseable_cells,
        )
        return response

    @staticmethod
    def get_result(analysis_id: str) -> NormalizeResponse | None:
        """Access the in-memory normalization results for an analysis, if present."""
        return _normalize_store.get(analysis_id)
