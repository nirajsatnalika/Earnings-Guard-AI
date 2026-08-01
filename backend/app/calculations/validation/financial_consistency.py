"""Rule 5 — Financial Consistency Checks.

Verifies accounting identities and ordering relationships across mapped
fields. All comparisons use a small tolerance to account for rounding.
"""

from __future__ import annotations

from app.calculations.validation.base import ValidationContext, make_issue
from app.calculations.validation.data_type import _coerce_numeric
from app.schemas.validation import Severity, ValidationIssue

TOLERANCE: float = 1.0  # absolute tolerance for near-equality checks


def _first_value(ctx: ValidationContext, canonical: str) -> float | None:
    """Return the first coercible numeric value for a canonical field, or None."""
    labels = ctx.canonical_to_labels.get(canonical, [])
    for raw_label in labels:
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


def _check_ge(
    ctx: ValidationContext,
    rule: "FinancialConsistencyRule",
    high: str,
    low: str,
    issues: list[ValidationIssue],
) -> None:
    """Check that *high* >= *low* and emit an issue if not."""
    high_val = _first_value(ctx, high)
    low_val = _first_value(ctx, low)
    if high_val is None or low_val is None:
        return
    if high_val + TOLERANCE < low_val:
        issues.append(
            make_issue(
                rule,
                Severity.ERROR,
                high,
                f"{high} ({high_val:,.2f}) should be >= {low} ({low_val:,.2f}).",
                f"Review the source data for {high} and {low}.",
            )
        )


class FinancialConsistencyRule:
    validation_id: str = "VAL-005"
    category: str = "Financial Consistency"

    def run(self, ctx: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        # Total Assets ≈ Total Liabilities + Equity
        total_assets = _first_value(ctx, "Total Assets")
        total_liab = _first_value(ctx, "Total Liabilities")
        equity = _first_value(ctx, "Equity")
        if total_assets is not None and total_liab is not None and equity is not None:
            expected = total_liab + equity
            if abs(total_assets - expected) > max(TOLERANCE, abs(expected) * 0.01):
                issues.append(
                    make_issue(
                        self,
                        Severity.CRITICAL,
                        "Total Assets",
                        f"Total Assets ({total_assets:,.2f}) != Total Liabilities + Equity ({expected:,.2f}).",
                        "Verify the Balance Sheet balances; check for missing or misclassified items.",
                    )
                )

        # Ordering checks (only if both sides are present)
        _check_ge(ctx, self, "Current Assets", "Cash and Cash Equivalents", issues)
        _check_ge(ctx, self, "Revenue", "EBIT", issues)
        _check_ge(ctx, self, "EBIT", "PAT", issues)

        # Cash Flow statement must contain all three sections
        for section in ("Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow"):
            if section not in ctx.canonical_to_labels:
                issues.append(
                    make_issue(
                        self,
                        Severity.WARNING,
                        section,
                        f"Cash Flow statement is missing the '{section}' section.",
                        "Ensure the uploaded Cash Flow Statement includes all three sections.",
                    )
                )

        return issues
