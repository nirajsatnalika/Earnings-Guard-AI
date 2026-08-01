"""Rule 8 — Confidence Validation: reject mappings below the confidence threshold.

Default threshold is 80%. Mappings below the threshold are flagged as warnings
so analysts can review and remap if needed.
"""

from __future__ import annotations

from app.calculations.validation.base import ValidationContext, make_issue
from app.schemas.validation import Severity, ValidationIssue


class ConfidenceValidationRule:
    validation_id: str = "VAL-008"
    category: str = "Confidence Validation"

    def run(self, ctx: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        threshold = ctx.confidence_threshold
        for mapped in ctx.mapped_fields:
            if mapped.confidence < threshold:
                issues.append(
                    make_issue(
                        self,
                        Severity.WARNING,
                        mapped.mapped,
                        f"Mapping '{mapped.original}' -> '{mapped.mapped}' has confidence {mapped.confidence}% (below {threshold}% threshold).",
                        "Review the mapping and add an alias or correct the source label.",
                    )
                )
        return issues
