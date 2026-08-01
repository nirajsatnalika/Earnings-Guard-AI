"""CSV reading and cleaning utility."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.exceptions import FileParsingError
from app.core.logging import get_logger

logger = get_logger(__name__)


def _clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop fully-blank rows/columns and trim whitespace without reordering."""
    frame = frame.dropna(how="all", axis=0)
    frame = frame.dropna(how="all", axis=1)

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


def parse_csv(path: str) -> dict[str, pd.DataFrame]:
    """Read a CSV file into a single-sheet mapping {filename: DataFrame}.

    The CSV is treated as one logical "sheet" named after the file stem so the
    parser service can treat Excel and CSV inputs uniformly.
    """
    try:
        frame = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001 - surface any read failure cleanly
        raise FileParsingError(path, str(exc)) from exc

    cleaned = _clean_frame(frame)
    sheet_name = Path(path).stem
    logger.debug(
        "Parsed CSV %s: %d rows, %d columns",
        path,
        cleaned.shape[0],
        cleaned.shape[1],
    )
    return {sheet_name: cleaned}
