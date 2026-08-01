"""Rule 3 — Missing Values: detect blank / null / NaN mapped values."""

from __future__ import annotations

import pandas as pd

from app.calculations.validation.base import ValidationContext, make_issue
from app.schemas.validation import Severity, ValidationIssue


class MissingValuesRule:
    validation_id: str = "VAL-003"
    category: str = "Missing Values"

    def run(self, ctx: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for canonical, labels in ctx.canonical_to_labels.items():
            for raw_label in labels:
                if _is_value_missing(ctx, raw_label):
                    issues.append(
                        make_issue(
                            self,
                            Severity.WARNING,
                            canonical,
                            f"Field '{canonical}' (label '{raw_label}') has a missing or blank value.",
                            "Provide a value in the source statement or confirm the field is not applicable.",
                        )
                    )
        return issues


def _is_value_missing(ctx: ValidationContext, raw_label: str) -> bool:
    """Return True if the row for *raw_label* has no value in any value column."""
    found_any_value = False
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
                    val = frame.iat[idx, col]
                    if pd.isna(val):
                        continue
                    if isinstance(val, str) and not val.strip():
                        continue
                    found_any_value = True
                    break
                if found_any_value:
                    break
            if found_any_value:
                break
    return not found_any_value
