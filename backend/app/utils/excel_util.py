"""Excel workbook reading and cleaning utility (.xlsx / .xls)."""

from __future__ import annotations

import pandas as pd

from app.core.exceptions import FileParsingError
from app.core.logging import get_logger

logger = get_logger(__name__)


def _clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop fully-blank rows/columns and trim whitespace without reordering."""
    frame = frame.dropna(how="all", axis=0)
    frame = frame.dropna(how="all", axis=1)

    # Trim whitespace on string cells and string-typed columns.
    for column in frame.columns:
        if frame[column].dtype == "object":
            frame[column] = frame[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )
    frame.columns = [
        column.strip() if isinstance(column, str) else column
        for column in frame.columns
    ]
    return frame


def parse_excel(path: str) -> dict[str, pd.DataFrame]:
    """Read every sheet of an Excel workbook into cleaned DataFrames.

    Returns a mapping of sheet name -> DataFrame. Numeric formatting is
    preserved by reading cell values as-is (no value coercion beyond what
    pandas/openpyxl performs by default).
    """
    try:
        # sheet_name=None returns {sheet_name: DataFrame} for all sheets.
        raw_sheets: dict[str, pd.DataFrame] = pd.read_excel(
            path, sheet_name=None, engine="openpyxl"
        )
    except Exception as exc:  # noqa: BLE001 - surface any read failure cleanly
        raise FileParsingError(path, str(exc)) from exc

    cleaned: dict[str, pd.DataFrame] = {}
    for sheet_name, frame in raw_sheets.items():
        cleaned_frame = _clean_frame(frame)
        cleaned[sheet_name] = cleaned_frame
        logger.debug(
            "Parsed sheet '%s' from %s: %d rows, %d columns",
            sheet_name,
            path,
            cleaned_frame.shape[0],
            cleaned_frame.shape[1],
        )
    return cleaned
