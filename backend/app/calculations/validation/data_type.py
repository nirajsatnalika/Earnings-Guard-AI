"""Rule 2 — Data Type Validation: ensure numeric fields hold numeric values.

Handles commas, brackets (negative accounting notation), currency symbols,
and percentage signs. Flags any mapped field whose value cannot be coerced
to a number.
"""

from __future__ import annotations

import numbers
import re

import pandas as pd

from app.calculations.validation.base import ValidationContext, make_issue
from app.schemas.validation import Severity, ValidationIssue

_CURRENCY_SYMBOLS = re.compile(r"[$€£¥₹₩]")


def _coerce_numeric(value: object) -> float | None:
    """Attempt to coerce a raw cell value to float, returning None on failure."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, numbers.Number):
        return float(value)
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]

    text = _CURRENCY_SYMBOLS.sub("", text)
    text = text.replace(",", "")
    text = text.replace("%", "")
    text = text.strip()

    if not text or text in {"-", "--", "N/A", "n/a", "NA"}:
        return None

    try:
        result = float(text)
    except ValueError:
        return None
    return -result if negative else result


class DataTypeValidationRule:
    validation_id: str = "VAL-002"
    category: str = "Data Type Validation"

    def run(self, ctx: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for canonical, labels in ctx.canonical_to_labels.items():
            for raw_label in labels:
                values = _values_for_label(ctx, raw_label)
                for value in values:
                    if value is None or (isinstance(value, float) and pd.isna(value)):
                        continue
                    if _coerce_numeric(value) is None:
                        issues.append(
                            make_issue(
                                self,
                                Severity.ERROR,
                                canonical,
                                f"Field '{canonical}' (label '{raw_label}') contains non-numeric value '{value}'.",
                                "Clean the source data or correct the mapping so the value is numeric.",
                            )
                        )
        return issues


def _values_for_label(ctx: ValidationContext, raw_label: str) -> list[object]:
    """Collect all non-label cell values for a raw label across all sheets."""
    values: list[object] = []
    for sheets in ctx.frames.values():
        for frame in sheets.values():
            if frame.empty or frame.shape[1] < 2:
                continue
            label_col = frame.iloc[:, 0]
            for idx in range(len(label_col)):
                cell = label_col.iloc[idx]
                if pd.isna(cell) or str(cell).strip() != raw_label:
                    continue
                for col in range(1, frame.shape[1]):
                    values.append(frame.iat[idx, col])
    return values
