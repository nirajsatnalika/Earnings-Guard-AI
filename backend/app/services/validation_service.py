"""Validation service — runs all rules and generates a validation report.

Reads mappings from the Mapping Engine's in-memory store, builds a
ValidationContext, executes every registered rule, and returns a structured
validation report. Results are also held in an in-memory store for downstream
engines.
"""

from __future__ import annotations

import pandas as pd

from app.calculations.validation.base import ValidationContext
from app.calculations.validation.registry import RULES
from app.core.exceptions import AnalysisNotFoundError
from app.core.logging import get_logger
from app.schemas.mapping import MappedField
from app.schemas.validation import (
    Severity,
    ValidationIssue,
    ValidationResponse,
    ValidationSummary,
)
from app.services.mapping_service import MappingService
from app.services.parser_service import ParserService

logger = get_logger(__name__)

DEFAULT_CONFIDENCE_THRESHOLD: int = 80

# In-memory store: analysis_id -> ValidationResponse
_validation_store: dict[str, ValidationResponse] = {}

_SEVERITY_WEIGHTS: dict[Severity, int] = {
    Severity.INFO: 0,
    Severity.WARNING: 1,
    Severity.ERROR: 3,
    Severity.CRITICAL: 10,
}


def _build_context(analysis_id: str, threshold: int) -> ValidationContext:
    """Assemble the shared context from parser + mapping stores."""
    frames = ParserService.get_frames(analysis_id) or {}
    mappings = MappingService.get_mappings(analysis_id) or {}

    mapped_fields: list[MappedField] = []
    canonical_to_labels: dict[str, list[str]] = {}
    for statement_mappings in mappings.values():
        for sheet_mappings in statement_mappings.values():
            for raw_label, mapped in sheet_mappings.items():
                mapped_fields.append(mapped)
                canonical_to_labels.setdefault(mapped.mapped, []).append(raw_label)

    unmapped_fields: list[str] = []
    for statement_mappings in mappings.values():
        for sheet_mappings in statement_mappings.values():
            pass  # unmapped fields are tracked in MapResponse, not per-sheet

    return ValidationContext(
        analysis_id=analysis_id,
        mapped_fields=mapped_fields,
        unmapped_fields=unmapped_fields,
        frames=frames,
        canonical_to_labels=canonical_to_labels,
        canonical_to_values={},
        confidence_threshold=threshold,
    )


def _compute_score(total_checks: int, issues: list[ValidationIssue]) -> int:
    """Derive a 0–100 validation score from issue severity and count."""
    if total_checks == 0:
        return 100
    penalty = sum(_SEVERITY_WEIGHTS[issue.severity] for issue in issues)
    max_penalty = total_checks * _SEVERITY_WEIGHTS[Severity.CRITICAL]
    if max_penalty == 0:
        return 100
    score = max(0, 100 - round((penalty / max_penalty) * 100))
    return score


class ValidationService:
    """Validates mapped financial statements and produces a report."""

    @staticmethod
    def validate(
        analysis_id: str,
        confidence_threshold: int = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> ValidationResponse:
        mappings = MappingService.get_mappings(analysis_id)
        if mappings is None:
            logger.warning("Validate requested for unmapped analysis %s", analysis_id)
            raise AnalysisNotFoundError(analysis_id)

        ctx = _build_context(analysis_id, confidence_threshold)

        all_issues: list[ValidationIssue] = []
        passed = 0

        for rule in RULES:
            issues = rule.run(ctx)
            if not issues:
                passed += 1
                logger.info(
                    "Analysis %s: rule %s PASSED (%s)",
                    analysis_id,
                    rule.validation_id,
                    rule.category,
                )
            else:
                for issue in issues:
                    all_issues.append(issue)
                    logger.log(
                        {
                            Severity.INFO: 20,
                            Severity.WARNING: 30,
                            Severity.ERROR: 40,
                            Severity.CRITICAL: 50,
                        }[issue.severity],
                        "Analysis %s: %s | %s | %s | %s",
                        analysis_id,
                        issue.validation_id,
                        issue.severity.value,
                        issue.field,
                        issue.message,
                    )

        warnings = sum(1 for i in all_issues if i.severity == Severity.WARNING)
        errors = sum(1 for i in all_issues if i.severity == Severity.ERROR)
        critical = sum(1 for i in all_issues if i.severity == Severity.CRITICAL)

        total_checks = len(RULES)
        score = _compute_score(total_checks, all_issues)

        summary = ValidationSummary(
            passed=passed,
            warnings=warnings,
            errors=errors,
            critical=critical,
        )
        response = ValidationResponse(
            analysis_id=analysis_id,
            status="validated",
            summary=summary,
            issues=all_issues,
            validation_score=score,
        )

        _validation_store[analysis_id] = response
        logger.info(
            "Analysis %s: validation complete — passed %d, warnings %d, errors %d, critical %d, score %d",
            analysis_id,
            passed,
            warnings,
            errors,
            critical,
            score,
        )
        return response

    @staticmethod
    def get_report(analysis_id: str) -> ValidationResponse | None:
        """Access the in-memory validation report for an analysis, if present."""
        return _validation_store.get(analysis_id)
