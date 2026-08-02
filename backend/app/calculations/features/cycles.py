"""Cycle features — cash conversion cycle and operating cycle in days."""

from __future__ import annotations

from app.calculations.features.base import div_zero, missing, ok
from app.calculations.ratios.calculation_utils import (
    ValueStore,
    safe_add,
    safe_days,
    safe_divide,
    safe_subtract,
)

CATEGORY = "cycles"


def _days(revenue: float | None, component: float | None) -> float | None:
    if revenue is None or component is None:
        return None
    turnover = safe_divide(revenue, component)
    return safe_days(turnover)


def cash_conversion_cycle(vs: ValueStore) -> DerivedMetric:
    """CCC = DSO + DIO - DPO (in days)."""
    rev = vs.get("Revenue")
    recv, inv, payables = vs.get("Receivables"), vs.get("Inventory"), vs.get("Trade Payables")
    inputs = {"Revenue": rev, "Receivables": recv, "Inventory": inv, "TradePayables": payables}
    if rev is None or recv is None or inv is None or payables is None:
        return missing("cash_conversion_cycle", CATEGORY, "DSO + DIO - DPO", inputs)
    dso_val = _days(rev, recv)
    dio_val = _days(rev, inv)
    dpo_val = _days(rev, payables)
    if dso_val is None or dio_val is None or dpo_val is None:
        return div_zero("cash_conversion_cycle", CATEGORY, "DSO + DIO - DPO", inputs)
    value = dso_val + dio_val - dpo_val
    interp = f"Cash conversion cycle of {value:.1f} days — {'efficient' if value <= 45 else 'lengthy'} working capital cycle."
    return ok("cash_conversion_cycle", CATEGORY, value, "DSO + DIO - DPO", inputs, interp)


def operating_cycle(vs: ValueStore) -> DerivedMetric:
    """Operating Cycle = DSO + DIO (in days)."""
    rev = vs.get("Revenue")
    recv, inv = vs.get("Receivables"), vs.get("Inventory")
    inputs = {"Revenue": rev, "Receivables": recv, "Inventory": inv}
    if rev is None or recv is None or inv is None:
        return missing("operating_cycle", CATEGORY, "DSO + DIO", inputs)
    dso_val = _days(rev, recv)
    dio_val = _days(rev, inv)
    if dso_val is None or dio_val is None:
        return div_zero("operating_cycle", CATEGORY, "DSO + DIO", inputs)
    value = dso_val + dio_val
    interp = f"Operating cycle of {value:.1f} days from inventory purchase to cash collection."
    return ok("operating_cycle", CATEGORY, value, "DSO + DIO", inputs, interp)


def net_trade_cycle(vs: ValueStore) -> DerivedMetric:
    """Net Trade Cycle = (Receivables + Inventory - Payables) / Revenue * 365."""
    rev = vs.get("Revenue")
    recv, inv, payables = vs.get("Receivables"), vs.get("Inventory"), vs.get("Trade Payables")
    inputs = {"Revenue": rev, "Receivables": recv, "Inventory": inv, "TradePayables": payables}
    if rev is None or recv is None or inv is None or payables is None:
        return missing("net_trade_cycle", CATEGORY, "(Recv + Inv - Pay) / Revenue * 365", inputs)
    nwc = safe_subtract(safe_add(recv, inv), payables)
    if nwc is None:
        return missing("net_trade_cycle", CATEGORY, "(Recv + Inv - Pay) / Revenue * 365", inputs)
    ratio = safe_divide(nwc, rev)
    if ratio is None:
        return div_zero("net_trade_cycle", CATEGORY, "(Recv + Inv - Pay) / Revenue * 365", inputs)
    value = ratio * 365
    interp = f"Net trade cycle of {value:.1f} days — working capital tied up in operations."
    return ok("net_trade_cycle", CATEGORY, value, "(Recv + Inv - Pay) / Revenue * 365", inputs, interp)


def dso_days(vs: ValueStore) -> DerivedMetric:
    rev, recv = vs.get("Revenue"), vs.get("Receivables")
    inputs = {"Revenue": rev, "Receivables": recv}
    if rev is None or recv is None:
        return missing("dso_days", CATEGORY, "(Receivables / Revenue) * 365", inputs)
    value = _days(rev, recv)
    if value is None:
        return div_zero("dso_days", CATEGORY, "(Receivables / Revenue) * 365", inputs)
    interp = f"Days sales outstanding of {value:.1f} days."
    return ok("dso_days", CATEGORY, value, "(Receivables / Revenue) * 365", inputs, interp)


def dio_days(vs: ValueStore) -> DerivedMetric:
    rev, inv = vs.get("Revenue"), vs.get("Inventory")
    inputs = {"Revenue": rev, "Inventory": inv}
    if rev is None or inv is None:
        return missing("dio_days", CATEGORY, "(Inventory / Revenue) * 365", inputs)
    value = _days(rev, inv)
    if value is None:
        return div_zero("dio_days", CATEGORY, "(Inventory / Revenue) * 365", inputs)
    interp = f"Days inventory outstanding of {value:.1f} days."
    return ok("dio_days", CATEGORY, value, "(Inventory / Revenue) * 365", inputs, interp)


def dpo_days(vs: ValueStore) -> DerivedMetric:
    rev, payables = vs.get("Revenue"), vs.get("Trade Payables")
    inputs = {"Revenue": rev, "TradePayables": payables}
    if rev is None or payables is None:
        return missing("dpo_days", CATEGORY, "(TradePayables / Revenue) * 365", inputs)
    value = _days(rev, payables)
    if value is None:
        return div_zero("dpo_days", CATEGORY, "(TradePayables / Revenue) * 365", inputs)
    interp = f"Days payable outstanding of {value:.1f} days."
    return ok("dpo_days", CATEGORY, value, "(TradePayables / Revenue) * 365", inputs, interp)


RATIOS = [
    cash_conversion_cycle,
    operating_cycle,
    net_trade_cycle,
    dso_days,
    dio_days,
    dpo_days,
]
