"""Rule 6 — Negative Value Validation.

Allows negatives where they make sense (depreciation, expenses, cash outflows)
and flags unexpected negatives in fields that should be positive.
"""

from __future__ import annotations

from app.calculations.validation.base import ValidationContext, make_issue
from app.calculations.validation.data_type import _coerce_numeric
from app.schemas.validation import Severity, ValidationIssue

# Fields where a negative value is expected or acceptable.
NEGATIVE_OK: set[str] = {
    "Depreciation",
    "Finance Cost",
    "Tax Expense",
    "Investing Cash Flow",
    "Financing Cash Flow",
}


class NegativeValueRule:
    validation_id: str = "VAL-006"
    category: str = "Negative Value Validation"

    def run(self, ctx: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for canonical, labels in ctx.canonical_to_labels.items():
            if canonical in NEGATIVE_OK:
                continue
            for raw_label in labels:
                value = _first_numeric_for_label(ctx, raw_label)
                if value is not None and value < 0:
                    issues.append(
                        make_issue(
                            self,
                            Severity.WARNING,
                            canonical,
                            f"Field '{canonical}' (label '{raw_label}') has an unexpected negative value ({value:,.2f}).",
                            "Confirm the sign is correct or check for bracket notation in the source.",
                        )
                    )
        return issues


def _first_numeric_for_label(ctx: ValidationContext, raw_label: str) -> float | None:
    for sheets in ctx.frames.values():
        for frame in sheets.values():
            if frame.empty or frame.shape[1] < 2:
                continue
            label_col = frame.iloc[:, 0]
            for idx in range(len(label_col)):
                cell = label_col.iloc[idx]
                if str(cell).strip() != raw_label:
                    continue
                for col in range(1, frame.shape[1]):
                    coerced = _coerce_numeric(frame.iat[idx, col])
                    if coerced is not None:
                        return coerced
    return None
