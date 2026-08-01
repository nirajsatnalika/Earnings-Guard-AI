"""Reusable validation framework — base protocol and context object.

Each rule is a self-contained class implementing the ValidationRule protocol.
The ValidationService iterates over all registered rules, passing a shared
ValidationContext. New rules can be added by dropping a new module into this
package and registering it in the registry — no existing code changes needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import pandas as pd

from app.schemas.mapping import MappedField
from app.schemas.validation import Severity, ValidationIssue


@dataclass
class ValidationContext:
    """Shared data passed to every validation rule."""

    analysis_id: str
    mapped_fields: list[MappedField]
    unmapped_fields: list[str]
    # statement_label -> { sheet_name: DataFrame }
    frames: dict[str, dict[str, pd.DataFrame]]
    # canonical field -> list of raw labels that mapped to it
    canonical_to_labels: dict[str, list[str]] = field(default_factory=dict)
    # canonical field -> list of parsed numeric values (from first value column)
    canonical_to_values: dict[str, list[float]] = field(default_factory=dict)
    confidence_threshold: int = 80


class ValidationRule(Protocol):
    """Protocol every validation rule implements."""

    validation_id: str
    category: str

    def run(self, ctx: ValidationContext) -> list[ValidationIssue]:
        ...


def make_issue(
    rule: ValidationRule,
    severity: Severity,
    field_name: str,
    message: str,
    recommendation: str,
) -> ValidationIssue:
    """Helper to construct a ValidationIssue from a rule."""
    return ValidationIssue(
        validation_id=rule.validation_id,
        category=rule.category,
        severity=severity,
        field=field_name,
        message=message,
        recommendation=recommendation,
    )
