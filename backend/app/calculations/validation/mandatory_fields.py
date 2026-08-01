"""Rule 1 — Mandatory Fields: verify presence of required canonical fields."""

from __future__ import annotations

from app.calculations.validation.base import ValidationContext, make_issue
from app.schemas.validation import Severity, ValidationIssue

MANDATORY_FIELDS: list[str] = [
    "Revenue",
    "Receivables",
    "Inventory",
    "Current Assets",
    "Current Liabilities",
    "Total Assets",
    "Total Liabilities",
    "Equity",
    "PAT",
    "Operating Cash Flow",
]


class MandatoryFieldsRule:
    validation_id: str = "VAL-001"
    category: str = "Mandatory Fields"

    def run(self, ctx: ValidationContext) -> list[ValidationIssue]:
        present = set(ctx.canonical_to_labels.keys())
        issues: list[ValidationIssue] = []
        for field_name in MANDATORY_FIELDS:
            if field_name not in present:
                issues.append(
                    make_issue(
                        self,
                        Severity.ERROR,
                        field_name,
                        f"Mandatory field '{field_name}' is missing.",
                        f"Review uploaded statements and ensure '{field_name}' is present and mapped.",
                    )
                )
        return issues
