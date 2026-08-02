"""Growth ratios — 10 independent functions.

Measures period-over-period growth across key financial metrics.
Requires at least two periods of data.
"""

from __future__ import annotations

from app.calculations.ratios.calculation_utils import (
    ValueStore,
    interpret_margin,
    safe_growth,
)
from app.schemas.ratios import RatioResult

CATEGORY = "Growth"


def _missing(ratio: str, msg: str = "At least two periods required.") -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="missing_input", benchmark="N/A", interpretation=msg)


def _div_zero(ratio: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="division_by_zero", benchmark="N/A", interpretation="Base period is zero — growth cannot be computed.")


def _ok(ratio: str, value: float, benchmark: str, interp: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=value, status="computed", benchmark=benchmark, interpretation=interp)


def _growth_ratio(vs: ValueStore, field: str, ratio_name: str, healthy: float, concerning: float) -> RatioResult:
    periods = vs.get_all(field)
    if len(periods) < 2:
        return _missing(ratio_name, f"At least two periods of {field} are required.")
    value = safe_growth(periods[0], periods[1])
    if value is None:
        return _div_zero(ratio_name)
    return _ok(ratio_name, value, f">= {healthy:.0f}%", interpret_margin(value, healthy, concerning))


def revenue_growth(vs: ValueStore) -> RatioResult:
    return _growth_ratio(vs, "Revenue", "Revenue Growth", 10, 0)


def pat_growth(vs: ValueStore) -> RatioResult:
    return _growth_ratio(vs, "PAT", "PAT Growth", 10, 0)


def asset_growth(vs: ValueStore) -> RatioResult:
    return _growth_ratio(vs, "Total Assets", "Asset Growth", 8, 0)


def equity_growth(vs: ValueStore) -> RatioResult:
    return _growth_ratio(vs, "Equity", "Equity Growth", 8, 0)


def ebit_growth(vs: ValueStore) -> RatioResult:
    return _growth_ratio(vs, "EBIT", "EBIT Growth", 10, 0)


def ebitda_growth(vs: ValueStore) -> RatioResult:
    return _growth_ratio(vs, "EBITDA", "EBITDA Growth", 10, 0)


def current_assets_growth(vs: ValueStore) -> RatioResult:
    return _growth_ratio(vs, "Current Assets", "Current Assets Growth", 8, 0)


def current_liabilities_growth(vs: ValueStore) -> RatioResult:
    return _growth_ratio(vs, "Current Liabilities", "Current Liabilities Growth", 5, 15)


def cfo_growth(vs: ValueStore) -> RatioResult:
    return _growth_ratio(vs, "Operating Cash Flow", "CFO Growth", 10, 0)


def inventory_growth(vs: ValueStore) -> RatioResult:
    return _growth_ratio(vs, "Inventory", "Inventory Growth", 5, 15)


RATIOS = [
    revenue_growth,
    pat_growth,
    asset_growth,
    equity_growth,
    ebit_growth,
    ebitda_growth,
    current_assets_growth,
    current_liabilities_growth,
    cfo_growth,
    inventory_growth,
]
