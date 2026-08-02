"""Liquidity ratios — 15 independent functions.

Measures a company's ability to meet short-term obligations.
"""

from __future__ import annotations

from app.calculations.ratios.calculation_utils import (
    ValueStore,
    interpret_ratio,
    safe_add,
    safe_divide,
    safe_subtract,
)
from app.schemas.ratios import RatioResult

CATEGORY = "Liquidity"


def _missing(ratio: str, msg: str = "Required field(s) missing.") -> RatioResult:
    return RatioResult(
        ratio=ratio,
        category=CATEGORY,
        value=None,
        status="missing_input",
        benchmark="N/A",
        interpretation=msg,
    )


def _div_zero(ratio: str) -> RatioResult:
    return RatioResult(
        ratio=ratio,
        category=CATEGORY,
        value=None,
        status="division_by_zero",
        benchmark="N/A",
        interpretation="Denominator is zero — ratio cannot be computed.",
    )


def _ok(ratio: str, value: float, benchmark: str, interp: str) -> RatioResult:
    return RatioResult(
        ratio=ratio,
        category=CATEGORY,
        value=value,
        status="computed",
        benchmark=benchmark,
        interpretation=interp,
    )


def current_ratio(vs: ValueStore) -> RatioResult:
    ca, cl = vs.get("Current Assets"), vs.get("Current Liabilities")
    if ca is None or cl is None:
        return _missing("Current Ratio")
    value = safe_divide(ca, cl)
    if value is None:
        return _div_zero("Current Ratio")
    return _ok("Current Ratio", value, "1.5 – 2.0", interpret_ratio(value, 1.5, 1.0))


def quick_ratio(vs: ValueStore) -> RatioResult:
    ca, inv, cl = vs.get("Current Assets"), vs.get("Inventory"), vs.get("Current Liabilities")
    if ca is None or cl is None:
        return _missing("Quick Ratio")
    inv_val = inv if inv is not None else 0.0
    numerator = safe_subtract(ca, inv_val)
    if numerator is None:
        return _missing("Quick Ratio")
    value = safe_divide(numerator, cl)
    if value is None:
        return _div_zero("Quick Ratio")
    return _ok("Quick Ratio", value, ">= 1.0", interpret_ratio(value, 1.0, 0.5))


def cash_ratio(vs: ValueStore) -> RatioResult:
    cash, cl = vs.get("Cash and Cash Equivalents"), vs.get("Current Liabilities")
    if cash is None or cl is None:
        return _missing("Cash Ratio")
    value = safe_divide(cash, cl)
    if value is None:
        return _div_zero("Cash Ratio")
    return _ok("Cash Ratio", value, "0.2 – 0.5", interpret_ratio(value, 0.5, 0.2))


def working_capital(vs: ValueStore) -> RatioResult:
    ca, cl = vs.get("Current Assets"), vs.get("Current Liabilities")
    if ca is None or cl is None:
        return _missing("Working Capital")
    value = safe_subtract(ca, cl)
    if value is None:
        return _missing("Working Capital")
    if value >= 0:
        interp = f"Positive working capital ({value:,.0f}) — short-term obligations are covered."
    else:
        interp = f"Negative working capital ({value:,.0f}) — potential short-term liquidity strain."
    return _ok("Working Capital", value, "> 0", interp)


def operating_cash_flow_ratio(vs: ValueStore) -> RatioResult:
    cfo, cl = vs.get("Operating Cash Flow"), vs.get("Current Liabilities")
    if cfo is None or cl is None:
        return _missing("Operating Cash Flow Ratio")
    value = safe_divide(cfo, cl)
    if value is None:
        return _div_zero("Operating Cash Flow Ratio")
    return _ok("Operating Cash Flow Ratio", value, ">= 1.0", interpret_ratio(value, 1.0, 0.4))


def defensive_interval_ratio(vs: ValueStore) -> RatioResult:
    """Days of cash + receivables coverage vs daily operating expenses."""
    cash, recv = vs.get("Cash and Cash Equivalents"), vs.get("Receivables")
    revenue, ebit = vs.get("Revenue"), vs.get("EBIT")
    dep = vs.get("Depreciation")
    if cash is None or recv is None or revenue is None or ebit is None:
        return _missing("Defensive Interval Ratio")
    dep_val = dep if dep is not None else 0.0
    daily_expenses = safe_subtract(safe_subtract(revenue, ebit), dep_val)
    if daily_expenses is None or daily_expenses == 0:
        return _div_zero("Defensive Interval Ratio")
    liquid_assets = safe_add(cash, recv)
    if liquid_assets is None:
        return _missing("Defensive Interval Ratio")
    value = (liquid_assets / daily_expenses) * 365
    return _ok("Defensive Interval Ratio", value, ">= 90 days", interpret_ratio(value, 90, 30))


def cash_to_current_liabilities(vs: ValueStore) -> RatioResult:
    cash, cl = vs.get("Cash and Cash Equivalents"), vs.get("Current Liabilities")
    if cash is None or cl is None:
        return _missing("Cash to Current Liabilities")
    value = safe_divide(cash, cl)
    if value is None:
        return _div_zero("Cash to Current Liabilities")
    return _ok("Cash to Current Liabilities", value, "0.2 – 0.5", interpret_ratio(value, 0.5, 0.2))


def nwc_to_total_assets(vs: ValueStore) -> RatioResult:
    """Net Working Capital / Total Assets."""
    ca, cl, ta = vs.get("Current Assets"), vs.get("Current Liabilities"), vs.get("Total Assets")
    if ca is None or cl is None or ta is None:
        return _missing("NWC to Total Assets")
    nwc = safe_subtract(ca, cl)
    if nwc is None:
        return _missing("NWC to Total Assets")
    value = safe_divide(nwc, ta)
    if value is None:
        return _div_zero("NWC to Total Assets")
    return _ok("NWC to Total Assets", value, "0.05 – 0.20", interpret_ratio(value, 0.15, 0.0))


def current_assets_to_total_assets(vs: ValueStore) -> RatioResult:
    ca, ta = vs.get("Current Assets"), vs.get("Total Assets")
    if ca is None or ta is None:
        return _missing("Current Assets to Total Assets")
    value = safe_divide(ca, ta)
    if value is None:
        return _div_zero("Current Assets to Total Assets")
    return _ok("Current Assets to Total Assets", value, "0.30 – 0.60", interpret_ratio(value, 0.4, 0.2))


def current_liabilities_to_total_liabilities(vs: ValueStore) -> RatioResult:
    cl, tl = vs.get("Current Liabilities"), vs.get("Total Liabilities")
    if cl is None or tl is None:
        return _missing("Current Liabilities to Total Liabilities")
    value = safe_divide(cl, tl)
    if value is None:
        return _div_zero("Current Liabilities to Total Liabilities")
    return _ok("Current Liabilities to Total Liabilities", value, "0.30 – 0.50", interpret_ratio(value, 0.4, 0.6, higher_is_better=False))


def inventory_to_current_assets(vs: ValueStore) -> RatioResult:
    inv, ca = vs.get("Inventory"), vs.get("Current Assets")
    if inv is None or ca is None:
        return _missing("Inventory to Current Assets")
    value = safe_divide(inv, ca)
    if value is None:
        return _div_zero("Inventory to Current Assets")
    return _ok("Inventory to Current Assets", value, "<= 0.50", interpret_ratio(value, 0.3, 0.6, higher_is_better=False))


def receivables_to_current_assets(vs: ValueStore) -> RatioResult:
    recv, ca = vs.get("Receivables"), vs.get("Current Assets")
    if recv is None or ca is None:
        return _missing("Receivables to Current Assets")
    value = safe_divide(recv, ca)
    if value is None:
        return _div_zero("Receivables to Current Assets")
    return _ok("Receivables to Current Assets", value, "0.20 – 0.40", interpret_ratio(value, 0.3, 0.5, higher_is_better=False))


def cash_to_total_assets(vs: ValueStore) -> RatioResult:
    cash, ta = vs.get("Cash and Cash Equivalents"), vs.get("Total Assets")
    if cash is None or ta is None:
        return _missing("Cash to Total Assets")
    value = safe_divide(cash, ta)
    if value is None:
        return _div_zero("Cash to Total Assets")
    return _ok("Cash to Total Assets", value, "0.05 – 0.15", interpret_ratio(value, 0.1, 0.03))


def absolute_liquidity_ratio(vs: ValueStore) -> RatioResult:
    """(Cash + Receivables) / Current Liabilities."""
    cash, recv, cl = vs.get("Cash and Cash Equivalents"), vs.get("Receivables"), vs.get("Current Liabilities")
    if cash is None or recv is None or cl is None:
        return _missing("Absolute Liquidity Ratio")
    numerator = safe_add(cash, recv)
    if numerator is None:
        return _missing("Absolute Liquidity Ratio")
    value = safe_divide(numerator, cl)
    if value is None:
        return _div_zero("Absolute Liquidity Ratio")
    return _ok("Absolute Liquidity Ratio", value, ">= 0.75", interpret_ratio(value, 0.75, 0.35))


def current_ratio_excluding_inventory(vs: ValueStore) -> RatioResult:
    """(Current Assets - Inventory) / Current Liabilities — same as Quick but explicit."""
    ca, inv, cl = vs.get("Current Assets"), vs.get("Inventory"), vs.get("Current Liabilities")
    if ca is None or cl is None:
        return _missing("Current Ratio (excl. Inventory)")
    inv_val = inv if inv is not None else 0.0
    numerator = safe_subtract(ca, inv_val)
    if numerator is None:
        return _missing("Current Ratio (excl. Inventory)")
    value = safe_divide(numerator, cl)
    if value is None:
        return _div_zero("Current Ratio (excl. Inventory)")
    return _ok("Current Ratio (excl. Inventory)", value, ">= 1.0", interpret_ratio(value, 1.0, 0.5))


RATIOS = [
    current_ratio,
    quick_ratio,
    cash_ratio,
    working_capital,
    operating_cash_flow_ratio,
    defensive_interval_ratio,
    cash_to_current_liabilities,
    nwc_to_total_assets,
    current_assets_to_total_assets,
    current_liabilities_to_total_liabilities,
    inventory_to_current_assets,
    receivables_to_current_assets,
    cash_to_total_assets,
    absolute_liquidity_ratio,
    current_ratio_excluding_inventory,
]
