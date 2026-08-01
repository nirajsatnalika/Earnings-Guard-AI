"""Rule 7 — Period Consistency: verify all statements share the same period.

Scans value-column headers across all sheets for year-like tokens. If
multiple distinct periods are detected, a warning is raised. When no period
can be detected at all, an info-level note is emitted (not an error — many
statements omit period headers).
"""

from __future__ import annotations

import re

import pandas as pd

from app.calculations.validation.base import ValidationContext, make_issue
from app.schemas.validation import Severity, ValidationIssue

_YEAR_RE = re.compile(r"(?:FY|FY-)?(\d{4})")


def _detect_periods(ctx: ValidationContext) -> set[str]:
    """Collect year-like tokens from column headers across all sheets."""
    periods: set[str] = set()
    for sheets in ctx.frames.values():
        for frame in sheets.values():
            if frame.empty or frame.shape[1] < 2:
                continue
            for col in range(1, frame.shape[1]):
                header = frame.columns[col]
                if not isinstance(header, str):
                    continue
                match = _YEAR_RE.search(header)
                if match:
                    periods.add(match.group(1))
    return periods


class PeriodConsistencyRule:
    validation_id: str = "VAL-007"
    category: str = "Period Consistency"

    def run(self, ctx: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        periods = _detect_periods(ctx)

        if len(periods) == 0:
            issues.append(
                make_issue(
                    self,
                    Severity.INFO,
                    "Period",
                    "No financial-year period detected in statement headers.",
                    "Optionally add a year column header (e.g. FY2024) to each statement for cross-statement period checks.",
                )
            )
        elif len(periods) > 1:
            issues.append(
                make_issue(
                    self,
                    Severity.WARNING,
                    "Period",
                    f"Multiple periods detected across statements: {', '.join(sorted(periods))}.",
                    "Confirm all statements cover the same financial year.",
                )
            )
        return issues
