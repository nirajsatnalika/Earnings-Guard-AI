"""Working Capital ratios — 10 independent functions.

Measures working capital cycle efficiency in days and turnover terms.
"""

from __future__ import annotations

from app.calculations.ratios.calculation_utils import (
    ValueStore,
    interpret_ratio,
    safe_add,
    safe_days,
    safe_divide,
    safe_subtract,
)
from app.schemas.ratios import RatioResult

CATEGORY = "Working Capital"


def _missing(ratio: str, msg: str = "Required field(s) missing.") -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="missing_input", benchmark="N/A", interpretation=msg)


def _div_zero(ratio: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="division_by_zero", benchmark="N/A", interpretation="Denominator is zero — ratio cannot be computed.")


def _ok(ratio: str, value: float, benchmark: str, interp: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=value, status="computed", benchmark=benchmark, interpretation=interp)


def _days_helper(revenue: float | None, field_val: float | None) -> float | None:
    if revenue is None or field_val is None:
        return None
    turnover = safe_divide(revenue, field_val)
    return safe_days(turnover)


def dso(vs: ValueStore) -> RatioResult:
    recv, revenue = vs.get("Receivables"), vs.get("Revenue")
    if recv is None or revenue is None:
        return _missing("DSO")
    value = _days_helper(revenue, recv)
    if value is None:
        return _div_zero("DSO")
    return _ok("DSO", value, "<= 45 days", interpret_ratio(value, 45, 75, higher_is_better=False))


def dio(vs: ValueStore) -> RatioResult:
    inv, revenue = vs.get("Inventory"), vs.get("Revenue")
    if inv is None or revenue is None:
        return _missing("DIO")
    value = _days_helper(revenue, inv)
    if value is None:
        return _div_zero("DIO")
    return _ok("DIO", value, "<= 60 days", interpret_ratio(value, 60, 120, higher_is_better=False))


def dpo(vs: ValueStore) -> RatioResult:
    payables, revenue = vs.get("Trade Payables"), vs.get("Revenue")
    if payables is None or revenue is None:
        return _missing("DPO")
    value = _days_helper(revenue, payables)
    if value is None:
        return _div_zero("DPO")
    return _ok("DPO", value, "30 – 60 days", interpret_ratio(value, 60, 30, higher_is_better=True))


def cash_conversion_cycle(vs: ValueStore) -> RatioResult:
    revenue = vs.get("Revenue")
    if revenue is None:
        return _missing("Cash Conversion Cycle")
    dso_val = _days_helper(revenue, vs.get("Receivables"))
    dio_val = _days_helper(revenue, vs.get("Inventory"))
    dpo_val = _days_helper(revenue, vs.get("Trade Payables"))
    if dso_val is None or dio_val is None or dpo_val is None:
        return _missing("Cash Conversion Cycle")
    value = dso_val + dio_val - dpo_val
    return _ok("Cash Conversion Cycle", value, "<= 45 days", interpret_ratio(value, 45, 90, higher_is_better=False))


def net_trade_cycle(vs: ValueStore) -> RatioResult:
    """(Receivables + Inventory - Trade Payables) / Revenue * 365 — days of net working capital tied up."""
    revenue = vs.get("Revenue")
    recv, inv, payables = vs.get("Receivables"), vs.get("Inventory"), vs.get("Trade Payables")
    if revenue is None or recv is None or inv is None or payables is None:
        return _missing("Net Trade Cycle")
    nwc = safe_subtract(safe_add(recv, inv), payables)
    if nwc is None:
        return _missing("Net Trade Cycle")
    ratio = safe_divide(nwc, revenue)
    if ratio is None:
        return _div_zero("Net Trade Cycle")
    value = ratio * 365
    return _ok("Net Trade Cycle", value, "<= 60 days", interpret_ratio(value, 60, 120, higher_is_better=False))


def working_capital_to_revenue(vs: ValueStore) -> RatioResult:
    ca, cl, revenue = vs.get("Current Assets"), vs.get("Current Liabilities"), vs.get("Revenue")
    if ca is None or cl is None or revenue is None:
        return _missing("Working Capital to Revenue")
    nwc = safe_subtract(ca, cl)
    if nwc is None:
        return _missing("Working Capital to Revenue")
    value = safe_divide(nwc, revenue)
    if value is None:
        return _div_zero("Working Capital to Revenue")
    return _ok("Working Capital to Revenue", value, "0.05 – 0.20", interpret_ratio(value, 0.15, 0.0))


def inventory_days_ratio(vs: ValueStore) -> RatioResult:
    """Same as DIO but explicit alias for inventory days on hand."""
    inv, revenue = vs.get("Inventory"), vs.get("Revenue")
    if inv is None or revenue is None:
        return _missing("Inventory Days")
    value = _days_helper(revenue, inv)
    if value is None:
        return _div_zero("Inventory Days")
    return _ok("Inventory Days", value, "<= 60 days", interpret_ratio(value, 60, 120, higher_is_better=False))


def receivable_days_ratio(vs: ValueStore) -> RatioResult:
    recv, revenue = vs.get("Receivables"), vs.get("Revenue")
    if recv is None or revenue is None:
        return _missing("Receivable Days")
    value = _days_helper(revenue, recv)
    if value is None:
        return _div_zero("Receivable Days")
    return _ok("Receivable Days", value, "<= 45 days", interpret_ratio(value, 45, 75, higher_is_better=False))


def payable_days_ratio(vs: ValueStore) -> RatioResult:
    payables, revenue = vs.get("Trade Payables"), vs.get("Revenue")
    if payables is None or revenue is None:
        return _missing("Payable Days")
    value = _days_helper(revenue, payables)
    if value is None:
        return _div_zero("Payable Days")
    return _ok("Payable Days", value, "30 – 60 days", interpret_ratio(value, 60, 30, higher_is_better=True))


def operating_cycle(vs: ValueStore) -> RatioResult:
    """DSO + DIO — total days from inventory purchase to cash collection."""
    revenue = vs.get("Revenue")
    if revenue is None:
        return _missing("Operating Cycle")
    dso_val = _days_helper(revenue, vs.get("Receivables"))
    dio_val = _days_helper(revenue, vs.get("Inventory"))
    if dso_val is None or dio_val is None:
        return _missing("Operating Cycle")
    value = dso_val + dio_val
    return _ok("Operating Cycle", value, "<= 90 days", interpret_ratio(value, 90, 150, higher_is_better=False))


RATIOS = [
    dso,
    dio,
    dpo,
    cash_conversion_cycle,
    net_trade_cycle,
    working_capital_to_revenue,
    inventory_days_ratio,
    receivable_days_ratio,
    payable_days_ratio,
    operating_cycle,
]
