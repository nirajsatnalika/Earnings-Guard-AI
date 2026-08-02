"""Efficiency ratios — 15 independent functions.

Measures how effectively a company uses its assets to generate revenue.
"""

from __future__ import annotations

from app.calculations.ratios.calculation_utils import (
    ValueStore,
    interpret_ratio,
    safe_average,
    safe_days,
    safe_divide,
    safe_subtract,
)
from app.schemas.ratios import RatioResult

CATEGORY = "Efficiency"


def _missing(ratio: str, msg: str = "Required field(s) missing.") -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="missing_input", benchmark="N/A", interpretation=msg)


def _div_zero(ratio: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="division_by_zero", benchmark="N/A", interpretation="Denominator is zero — ratio cannot be computed.")


def _ok(ratio: str, value: float, benchmark: str, interp: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=value, status="computed", benchmark=benchmark, interpretation=interp)


def asset_turnover(vs: ValueStore) -> RatioResult:
    revenue, ta = vs.get("Revenue"), vs.get("Total Assets")
    if revenue is None or ta is None:
        return _missing("Asset Turnover")
    value = safe_divide(revenue, ta)
    if value is None:
        return _div_zero("Asset Turnover")
    return _ok("Asset Turnover", value, ">= 0.80", interpret_ratio(value, 0.8, 0.3))


def inventory_turnover(vs: ValueStore) -> RatioResult:
    revenue, inv = vs.get("Revenue"), vs.get("Inventory")
    if revenue is None or inv is None:
        return _missing("Inventory Turnover")
    value = safe_divide(revenue, inv)
    if value is None:
        return _div_zero("Inventory Turnover")
    return _ok("Inventory Turnover", value, ">= 6.0", interpret_ratio(value, 6.0, 3.0))


def receivable_turnover(vs: ValueStore) -> RatioResult:
    revenue, recv = vs.get("Revenue"), vs.get("Receivables")
    if revenue is None or recv is None:
        return _missing("Receivable Turnover")
    value = safe_divide(revenue, recv)
    if value is None:
        return _div_zero("Receivable Turnover")
    return _ok("Receivable Turnover", value, ">= 8.0", interpret_ratio(value, 8.0, 4.0))


def payable_turnover(vs: ValueStore) -> RatioResult:
    revenue, payables = vs.get("Revenue"), vs.get("Trade Payables")
    if revenue is None or payables is None:
        return _missing("Payable Turnover")
    value = safe_divide(revenue, payables)
    if value is None:
        return _div_zero("Payable Turnover")
    return _ok("Payable Turnover", value, ">= 6.0", interpret_ratio(value, 6.0, 3.0))


def fixed_asset_turnover(vs: ValueStore) -> RatioResult:
    revenue, ppe = vs.get("Revenue"), vs.get("Property Plant and Equipment")
    if revenue is None or ppe is None:
        return _missing("Fixed Asset Turnover")
    value = safe_divide(revenue, ppe)
    if value is None:
        return _div_zero("Fixed Asset Turnover")
    return _ok("Fixed Asset Turnover", value, ">= 3.0", interpret_ratio(value, 3.0, 1.0))


def equity_turnover(vs: ValueStore) -> RatioResult:
    revenue, equity = vs.get("Revenue"), vs.get("Equity")
    if revenue is None or equity is None:
        return _missing("Equity Turnover")
    value = safe_divide(revenue, equity)
    if value is None:
        return _div_zero("Equity Turnover")
    return _ok("Equity Turnover", value, ">= 2.0", interpret_ratio(value, 2.0, 0.8))


def current_asset_turnover(vs: ValueStore) -> RatioResult:
    revenue, ca = vs.get("Revenue"), vs.get("Current Assets")
    if revenue is None or ca is None:
        return _missing("Current Asset Turnover")
    value = safe_divide(revenue, ca)
    if value is None:
        return _div_zero("Current Asset Turnover")
    return _ok("Current Asset Turnover", value, ">= 2.5", interpret_ratio(value, 2.5, 1.0))


def non_current_asset_turnover(vs: ValueStore) -> RatioResult:
    revenue, nca = vs.get("Revenue"), vs.get("Non Current Assets")
    if revenue is None or nca is None:
        return _missing("Non-Current Asset Turnover")
    value = safe_divide(revenue, nca)
    if value is None:
        return _div_zero("Non-Current Asset Turnover")
    return _ok("Non-Current Asset Turnover", value, ">= 1.0", interpret_ratio(value, 1.0, 0.4))


def working_capital_turnover(vs: ValueStore) -> RatioResult:
    revenue, ca, cl = vs.get("Revenue"), vs.get("Current Assets"), vs.get("Current Liabilities")
    if revenue is None or ca is None or cl is None:
        return _missing("Working Capital Turnover")
    nwc = safe_subtract(ca, cl)
    if nwc is None or nwc == 0:
        return _div_zero("Working Capital Turnover")
    value = safe_divide(revenue, nwc)
    if value is None:
        return _div_zero("Working Capital Turnover")
    return _ok("Working Capital Turnover", value, ">= 5.0", interpret_ratio(value, 5.0, 2.0))


def total_asset_turnover(vs: ValueStore) -> RatioResult:
    revenue, ta = vs.get("Revenue"), vs.get("Total Assets")
    if revenue is None or ta is None:
        return _missing("Total Asset Turnover")
    value = safe_divide(revenue, ta)
    if value is None:
        return _div_zero("Total Asset Turnover")
    return _ok("Total Asset Turnover", value, ">= 0.80", interpret_ratio(value, 0.8, 0.3))


def inventory_to_revenue(vs: ValueStore) -> RatioResult:
    inv, revenue = vs.get("Inventory"), vs.get("Revenue")
    if inv is None or revenue is None:
        return _missing("Inventory to Revenue")
    value = safe_divide(inv, revenue)
    if value is None:
        return _div_zero("Inventory to Revenue")
    return _ok("Inventory to Revenue", value, "<= 0.20", interpret_ratio(value, 0.15, 0.3, higher_is_better=False))


def receivables_to_revenue(vs: ValueStore) -> RatioResult:
    recv, revenue = vs.get("Receivables"), vs.get("Revenue")
    if recv is None or revenue is None:
        return _missing("Receivables to Revenue")
    value = safe_divide(recv, revenue)
    if value is None:
        return _div_zero("Receivables to Revenue")
    return _ok("Receivables to Revenue", value, "<= 0.15", interpret_ratio(value, 0.12, 0.25, higher_is_better=False))


def payables_to_revenue(vs: ValueStore) -> RatioResult:
    payables, revenue = vs.get("Trade Payables"), vs.get("Revenue")
    if payables is None or revenue is None:
        return _missing("Payables to Revenue")
    value = safe_divide(payables, revenue)
    if value is None:
        return _div_zero("Payables to Revenue")
    return _ok("Payables to Revenue", value, "0.10 – 0.20", interpret_ratio(value, 0.15, 0.05))


def asset_turnover_average(vs: ValueStore) -> RatioResult:
    """Revenue / Average Total Assets (two periods)."""
    revenue = vs.get("Revenue")
    ta_periods = vs.get_all("Total Assets")
    if revenue is None or len(ta_periods) < 2:
        return _missing("Asset Turnover (Average)", "Revenue or two periods of Total Assets required.")
    avg_ta = safe_average([ta_periods[0], ta_periods[1]])
    if avg_ta is None:
        return _missing("Asset Turnover (Average)")
    value = safe_divide(revenue, avg_ta)
    if value is None:
        return _div_zero("Asset Turnover (Average)")
    return _ok("Asset Turnover (Average)", value, ">= 0.80", interpret_ratio(value, 0.8, 0.3))


def fixed_asset_turnover_average(vs: ValueStore) -> RatioResult:
    """Revenue / Average PPE (two periods)."""
    revenue = vs.get("Revenue")
    ppe_periods = vs.get_all("Property Plant and Equipment")
    if revenue is None or len(ppe_periods) < 2:
        return _missing("Fixed Asset Turnover (Average)", "Revenue or two periods of PPE required.")
    avg_ppe = safe_average([ppe_periods[0], ppe_periods[1]])
    if avg_ppe is None:
        return _missing("Fixed Asset Turnover (Average)")
    value = safe_divide(revenue, avg_ppe)
    if value is None:
        return _div_zero("Fixed Asset Turnover (Average)")
    return _ok("Fixed Asset Turnover (Average)", value, ">= 3.0", interpret_ratio(value, 3.0, 1.0))


RATIOS = [
    asset_turnover,
    inventory_turnover,
    receivable_turnover,
    payable_turnover,
    fixed_asset_turnover,
    equity_turnover,
    current_asset_turnover,
    non_current_asset_turnover,
    working_capital_turnover,
    total_asset_turnover,
    inventory_to_revenue,
    receivables_to_revenue,
    payables_to_revenue,
    asset_turnover_average,
    fixed_asset_turnover_average,
]
