"""Accrual ratios — 5 independent functions.

Measures the quality of earnings by assessing the proportion of profits
backed by cash flow vs. non-cash accruals.
"""

from __future__ import annotations

from app.calculations.ratios.calculation_utils import (
    ValueStore,
    safe_add,
    safe_average,
    safe_divide,
    safe_subtract,
)
from app.schemas.ratios import RatioResult

CATEGORY = "Accrual"


def _missing(ratio: str, msg: str = "Required field(s) missing.") -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="missing_input", benchmark="N/A", interpretation=msg)


def _div_zero(ratio: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="division_by_zero", benchmark="N/A", interpretation="Denominator is zero — ratio cannot be computed.")


def _ok(ratio: str, value: float, benchmark: str, interp: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=value, status="computed", benchmark=benchmark, interpretation=interp)


def sloan_ratio(vs: ValueStore) -> RatioResult:
    """Sloan Ratio = (PAT - CFO) / Average Total Assets."""
    pat, cfo = vs.get("PAT"), vs.get("Operating Cash Flow")
    ta_periods = vs.get_all("Total Assets")
    if pat is None or cfo is None:
        return _missing("Sloan Ratio")
    if len(ta_periods) >= 2:
        avg_ta = safe_average([ta_periods[0], ta_periods[1]])
    else:
        avg_ta = vs.get("Total Assets")
    if avg_ta is None:
        return _missing("Sloan Ratio")
    accruals = safe_subtract(pat, cfo)
    if accruals is None:
        return _missing("Sloan Ratio")
    value = safe_divide(accruals, avg_ta)
    if value is None:
        return _div_zero("Sloan Ratio")
    if abs(value) <= 0.05:
        interp = f"Low accruals ({value*100:.1f}% of assets) — earnings are largely cash-backed."
    else:
        interp = f"High accruals ({value*100:.1f}% of assets) — earnings may be driven by non-cash items."
    return _ok("Sloan Ratio", value, "|ratio| <= 5%", interp)


def total_accruals(vs: ValueStore) -> RatioResult:
    """Total Accruals = Δ(Current Assets) - Δ(Current Liabilities)."""
    ca_periods = vs.get_all("Current Assets")
    cl_periods = vs.get_all("Current Liabilities")
    if len(ca_periods) >= 2 and len(cl_periods) >= 2:
        ca_delta = safe_subtract(ca_periods[0], ca_periods[1])
        cl_delta = safe_subtract(cl_periods[0], cl_periods[1])
        if ca_delta is None or cl_delta is None:
            return _missing("Total Accruals")
        value = safe_subtract(ca_delta, cl_delta)
        if value is None:
            return _missing("Total Accruals")
        interp = f"Working-capital change of {value:,.0f} over the period."
        return _ok("Total Accruals", value, "Lower is better", interp)

    # Fallback: PAT - CFO
    pat, cfo = vs.get("PAT"), vs.get("Operating Cash Flow")
    if pat is None or cfo is None:
        return _missing("Total Accruals", "Insufficient periods for WC change and PAT/CFO missing.")
    value = safe_subtract(pat, cfo)
    if value is None:
        return _missing("Total Accruals")
    interp = f"Accruals (PAT - CFO) of {value:,.0f} — single-period fallback."
    return _ok("Total Accruals", value, "Lower is better", interp)


def working_capital_accruals(vs: ValueStore) -> RatioResult:
    """WC Accruals = Δ(Current Assets) - Δ(Cash) - Δ(Current Liabilities)."""
    ca = vs.get_all("Current Assets")
    cash = vs.get_all("Cash and Cash Equivalents")
    cl = vs.get_all("Current Liabilities")

    if len(ca) >= 2 and len(cash) >= 2 and len(cl) >= 2:
        ca_delta = safe_subtract(ca[0], ca[1])
        cash_delta = safe_subtract(cash[0], cash[1])
        cl_delta = safe_subtract(cl[0], cl[1])
        if ca_delta is None or cash_delta is None or cl_delta is None:
            return _missing("Working Capital Accruals")
        value = safe_subtract(safe_subtract(ca_delta, cash_delta), cl_delta)
        if value is None:
            return _missing("Working Capital Accruals")
        interp = f"WC accruals (ex-cash) of {value:,.0f} over the period."
        return _ok("Working Capital Accruals", value, "Lower is better", interp)

    # Fallback: Δ(Receivables + Inventory - Trade Payables)
    recv = vs.get_all("Receivables")
    inv = vs.get_all("Inventory")
    payables = vs.get_all("Trade Payables")
    if len(recv) >= 2 and len(inv) >= 2 and len(payables) >= 2:
        recv_delta = safe_subtract(recv[0], recv[1])
        inv_delta = safe_subtract(inv[0], inv[1])
        payables_delta = safe_subtract(payables[0], payables[1])
        if recv_delta is None or inv_delta is None or payables_delta is None:
            return _missing("Working Capital Accruals")
        gross_wc = safe_add(recv_delta, inv_delta)
        if gross_wc is None:
            return _missing("Working Capital Accruals")
        value = safe_subtract(gross_wc, payables_delta)
        if value is None:
            return _missing("Working Capital Accruals")
        interp = f"WC accruals (component-based) of {value:,.0f} over the period."
        return _ok("Working Capital Accruals", value, "Lower is better", interp)

    return _missing("Working Capital Accruals", "At least two periods of working-capital components are required.")


def accruals_to_assets(vs: ValueStore) -> RatioResult:
    """(PAT - CFO) / Total Assets — accruals relative to asset base."""
    pat, cfo, ta = vs.get("PAT"), vs.get("Operating Cash Flow"), vs.get("Total Assets")
    if pat is None or cfo is None or ta is None:
        return _missing("Accruals to Assets")
    accruals = safe_subtract(pat, cfo)
    if accruals is None:
        return _missing("Accruals to Assets")
    value = safe_divide(accruals, ta)
    if value is None:
        return _div_zero("Accruals to Assets")
    if abs(value) <= 0.05:
        interp = f"Low accruals ({value*100:.1f}% of assets) — earnings quality is good."
    else:
        interp = f"High accruals ({value*100:.1f}% of assets) — earnings quality may be poor."
    return _ok("Accruals to Assets", value, "|ratio| <= 5%", interp)


def accruals_to_revenue(vs: ValueStore) -> RatioResult:
    """(PAT - CFO) / Revenue — accruals relative to revenue."""
    pat, cfo, revenue = vs.get("PAT"), vs.get("Operating Cash Flow"), vs.get("Revenue")
    if pat is None or cfo is None or revenue is None:
        return _missing("Accruals to Revenue")
    accruals = safe_subtract(pat, cfo)
    if accruals is None:
        return _missing("Accruals to Revenue")
    value = safe_divide(accruals, revenue)
    if value is None:
        return _div_zero("Accruals to Revenue")
    if abs(value) <= 0.05:
        interp = f"Low accruals ({value*100:.1f}% of revenue) — earnings quality is good."
    else:
        interp = f"High accruals ({value*100:.1f}% of revenue) — earnings quality may be poor."
    return _ok("Accruals to Revenue", value, "|ratio| <= 5%", interp)


RATIOS = [
    sloan_ratio,
    total_accruals,
    working_capital_accruals,
    accruals_to_assets,
    accruals_to_revenue,
]
