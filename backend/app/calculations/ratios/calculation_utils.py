"""Calculation utilities — value extraction and safe arithmetic helpers.

These helpers bridge the parsed DataFrames + canonical-to-label mapping into
the simple ``float | None`` inputs that every ratio function in the formula
library expects. They also provide divide-safe wrappers so ratio functions
never need to repeat boilerplate guard logic.
"""

from __future__ import annotations

import numbers
import re
from typing import Callable

import pandas as pd

from app.calculations.validation.data_type import _coerce_numeric

_CURRENCY_SYMBOLS = re.compile(r"[$€£¥₹₩]")


class ValueStore:
    """Read-only accessor for canonical field values.

    Built once per analysis from the parsed DataFrames and the canonical-to-label
    mapping. Each canonical field resolves to its first coercible numeric value
    across all sheets and statements. Multi-period columns are stored in order
    so growth ratios can compute period-over-period deltas.
    """

    def __init__(
        self,
        frames: dict[str, dict[str, pd.DataFrame]],
        canonical_to_labels: dict[str, list[str]],
    ) -> None:
        self._values: dict[str, list[float]] = {}
        for canonical, labels in canonical_to_labels.items():
            collected = _collect_values_for_labels(frames, labels)
            if collected:
                self._values[canonical] = collected

    def get(self, canonical: str) -> float | None:
        """Return the first numeric value for *canonical*, or None."""
        values = self._values.get(canonical)
        if not values:
            return None
        return values[0]

    def get_all(self, canonical: str) -> list[float]:
        """Return all numeric values for *canonical* (period 0, 1, …)."""
        return list(self._values.get(canonical, []))


def _collect_values_for_labels(
    frames: dict[str, dict[str, pd.DataFrame]],
    labels: list[str],
) -> list[float]:
    """Collect coercible numeric values for a set of raw labels across sheets.

    Values are collected per period-column in order (column 1, then 2, …) so
    that growth ratios have ordered time series.
    """
    if not labels:
        return []

    # Determine the maximum number of value columns across all matching rows.
    max_cols = 1
    matches: list[tuple[pd.DataFrame, int]] = []
    for sheets in frames.values():
        for frame in sheets.values():
            if frame.empty or frame.shape[1] < 2:
                continue
            label_col = frame.iloc[:, 0]
            for idx in range(len(label_col)):
                cell = label_col.iloc[idx]
                if pd.isna(cell):
                    continue
                if str(cell).strip() in labels:
                    matches.append((frame, idx))
                    max_cols = max(max_cols, frame.shape[1])

    if not matches:
        return []

    # For each value column, take the first coercible value across all matches.
    result: list[float] = []
    for col in range(1, max_cols):
        for frame, idx in matches:
            if col >= frame.shape[1]:
                continue
            coerced = _coerce_numeric(frame.iat[idx, col])
            if coerced is not None:
                result.append(coerced)
                break
    return result


# ---------------------------------------------------------------------------
# Safe arithmetic helpers
# ---------------------------------------------------------------------------

def safe_divide(
    numerator: float | None,
    denominator: float | None,
) -> float | None:
    """Divide two values, returning None for missing inputs or zero denominator."""
    if numerator is None or denominator is None:
        return None
    if denominator == 0:
        return None
    return numerator / denominator


def safe_subtract(a: float | None, b: float | None) -> float | None:
    """Subtract two values, returning None if either is missing."""
    if a is None or b is None:
        return None
    return a - b


def safe_add(a: float | None, b: float | None) -> float | None:
    """Add two values, returning None if either is missing."""
    if a is None or b is None:
        return None
    return a + b


def safe_growth(current: float | None, previous: float | None) -> float | None:
    """Compute period-over-period growth rate, returning None on missing/zero base."""
    if current is None or previous is None:
        return None
    if previous == 0:
        return None
    return (current - previous) / abs(previous)


def interpret_ratio(
    value: float | None,
    good_threshold: float,
    bad_threshold: float,
    higher_is_better: bool = True,
) -> str:
    """Generate a plain-language interpretation for a ratio value.

    Returns a human-readable string describing whether the value is healthy,
    concerning, or could not be computed.
    """
    if value is None:
        return "Could not be computed due to missing inputs or division by zero."
    if higher_is_better:
        if value >= good_threshold:
            return f"Healthy ({value:.2f}) — above the healthy benchmark of {good_threshold:.2f}."
        if value <= bad_threshold:
            return f"Concerning ({value:.2f}) — below the caution benchmark of {bad_threshold:.2f}."
        return f"Moderate ({value:.2f}) — between caution ({bad_threshold:.2f}) and healthy ({good_threshold:.2f}) benchmarks."
    else:
        if value <= good_threshold:
            return f"Healthy ({value:.2f}) — below the healthy benchmark of {good_threshold:.2f}."
        if value >= bad_threshold:
            return f"Concerning ({value:.2f}) — above the caution benchmark of {bad_threshold:.2f}."
        return f"Moderate ({value:.2f}) — between healthy ({good_threshold:.2f}) and caution ({bad_threshold:.2f}) benchmarks."


def interpret_margin(value: float | None, healthy_pct: float, concerning_pct: float) -> str:
    """Interpret a margin ratio expressed as a decimal (0.15 = 15%)."""
    if value is None:
        return "Could not be computed due to missing inputs or division by zero."
    pct = value * 100
    if pct >= healthy_pct:
        return f"Strong margin ({pct:.1f}%) — above the healthy benchmark of {healthy_pct:.0f}%."
    if pct <= concerning_pct:
        return f"Weak margin ({pct:.1f}%) — below the caution benchmark of {concerning_pct:.0f}%."
    return f"Moderate margin ({pct:.1f}%) — between {concerning_pct:.0f}% and {healthy_pct:.0f}%."
