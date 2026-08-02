"""Leverage ratios — 15 independent functions.

Measures the extent to which a company uses debt financing and its ability
to service debt obligations.
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

CATEGORY = "Leverage"


def _missing(ratio: str, msg: str = "Required field(s) missing.") -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="missing_input", benchmark="N/A", interpretation=msg)


def _div_zero(ratio: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=None, status="division_by_zero", benchmark="N/A", interpretation="Denominator is zero — ratio cannot be computed.")


def _ok(ratio: str, value: float, benchmark: str, interp: str) -> RatioResult:
    return RatioResult(ratio=ratio, category=CATEGORY, value=value, status="computed", benchmark=benchmark, interpretation=interp)


def debt_to_equity(vs: ValueStore) -> RatioResult:
    tl, equity = vs.get("Total Liabilities"), vs.get("Equity")
    if tl is None or equity is None:
        return _missing("Debt/Equity")
    value = safe_divide(tl, equity)
    if value is None:
        return _div_zero("Debt/Equity")
    return _ok("Debt/Equity", value, "<= 1.5", interpret_ratio(value, 1.5, 3.0, higher_is_better=False))


def debt_ratio(vs: ValueStore) -> RatioResult:
    tl, ta = vs.get("Total Liabilities"), vs.get("Total Assets")
    if tl is None or ta is None:
        return _missing("Debt Ratio")
    value = safe_divide(tl, ta)
    if value is None:
        return _div_zero("Debt Ratio")
    return _ok("Debt Ratio", value, "<= 0.50", interpret_ratio(value, 0.5, 0.7, higher_is_better=False))


def interest_coverage(vs: ValueStore) -> RatioResult:
    ebit, fc = vs.get("EBIT"), vs.get("Finance Cost")
    if ebit is None or fc is None:
        return _missing("Interest Coverage")
    value = safe_divide(ebit, fc)
    if value is None:
        return _div_zero("Interest Coverage")
    return _ok("Interest Coverage", value, ">= 3.0", interpret_ratio(value, 3.0, 1.5))


def equity_ratio(vs: ValueStore) -> RatioResult:
    """Equity / Total Assets — proportion of assets funded by equity."""
    equity, ta = vs.get("Equity"), vs.get("Total Assets")
    if equity is None or ta is None:
        return _missing("Equity Ratio")
    value = safe_divide(equity, ta)
    if value is None:
        return _div_zero("Equity Ratio")
    return _ok("Equity Ratio", value, ">= 0.50", interpret_ratio(value, 0.5, 0.3))


def equity_multiplier(vs: ValueStore) -> RatioResult:
    """Total Assets / Equity — leverage amplification factor."""
    ta, equity = vs.get("Total Assets"), vs.get("Equity")
    if ta is None or equity is None:
        return _missing("Equity Multiplier")
    value = safe_divide(ta, equity)
    if value is None:
        return _div_zero("Equity Multiplier")
    return _ok("Equity Multiplier", value, "<= 2.0", interpret_ratio(value, 2.0, 4.0, higher_is_better=False))


def debt_to_assets(vs: ValueStore) -> RatioResult:
    tl, ta = vs.get("Total Liabilities"), vs.get("Total Assets")
    if tl is None or ta is None:
        return _missing("Debt to Assets")
    value = safe_divide(tl, ta)
    if value is None:
        return _div_zero("Debt to Assets")
    return _ok("Debt to Assets", value, "<= 0.50", interpret_ratio(value, 0.5, 0.7, higher_is_better=False))


def long_term_debt_to_equity(vs: ValueStore) -> RatioResult:
    """(Total Liabilities - Current Liabilities) / Equity — proxy for LT debt/equity."""
    tl, cl, equity = vs.get("Total Liabilities"), vs.get("Current Liabilities"), vs.get("Equity")
    if tl is None or cl is None or equity is None:
        return _missing("Long-Term Debt to Equity")
    lt_debt = safe_subtract(tl, cl)
    if lt_debt is None:
        return _missing("Long-Term Debt to Equity")
    value = safe_divide(lt_debt, equity)
    if value is None:
        return _div_zero("Long-Term Debt to Equity")
    return _ok("Long-Term Debt to Equity", value, "<= 1.0", interpret_ratio(value, 1.0, 2.0, higher_is_better=False))


def debt_to_capital(vs: ValueStore) -> RatioResult:
    """Total Liabilities / (Total Liabilities + Equity)."""
    tl, equity = vs.get("Total Liabilities"), vs.get("Equity")
    if tl is None or equity is None:
        return _missing("Debt to Capital")
    total_capital = safe_add(tl, equity)
    if total_capital is None:
        return _missing("Debt to Capital")
    value = safe_divide(tl, total_capital)
    if value is None:
        return _div_zero("Debt to Capital")
    return _ok("Debt to Capital", value, "<= 0.40", interpret_ratio(value, 0.4, 0.6, higher_is_better=False))


def ebitda_to_interest(vs: ValueStore) -> RatioResult:
    ebitda, fc = vs.get("EBITDA"), vs.get("Finance Cost")
    if ebitda is None or fc is None:
        return _missing("EBITDA to Interest")
    value = safe_divide(ebitda, fc)
    if value is None:
        return _div_zero("EBITDA to Interest")
    return _ok("EBITDA to Interest", value, ">= 4.0", interpret_ratio(value, 4.0, 2.0))


def ebitda_to_debt(vs: ValueStore) -> RatioResult:
    ebitda, tl = vs.get("EBITDA"), vs.get("Total Liabilities")
    if ebitda is None or tl is None:
        return _missing("EBITDA to Debt")
    value = safe_divide(ebitda, tl)
    if value is None:
        return _div_zero("EBITDA to Debt")
    return _ok("EBITDA to Debt", value, ">= 0.30", interpret_ratio(value, 0.3, 0.1))


def liabilities_to_equity(vs: ValueStore) -> RatioResult:
    tl, equity = vs.get("Total Liabilities"), vs.get("Equity")
    if tl is None or equity is None:
        return _missing("Liabilities to Equity")
    value = safe_divide(tl, equity)
    if value is None:
        return _div_zero("Liabilities to Equity")
    return _ok("Liabilities to Equity", value, "<= 1.0", interpret_ratio(value, 1.0, 2.0, higher_is_better=False))


def current_liabilities_to_equity(vs: ValueStore) -> RatioResult:
    cl, equity = vs.get("Current Liabilities"), vs.get("Equity")
    if cl is None or equity is None:
        return _missing("Current Liabilities to Equity")
    value = safe_divide(cl, equity)
    if value is None:
        return _div_zero("Current Liabilities to Equity")
    return _ok("Current Liabilities to Equity", value, "<= 0.50", interpret_ratio(value, 0.5, 1.0, higher_is_better=False))


def non_current_liabilities_to_equity(vs: ValueStore) -> RatioResult:
    tl, cl, equity = vs.get("Total Liabilities"), vs.get("Current Liabilities"), vs.get("Equity")
    if tl is None or cl is None or equity is None:
        return _missing("Non-Current Liabilities to Equity")
    ncl = safe_subtract(tl, cl)
    if ncl is None:
        return _missing("Non-Current Liabilities to Equity")
    value = safe_divide(ncl, equity)
    if value is None:
        return _div_zero("Non-Current Liabilities to Equity")
    return _ok("Non-Current Liabilities to Equity", value, "<= 0.50", interpret_ratio(value, 0.5, 1.0, higher_is_better=False))


def ebit_to_interest(vs: ValueStore) -> RatioResult:
    ebit, fc = vs.get("EBIT"), vs.get("Finance Cost")
    if ebit is None or fc is None:
        return _missing("EBIT to Interest")
    value = safe_divide(ebit, fc)
    if value is None:
        return _div_zero("EBIT to Interest")
    return _ok("EBIT to Interest", value, ">= 3.0", interpret_ratio(value, 3.0, 1.5))


def pat_to_interest(vs: ValueStore) -> RatioResult:
    pat, fc = vs.get("PAT"), vs.get("Finance Cost")
    if pat is None or fc is None:
        return _missing("PAT to Interest")
    value = safe_divide(pat, fc)
    if value is None:
        return _div_zero("PAT to Interest")
    return _ok("PAT to Interest", value, ">= 2.0", interpret_ratio(value, 2.0, 1.0))


RATIOS = [
    debt_to_equity,
    debt_ratio,
    interest_coverage,
    equity_ratio,
    equity_multiplier,
    debt_to_assets,
    long_term_debt_to_equity,
    debt_to_capital,
    ebitda_to_interest,
    ebitda_to_debt,
    liabilities_to_equity,
    current_liabilities_to_equity,
    non_current_liabilities_to_equity,
    ebit_to_interest,
    pat_to_interest,
]
