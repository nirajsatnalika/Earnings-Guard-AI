"""Growth features — period-over-year growth metrics for key financial items."""

from __future__ import annotations

from app.calculations.features.base import div_zero, missing, ok
from app.calculations.ratios.calculation_utils import ValueStore, safe_divide, safe_subtract

CATEGORY = "growth"


def _growth_feature(vs: ValueStore, canonical: str, feature_name: str) -> DerivedMetric:
    periods = vs.get_all(canonical)
    inputs = {
        f"{canonical}_t": periods[0] if len(periods) >= 1 else None,
        f"{canonical}_t-1": periods[1] if len(periods) >= 2 else None,
    }
    formula = f"({canonical}_t - {canonical}_t-1) / {canonical}_t-1"
    if len(periods) < 2:
        return missing(feature_name, CATEGORY, formula, inputs, f"Two periods of {canonical} required for growth.")
    delta = safe_subtract(periods[0], periods[1])
    if delta is None:
        return missing(feature_name, CATEGORY, formula, inputs)
    value = safe_divide(delta, periods[1])
    if value is None:
        return div_zero(feature_name, CATEGORY, formula, inputs)
    interp = f"{canonical} {'grew' if value > 0 else 'declined'} by {abs(value) * 100:.1f}% over the prior year."
    return ok(feature_name, CATEGORY, value, formula, inputs, interp)


def revenue_growth(vs: ValueStore) -> DerivedMetric:
    return _growth_feature(vs, "Revenue", "revenue_growth")


def pat_growth(vs: ValueStore) -> DerivedMetric:
    return _growth_feature(vs, "PAT", "pat_growth")


def ebit_growth(vs: ValueStore) -> DerivedMetric:
    return _growth_feature(vs, "EBIT", "ebit_growth")


def ebitda_growth(vs: ValueStore) -> DerivedMetric:
    return _growth_feature(vs, "EBITDA", "ebitda_growth")


def asset_growth(vs: ValueStore) -> DerivedMetric:
    return _growth_feature(vs, "Total Assets", "asset_growth")


def equity_growth(vs: ValueStore) -> DerivedMetric:
    return _growth_feature(vs, "Equity", "equity_growth")


def cfo_growth(vs: ValueStore) -> DerivedMetric:
    return _growth_feature(vs, "Operating Cash Flow", "cfo_growth")


def inventory_growth(vs: ValueStore) -> DerivedMetric:
    return _growth_feature(vs, "Inventory", "inventory_growth")


def receivables_growth(vs: ValueStore) -> DerivedMetric:
    return _growth_feature(vs, "Receivables", "receivables_growth")


def liabilities_growth(vs: ValueStore) -> DerivedMetric:
    return _growth_feature(vs, "Total Liabilities", "liabilities_growth")


RATIOS = [
    revenue_growth,
    pat_growth,
    ebit_growth,
    ebitda_growth,
    asset_growth,
    equity_growth,
    cfo_growth,
    inventory_growth,
    receivables_growth,
    liabilities_growth,
]
