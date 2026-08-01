"""Rule 4 — Duplicate Detection: flag canonical fields mapped more than once."""

from __future__ import annotations

from app.calculations.validation.base import ValidationContext, make_issue
from app.schemas.validation import Severity, ValidationIssue


class DuplicateDetectionRule:
    validation_id: str = "VAL-004"
    category: str = "Duplicate Detection"

    def run(self, ctx: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for canonical, labels in ctx.canonical_to_labels.items():
            if len(labels) > 1:
                issues.append(
                    make_issue(
                        self,
                        Severity.WARNING,
                        canonical,
                        f"Field '{canonical}' was mapped {len(labels)} times from labels: {', '.join(labels)}.",
                        "Remove the duplicate row or remap so each canonical field appears only once.",
                    )
                )
        return issues
