"""Core normalizer — orchestrates currency, unit, and bracket normalization.

The Normalizer reads parsed DataFrames from the Parser Engine's in-memory store
and produces a grid of NormalizedCell objects for each sheet, with full
provenance: the raw value, detected currency, detected unit, scale factor,
sign, and parseability. It does not modify the Parser's store or any other
module's state.
"""

from __future__ import annotations

import numbers

import pandas as pd

from app.calculations.normalizer.brackets import detect_negative
from app.calculations.normalizer.currency import detect_currency, strip_currency_symbols
from app.calculations.normalizer.units import detect_unit, strip_unit_qualifiers
from app.schemas.normalize import NormalizedCell, NormalizedSheetResult, NormalizedStatementResult


class Normalizer:
    """Normalizes parsed financial DataFrames into structured numeric grids."""

    @staticmethod
    def normalize(
        frames: dict[str, dict[str, pd.DataFrame]],
    ) -> list[NormalizedStatementResult]:
        """Normalize all statements for an analysis.

        Args:
            frames: The Parser's in-memory store —
                {statement_label: {sheet_name: DataFrame}}.

        Returns:
            A list of NormalizedStatementResult, one per uploaded statement.
        """
        results: list[NormalizedStatementResult] = []

        for statement_label, sheets in frames.items():
            sheet_results: list[NormalizedSheetResult] = []

            for sheet_name, frame in sheets.items():
                sheet_result = Normalizer._normalize_sheet(
                    frame, sheet_name, statement_label
                )
                sheet_results.append(sheet_result)

            results.append(
                NormalizedStatementResult(
                    statement=statement_label,
                    filename=sheet_name,
                    sheets=sheet_results,
                )
            )

        return results

    @staticmethod
    def _normalize_sheet(
        frame: pd.DataFrame,
        sheet_name: str,
        statement_label: str,
    ) -> NormalizedSheetResult:
        """Normalize a single sheet into a grid of NormalizedCell objects."""
        if frame.empty:
            return NormalizedSheetResult(
                sheet_name=sheet_name,
                statement=statement_label,
                detected_currency=None,
                detected_unit=None,
                rows=0,
                columns=0,
                cells=[],
            )

        # Detect currency and unit from the entire sheet (headers + cells).
        sheet_text = Normalizer._collect_sheet_text(frame)
        detected_currency = detect_currency(sheet_text)
        unit_name, unit_scale = detect_unit(sheet_text)

        rows = frame.shape[0]
        cols = frame.shape[1]
        cells: list[list[NormalizedCell]] = []

        for row_idx in range(rows):
            row_cells: list[NormalizedCell] = []
            for col_idx in range(cols):
                raw_value = frame.iat[row_idx, col_idx]
                cell = Normalizer._normalize_cell(raw_value, detected_currency, unit_name, unit_scale)
                row_cells.append(cell)
            cells.append(row_cells)

        return NormalizedSheetResult(
            sheet_name=sheet_name,
            statement=statement_label,
            detected_currency=detected_currency,
            detected_unit=unit_name,
            rows=rows,
            columns=cols,
            cells=cells,
        )

    @staticmethod
    def _normalize_cell(
        raw_value: object,
        sheet_currency: str | None,
        sheet_unit: str | None,
        sheet_scale: float,
    ) -> NormalizedCell:
        """Normalize a single cell value into a NormalizedCell."""
        raw_str = str(raw_value) if raw_value is not None else ""

        # Already-numeric values (int, float) pass through directly.
        if isinstance(raw_value, bool):
            return NormalizedCell(
                raw_value=raw_str,
                normalized_value=None,
                currency=sheet_currency,
                unit=sheet_unit,
                scale_factor=sheet_scale,
                is_negative=False,
                is_parseable=False,
                notes="Boolean value — not a financial figure.",
            )

        if isinstance(raw_value, numbers.Number) and not (
            isinstance(raw_value, float) and pd.isna(raw_value)
        ):
            return NormalizedCell(
                raw_value=raw_str,
                normalized_value=float(raw_value) * sheet_scale,
                currency=sheet_currency,
                unit=sheet_unit,
                scale_factor=sheet_scale,
                is_negative=float(raw_value) < 0,
                is_parseable=True,
                notes="Numeric value — scaled by detected unit." if sheet_scale != 1.0 else "Numeric value.",
            )

        if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
            return NormalizedCell(
                raw_value=raw_str,
                normalized_value=None,
                currency=sheet_currency,
                unit=sheet_unit,
                scale_factor=sheet_scale,
                is_negative=False,
                is_parseable=False,
                notes="Empty or NaN value.",
            )

        # String values — apply full normalization pipeline.
        text = raw_str.strip()
        if not text:
            return NormalizedCell(
                raw_value=raw_str,
                normalized_value=None,
                currency=sheet_currency,
                unit=sheet_unit,
                scale_factor=sheet_scale,
                is_negative=False,
                is_parseable=False,
                notes="Empty string.",
            )

        notes_parts: list[str] = []

        # Detect per-cell currency (may differ from sheet-level).
        cell_currency = detect_currency(text) or sheet_currency
        text = strip_currency_symbols(text)

        # Detect negative (brackets or minus).
        is_negative, text = detect_negative(text)
        if is_negative:
            notes_parts.append("Negative value detected (bracket or minus notation).")

        # Remove commas, percent signs, and remaining qualifiers.
        text = text.replace(",", "")
        text = text.replace("%", "")
        text = strip_unit_qualifiers(text)
        text = text.strip()

        if not text or text in {"-", "--", "N/A", "n/a", "NA", "—"}:
            return NormalizedCell(
                raw_value=raw_str,
                normalized_value=None,
                currency=cell_currency,
                unit=sheet_unit,
                scale_factor=sheet_scale,
                is_negative=False,
                is_parseable=False,
                notes="Non-numeric placeholder.",
            )

        try:
            value = float(text)
            scaled = value * sheet_scale
            if is_negative:
                scaled = -abs(scaled)
            if sheet_scale != 1.0:
                notes_parts.append(f"Scaled by {sheet_scale:.0f} ({sheet_unit}).")
            return NormalizedCell(
                raw_value=raw_str,
                normalized_value=scaled,
                currency=cell_currency,
                unit=sheet_unit,
                scale_factor=sheet_scale,
                is_negative=is_negative,
                is_parseable=True,
                notes=" ".join(notes_parts) if notes_parts else "Parsed from string.",
            )
        except ValueError:
            notes_parts.append("Could not parse as numeric.")
            return NormalizedCell(
                raw_value=raw_str,
                normalized_value=None,
                currency=cell_currency,
                unit=sheet_unit,
                scale_factor=sheet_scale,
                is_negative=is_negative,
                is_parseable=False,
                notes=" ".join(notes_parts),
            )

    @staticmethod
    def _collect_sheet_text(frame: pd.DataFrame) -> str:
        """Collect all text from a DataFrame for currency/unit detection.

        Scans column headers and the first few rows of data for currency
        symbols and unit qualifiers.
        """
        parts: list[str] = []

        # Column headers
        for col in frame.columns:
            if isinstance(col, str):
                parts.append(col)

        # First 5 rows of all cells (enough to detect headers/annotations)
        scan_rows = min(5, frame.shape[0])
        for row_idx in range(scan_rows):
            for col_idx in range(frame.shape[1]):
                val = frame.iat[row_idx, col_idx]
                if isinstance(val, str):
                    parts.append(val)

        return " ".join(parts)
