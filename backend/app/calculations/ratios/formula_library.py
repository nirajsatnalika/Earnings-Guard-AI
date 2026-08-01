"""Formula library — every ratio as an independent function.

Each function receives a :class:`ValueStore` and returns a
:class:`RatioResult`. Functions are self-contained: they pull their own inputs,
handle missing values and divide-by-zero, and produce a plain-language
interpretation. New ratios can be appended to ``RATIO_FUNCTIONS`` without
touching existing code.
"""

from __future__ import annotations

from app.calculations.ratios.calculation_utils import (
    ValueStore,
    interpret_margin,
    interpret_ratio,
    safe_add,
    safe_divide,
    safe_growth,
    safe_subtract,
)
from app.schemas.ratios import RatioResult


def _missing(ratio: str, category: str, msg: str = "Required field(s) missing.") -> RatioResult:
    return RatioResult(
        ratio=ratio,
        category=category,
        value=None,
        status="missing_input",
        interpretation=msg,
    )


def _div_zero(ratio: str, category: str) -> RatioResult:
    return RatioResult(
        ratio=ratio,
        category=category,
        value=None,
        status="division_by_zero",
        interpretation="Denominator is zero — ratio cannot be computed.",
    )


# ---------------------------------------------------------------------------
# Liquidity
# ---------------------------------------------------------------------------

def current_ratio(vs: ValueStore) -> RatioResult:
    cat = "Liquidity"
    ca = vs.get("Current Assets")
    cl = vs.get("Current Liabilities")
    if ca is None or cl is None:
        return _missing("Current Ratio", cat)
    value = safe_divide(ca, cl)
    if value is None:
        return _div_zero("Current Ratio", cat)
    return RatioResult(ratio="Current Ratio", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 1.5, 1.0))


def quick_ratio(vs: ValueStore) -> RatioResult:
    cat = "Liquidity"
    ca = vs.get("Current Assets")
    inv = vs.get("Inventory")
    cl = vs.get("Current Liabilities")
    if ca is None or cl is None:
        return _missing("Quick Ratio", cat)
    inv_val = inv if inv is not None else 0.0
    numerator = safe_subtract(ca, inv_val)
    if numerator is None:
        return _missing("Quick Ratio", cat)
    value = safe_divide(numerator, cl)
    if value is None:
        return _div_zero("Quick Ratio", cat)
    return RatioResult(ratio="Quick Ratio", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 1.0, 0.5))


def cash_ratio(vs: ValueStore) -> RatioResult:
    cat = "Liquidity"
    cash = vs.get("Cash and Cash Equivalents")
    cl = vs.get("Current Liabilities")
    if cash is None or cl is None:
        return _missing("Cash Ratio", cat)
    value = safe_divide(cash, cl)
    if value is None:
        return _div_zero("Cash Ratio", cat)
    return RatioResult(ratio="Cash Ratio", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 0.5, 0.2))


def working_capital(vs: ValueStore) -> RatioResult:
    cat = "Liquidity"
    ca = vs.get("Current Assets")
    cl = vs.get("Current Liabilities")
    if ca is None or cl is None:
        return _missing("Working Capital", cat)
    value = safe_subtract(ca, cl)
    if value is None:
        return _missing("Working Capital", cat)
    if value >= 0:
        interp = f"Positive working capital ({value:,.0f}) — short-term obligations are covered."
    else:
        interp = f"Negative working capital ({value:,.0f}) — potential short-term liquidity strain."
    return RatioResult(ratio="Working Capital", category=cat, value=value, status="computed", interpretation=interp)


# ---------------------------------------------------------------------------
# Profitability
# ---------------------------------------------------------------------------

def gross_margin(vs: ValueStore) -> RatioResult:
    cat = "Profitability"
    revenue = vs.get("Revenue")
    gp = vs.get("Gross Profit")
    if revenue is None:
        return _missing("Gross Margin", cat)
    if gp is None:
        return _missing("Gross Margin", cat, "Gross Profit missing — cannot compute gross margin.")
    value = safe_divide(gp, revenue)
    if value is None:
        return _div_zero("Gross Margin", cat)
    return RatioResult(ratio="Gross Margin", category=cat, value=value, status="computed", interpretation=interpret_margin(value, 30, 10))


def operating_margin(vs: ValueStore) -> RatioResult:
    cat = "Profitability"
    revenue = vs.get("Revenue")
    ebit = vs.get("EBIT")
    if revenue is None or ebit is None:
        return _missing("Operating Margin", cat)
    value = safe_divide(ebit, revenue)
    if value is None:
        return _div_zero("Operating Margin", cat)
    return RatioResult(ratio="Operating Margin", category=cat, value=value, status="computed", interpretation=interpret_margin(value, 15, 5))


def net_margin(vs: ValueStore) -> RatioResult:
    cat = "Profitability"
    revenue = vs.get("Revenue")
    pat = vs.get("PAT")
    if revenue is None or pat is None:
        return _missing("Net Margin", cat)
    value = safe_divide(pat, revenue)
    if value is None:
        return _div_zero("Net Margin", cat)
    return RatioResult(ratio="Net Margin", category=cat, value=value, status="computed", interpretation=interpret_margin(value, 10, 3))


def return_on_assets(vs: ValueStore) -> RatioResult:
    cat = "Profitability"
    pat = vs.get("PAT")
    ta = vs.get("Total Assets")
    if pat is None or ta is None:
        return _missing("ROA", cat)
    value = safe_divide(pat, ta)
    if value is None:
        return _div_zero("ROA", cat)
    return RatioResult(ratio="ROA", category=cat, value=value, status="computed", interpretation=interpret_margin(value, 7, 2))


def return_on_equity(vs: ValueStore) -> RatioResult:
    cat = "Profitability"
    pat = vs.get("PAT")
    equity = vs.get("Equity")
    if pat is None or equity is None:
        return _missing("ROE", cat)
    value = safe_divide(pat, equity)
    if value is None:
        return _div_zero("ROE", cat)
    return RatioResult(ratio="ROE", category=cat, value=value, status="computed", interpretation=interpret_margin(value, 15, 5))


def return_on_capital_employed(vs: ValueStore) -> RatioResult:
    cat = "Profitability"
    ebit = vs.get("EBIT")
    ta = vs.get("Total Assets")
    cl = vs.get("Current Liabilities")
    if ebit is None or ta is None or cl is None:
        return _missing("ROCE", cat)
    capital_employed = safe_subtract(ta, cl)
    if capital_employed is None:
        return _missing("ROCE", cat)
    value = safe_divide(ebit, capital_employed)
    if value is None:
        return _div_zero("ROCE", cat)
    return RatioResult(ratio="ROCE", category=cat, value=value, status="computed", interpretation=interpret_margin(value, 12, 5))


# ---------------------------------------------------------------------------
# Leverage
# ---------------------------------------------------------------------------

def debt_to_equity(vs: ValueStore) -> RatioResult:
    cat = "Leverage"
    tl = vs.get("Total Liabilities")
    equity = vs.get("Equity")
    if tl is None or equity is None:
        return _missing("Debt/Equity", cat)
    value = safe_divide(tl, equity)
    if value is None:
        return _div_zero("Debt/Equity", cat)
    return RatioResult(ratio="Debt/Equity", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 1.5, 3.0, higher_is_better=False))


def debt_ratio(vs: ValueStore) -> RatioResult:
    cat = "Leverage"
    tl = vs.get("Total Liabilities")
    ta = vs.get("Total Assets")
    if tl is None or ta is None:
        return _missing("Debt Ratio", cat)
    value = safe_divide(tl, ta)
    if value is None:
        return _div_zero("Debt Ratio", cat)
    return RatioResult(ratio="Debt Ratio", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 0.5, 0.7, higher_is_better=False))


def interest_coverage(vs: ValueStore) -> RatioResult:
    cat = "Leverage"
    ebit = vs.get("EBIT")
    finance_cost = vs.get("Finance Cost")
    if ebit is None or finance_cost is None:
        return _missing("Interest Coverage", cat)
    value = safe_divide(ebit, finance_cost)
    if value is None:
        return _div_zero("Interest Coverage", cat)
    return RatioResult(ratio="Interest Coverage", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 3.0, 1.5))


# ---------------------------------------------------------------------------
# Efficiency
# ---------------------------------------------------------------------------

def asset_turnover(vs: ValueStore) -> RatioResult:
    cat = "Efficiency"
    revenue = vs.get("Revenue")
    ta = vs.get("Total Assets")
    if revenue is None or ta is None:
        return _missing("Asset Turnover", cat)
    value = safe_divide(revenue, ta)
    if value is None:
        return _div_zero("Asset Turnover", cat)
    return RatioResult(ratio="Asset Turnover", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 0.8, 0.3))


def inventory_turnover(vs: ValueStore) -> RatioResult:
    cat = "Efficiency"
    revenue = vs.get("Revenue")
    inv = vs.get("Inventory")
    if revenue is None or inv is None:
        return _missing("Inventory Turnover", cat)
    value = safe_divide(revenue, inv)
    if value is None:
        return _div_zero("Inventory Turnover", cat)
    return RatioResult(ratio="Inventory Turnover", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 6.0, 3.0))


def receivable_turnover(vs: ValueStore) -> RatioResult:
    cat = "Efficiency"
    revenue = vs.get("Revenue")
    recv = vs.get("Receivables")
    if revenue is None or recv is None:
        return _missing("Receivable Turnover", cat)
    value = safe_divide(revenue, recv)
    if value is None:
        return _div_zero("Receivable Turnover", cat)
    return RatioResult(ratio="Receivable Turnover", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 8.0, 4.0))


def payable_turnover(vs: ValueStore) -> RatioResult:
    cat = "Efficiency"
    revenue = vs.get("Revenue")
    payables = vs.get("Trade Payables")
    if revenue is None or payables is None:
        return _missing("Payable Turnover", cat)
    value = safe_divide(revenue, payables)
    if value is None:
        return _div_zero("Payable Turnover", cat)
    return RatioResult(ratio="Payable Turnover", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 6.0, 3.0))


# ---------------------------------------------------------------------------
# Working Capital (days)
# ---------------------------------------------------------------------------

def dso(vs: ValueStore) -> RatioResult:
    cat = "Working Capital"
    recv = vs.get("Receivables")
    revenue = vs.get("Revenue")
    if recv is None or revenue is None:
        return _missing("DSO", cat)
    turnover = safe_divide(revenue, recv)
    if turnover is None or turnover == 0:
        return _div_zero("DSO", cat)
    value = 365.0 / turnover
    return RatioResult(ratio="DSO", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 45, 75, higher_is_better=False))


def dio(vs: ValueStore) -> RatioResult:
    cat = "Working Capital"
    inv = vs.get("Inventory")
    revenue = vs.get("Revenue")
    if inv is None or revenue is None:
        return _missing("DIO", cat)
    turnover = safe_divide(revenue, inv)
    if turnover is None or turnover == 0:
        return _div_zero("DIO", cat)
    value = 365.0 / turnover
    return RatioResult(ratio="DIO", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 60, 120, higher_is_better=False))


def dpo(vs: ValueStore) -> RatioResult:
    cat = "Working Capital"
    payables = vs.get("Trade Payables")
    revenue = vs.get("Revenue")
    if payables is None or revenue is None:
        return _missing("DPO", cat)
    turnover = safe_divide(revenue, payables)
    if turnover is None or turnover == 0:
        return _div_zero("DPO", cat)
    value = 365.0 / turnover
    return RatioResult(ratio="DPO", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 60, 30, higher_is_better=True))


def cash_conversion_cycle(vs: ValueStore) -> RatioResult:
    cat = "Working Capital"
    dso_val = _days_metric(vs, "Receivables")
    dio_val = _days_metric(vs, "Inventory")
    dpo_val = _days_metric(vs, "Trade Payables")
    if dso_val is None or dio_val is None or dpo_val is None:
        return _missing("Cash Conversion Cycle", cat)
    value = dso_val + dio_val - dpo_val
    return RatioResult(ratio="Cash Conversion Cycle", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 45, 90, higher_is_better=False),
    )


def _days_metric(vs: ValueStore, field: str) -> float | None:
    """Helper: compute days metric (365 / turnover) for a working-capital field."""
    field_val = vs.get(field)
    revenue = vs.get("Revenue")
    if field_val is None or revenue is None:
        return None
    turnover = safe_divide(revenue, field_val)
    if turnover is None or turnover == 0:
        return None
    return 365.0 / turnover


# ---------------------------------------------------------------------------
# Cash Flow
# ---------------------------------------------------------------------------

def cfo_to_pat(vs: ValueStore) -> RatioResult:
    cat = "Cash Flow"
    cfo = vs.get("Operating Cash Flow")
    pat = vs.get("PAT")
    if cfo is None or pat is None:
        return _missing("CFO/PAT", cat)
    value = safe_divide(cfo, pat)
    if value is None:
        return _div_zero("CFO/PAT", cat)
    return RatioResult(ratio="CFO/PAT", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 1.0, 0.5))


def cfo_to_revenue(vs: ValueStore) -> RatioResult:
    cat = "Cash Flow"
    cfo = vs.get("Operating Cash Flow")
    revenue = vs.get("Revenue")
    if cfo is None or revenue is None:
        return _missing("CFO/Revenue", cat)
    value = safe_divide(cfo, revenue)
    if value is None:
        return _div_zero("CFO/Revenue", cat)
    return RatioResult(ratio="CFO/Revenue", category=cat, value=value, status="computed", interpretation=interpret_margin(value, 15, 5))


def free_cash_flow(vs: ValueStore) -> RatioResult:
    cat = "Cash Flow"
    cfo = vs.get("Operating Cash Flow")
    capex = vs.get("Property Plant and Equipment")
    if cfo is None or capex is None:
        return _missing("Free Cash Flow", cat)
    value = safe_subtract(cfo, capex)
    if value is None:
        return _missing("Free Cash Flow", cat)
    if value >= 0:
        interp = f"Positive free cash flow ({value:,.0f}) — the business generates cash after investment."
    else:
        interp = f"Negative free cash flow ({value:,.0f}) — capex exceeds operating cash generation."
    return RatioResult(ratio="Free Cash Flow", category=cat, value=value, status="computed", interpretation=interp)


def cash_conversion_ratio(vs: ValueStore) -> RatioResult:
    cat = "Cash Flow"
    cfo = vs.get("Operating Cash Flow")
    pat = vs.get("PAT")
    if cfo is None or pat is None:
        return _missing("Cash Conversion Ratio", cat)
    value = safe_divide(cfo, pat)
    if value is None:
        return _div_zero("Cash Conversion Ratio", cat)
    return RatioResult(ratio="Cash Conversion Ratio", category=cat, value=value, status="computed", interpretation=interpret_ratio(value, 1.0, 0.5))


# ---------------------------------------------------------------------------
# Growth
# ---------------------------------------------------------------------------

def revenue_growth(vs: ValueStore) -> RatioResult:
    cat = "Growth"
    periods = vs.get_all("Revenue")
    if len(periods) < 2:
        return _missing("Revenue Growth", cat, "At least two periods of Revenue are required.")
    value = safe_growth(periods[0], periods[1])
    if value is None:
        return _div_zero("Revenue Growth", cat)
    return RatioResult(ratio="Revenue Growth", category=cat, value=value, status="computed", interpretation=interpret_margin(value, 10, 0))


def pat_growth(vs: ValueStore) -> RatioResult:
    cat = "Growth"
    periods = vs.get_all("PAT")
    if len(periods) < 2:
        return _missing("PAT Growth", cat, "At least two periods of PAT are required.")
    value = safe_growth(periods[0], periods[1])
    if value is None:
        return _div_zero("PAT Growth", cat)
    return RatioResult(ratio="PAT Growth", category=cat, value=value, status="computed", interpretation=interpret_margin(value, 10, 0))


def asset_growth(vs: ValueStore) -> RatioResult:
    cat = "Growth"
    periods = vs.get_all("Total Assets")
    if len(periods) < 2:
        return _missing("Asset Growth", cat, "At least two periods of Total Assets are required.")
    value = safe_growth(periods[0], periods[1])
    if value is None:
        return _div_zero("Asset Growth", cat)
    return RatioResult(ratio="Asset Growth", category=cat, value=value, status="computed", interpretation=interpret_margin(value, 8, 0))


# ---------------------------------------------------------------------------
# Accrual
# ---------------------------------------------------------------------------

def sloan_ratio(vs: ValueStore) -> RatioResult:
    """Sloan Ratio = (Accruals / Average Total Assets).

    Accruals = Net Income − Operating Cash Flow. High accruals relative to
    assets indicate earnings driven by non-cash items.
    """
    cat = "Accrual"
    pat = vs.get("PAT")
    cfo = vs.get("Operating Cash Flow")
    ta = vs.get("Total Assets")
    if pat is None or cfo is None or ta is None:
        return _missing("Sloan Ratio", cat)
    accruals = safe_subtract(pat, cfo)
    if accruals is None:
        return _missing("Sloan Ratio", cat)
    value = safe_divide(accruals, ta)
    if value is None:
        return _div_zero("Sloan Ratio", cat)
    if abs(value) <= 0.05:
        interp = f"Low accruals ({value*100:.1f}% of assets) — earnings are largely cash-backed."
    else:
        interp = f"High accruals ({value*100:.1f}% of assets) — earnings may be driven by non-cash items."
    return RatioResult(ratio="Sloan Ratio", category=cat, value=value, status="computed", interpretation=interp)


def total_accruals(vs: ValueStore) -> RatioResult:
    """Total Accruals = Change in Working Capital.

    Measured as the change in non-cash current assets less the change in
    current liabilities. When only one period is available we fall back to
    PAT − CFO as a proxy.
    """
    cat = "Accrual"
    ca_periods = vs.get_all("Current Assets")
    cl_periods = vs.get_all("Current Liabilities")
    if len(ca_periods) >= 2 and len(cl_periods) >= 2:
        ca_delta = safe_subtract(ca_periods[0], ca_periods[1])
        cl_delta = safe_subtract(cl_periods[0], cl_periods[1])
        if ca_delta is None or cl_delta is None:
            return _missing("Total Accruals", cat)
        value = safe_subtract(ca_delta, cl_delta)
        if value is None:
            return _missing("Total Accruals", cat)
        interp = f"Working-capital change of {value:,.0f} over the period."
        return RatioResult(ratio="Total Accruals", category=cat, value=value, status="computed", interpretation=interp)

    # Fallback: PAT − CFO
    pat = vs.get("PAT")
    cfo = vs.get("Operating Cash Flow")
    if pat is None or cfo is None:
        return _missing("Total Accruals", cat, "Insufficient periods for WC change and PAT/CFO missing.")
    value = safe_subtract(pat, cfo)
    if value is None:
        return _missing("Total Accruals", cat)
    interp = f"Accruals (PAT − CFO) of {value:,.0f} — single-period fallback."
    return RatioResult(ratio="Total Accruals", category=cat, value=value, status="computed", interpretation=interp)


def working_capital_accruals(vs: ValueStore) -> RatioResult:
    """Working Capital Accruals = Δ(Current Assets) − Δ(Cash) − Δ(Current Liabilities).

    Requires two periods. Falls back to Δ(Receivables + Inventory − Trade Payables)
    when Current Assets / Cash are unavailable.
    """
    cat = "Accrual"
    ca = vs.get_all("Current Assets")
    cash = vs.get_all("Cash and Cash Equivalents")
    cl = vs.get_all("Current Liabilities")

    if len(ca) >= 2 and len(cash) >= 2 and len(cl) >= 2:
        ca_delta = safe_subtract(ca[0], ca[1])
        cash_delta = safe_subtract(cash[0], cash[1])
        cl_delta = safe_subtract(cl[0], cl[1])
        if ca_delta is None or cash_delta is None or cl_delta is None:
            return _missing("Working Capital Accruals", cat)
        value = safe_subtract(safe_subtract(ca_delta, cash_delta), cl_delta)
        if value is None:
            return _missing("Working Capital Accruals", cat)
        interp = f"WC accruals (ex-cash) of {value:,.0f} over the period."
        return RatioResult(ratio="Working Capital Accruals", category=cat, value=value, status="computed", interpretation=interp)

    # Fallback: Δ(Receivables + Inventory − Trade Payables)
    recv = vs.get_all("Receivables")
    inv = vs.get_all("Inventory")
    payables = vs.get_all("Trade Payables")
    if len(recv) >= 2 and len(inv) >= 2 and len(payables) >= 2:
        recv_delta = safe_subtract(recv[0], recv[1])
        inv_delta = safe_subtract(inv[0], inv[1])
        payables_delta = safe_subtract(payables[0], payables[1])
        if recv_delta is None or inv_delta is None or payables_delta is None:
            return _missing("Working Capital Accruals", cat)
        gross_wc = safe_add(recv_delta, inv_delta)
        if gross_wc is None:
            return _missing("Working Capital Accruals", cat)
        value = safe_subtract(gross_wc, payables_delta)
        if value is None:
            return _missing("Working Capital Accruals", cat)
        interp = f"WC accruals (component-based) of {value:,.0f} over the period."
        return RatioResult(ratio="Working Capital Accruals", category=cat, value=value, status="computed", interpretation=interp)

    return _missing(
        "Working Capital Accruals",
        cat,
        "At least two periods of working-capital components are required.",
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

RATIO_FUNCTIONS: list = [
    # Liquidity
    current_ratio,
    quick_ratio,
    cash_ratio,
    working_capital,
    # Profitability
    gross_margin,
    operating_margin,
    net_margin,
    return_on_assets,
    return_on_equity,
    return_on_capital_employed,
    # Leverage
    debt_to_equity,
    debt_ratio,
    interest_coverage,
    # Efficiency
    asset_turnover,
    inventory_turnover,
    receivable_turnover,
    payable_turnover,
    # Working Capital
    dso,
    dio,
    dpo,
    cash_conversion_cycle,
    # Cash Flow
    cfo_to_pat,
    cfo_to_revenue,
    free_cash_flow,
    cash_conversion_ratio,
    # Growth
    revenue_growth,
    pat_growth,
    asset_growth,
    # Accrual
    sloan_ratio,
    total_accruals,
    working_capital_accruals,
]
