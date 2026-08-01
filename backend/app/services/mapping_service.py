"""Mapping service — maps raw parsed labels to canonical financial fields.

Reads DataFrames from the Parser Engine's in-memory store, extracts row labels
from the first column of each sheet, matches them against the canonical
dictionary + aliases using the priority matching strategy, and stores the
resulting mappings in memory for downstream engines.
"""

from __future__ import annotations

import pandas as pd

from app.calculations.mapping.matcher import MatchResult, match_label, normalize
from app.core.exceptions import AnalysisNotFoundError
from app.core.logging import get_logger
from app.schemas.mapping import MapResponse, MappedField
from app.services.parser_service import ParserService

logger = get_logger(__name__)

# In-memory store: analysis_id -> { statement_label: { sheet_name: { raw_label: MappedField } } }
_mapped_store: dict[str, dict[str, dict[str, dict[str, MappedField]]]] = {}


def _extract_labels(frame: pd.DataFrame) -> list[str]:
    """Extract row labels from the first column of a DataFrame.

    Financial statements typically have the field name in the first column and
    values in subsequent columns. We read the first column, drop NaN/blank
    entries, and preserve order.
    """
    if frame.empty or frame.shape[1] == 0:
        return []
    first_col = frame.iloc[:, 0]
    labels: list[str] = []
    for value in first_col:
        if pd.isna(value):
            continue
        normalized = normalize(str(value))
        if normalized:
            labels.append(str(value))
    return labels


class MappingService:
    """Maps parsed statement labels to canonical financial dictionary fields."""

    @staticmethod
    def map(analysis_id: str) -> MapResponse:
        frames = ParserService.get_frames(analysis_id)
        if frames is None:
            logger.warning("Map requested for unparsed analysis %s", analysis_id)
            raise AnalysisNotFoundError(analysis_id)

        mapped_fields: list[MappedField] = []
        unmapped_fields: list[str] = []
        seen_labels: set[str] = set()
        in_memory: dict[str, dict[str, dict[str, MappedField]]] = {}

        for statement_label, sheets in frames.items():
            statement_mappings: dict[str, dict[str, MappedField]] = {}
            for sheet_name, frame in sheets.items():
                sheet_mappings: dict[str, MappedField] = {}
                labels = _extract_labels(frame)
                for raw_label in labels:
                    # Deduplicate across sheets/statements — keep first occurrence.
                    if raw_label in seen_labels:
                        continue
                    seen_labels.add(raw_label)

                    result: MatchResult = match_label(raw_label)
                    if result.matched:
                        mapped = MappedField(
                            original=raw_label,
                            mapped=result.canonical,  # type: ignore[arg-type]
                            confidence=result.confidence,
                        )
                        mapped_fields.append(mapped)
                        sheet_mappings[raw_label] = mapped
                        logger.info(
                            "Mapped '%s' -> '%s' (confidence %d, strategy %s) [%s/%s]",
                            raw_label,
                            result.canonical,
                            result.confidence,
                            result.strategy,
                            statement_label,
                            sheet_name,
                        )
                    else:
                        unmapped_fields.append(raw_label)
                        logger.info(
                            "Unmapped '%s' [%s/%s]",
                            raw_label,
                            statement_label,
                            sheet_name,
                        )
                statement_mappings[sheet_name] = sheet_mappings
            in_memory[statement_label] = statement_mappings

        _mapped_store[analysis_id] = in_memory
        logger.info(
            "Analysis %s: mapped %d field(s), %d unmapped",
            analysis_id,
            len(mapped_fields),
            len(unmapped_fields),
        )
        return MapResponse(
            analysis_id=analysis_id,
            status="mapped",
            mapped_fields=mapped_fields,
            unmapped_fields=unmapped_fields,
        )

    @staticmethod
    def get_mappings(analysis_id: str) -> dict[str, dict[str, dict[str, MappedField]]] | None:
        """Access the in-memory mappings for an analysis, if present."""
        return _mapped_store.get(analysis_id)
