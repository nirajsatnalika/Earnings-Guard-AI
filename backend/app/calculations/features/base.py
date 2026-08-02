"""Shared helpers for feature engineering modules."""

from __future__ import annotations

from app.calculations.ratios.calculation_utils import ValueStore
from app.schemas.features import DerivedMetric


def make_metric(
    name: str,
    category: str,
    value: float | None,
    status: str,
    formula: str,
    inputs: dict[str, float | None],
    interpretation: str,
) -> DerivedMetric:
    """Construct a DerivedMetric with all fields."""
    return DerivedMetric(
        name=name,
        category=category,
        value=value,
        status=status,
        formula=formula,
        inputs=inputs,
        interpretation=interpretation,
    )


def missing(name: str, category: str, formula: str, inputs: dict[str, float | None], msg: str = "Required field(s) missing.") -> DerivedMetric:
    return make_metric(name, category, None, "missing_input", formula, inputs, msg)


def div_zero(name: str, category: str, formula: str, inputs: dict[str, float | None]) -> DerivedMetric:
    return make_metric(name, category, None, "division_by_zero", formula, inputs, "Denominator is zero — metric cannot be computed.")


def ok(name: str, category: str, value: float, formula: str, inputs: dict[str, float | None], interpretation: str) -> DerivedMetric:
    return make_metric(name, category, value, "computed", formula, inputs, interpretation)
