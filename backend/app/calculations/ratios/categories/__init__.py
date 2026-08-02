"""Ratio categories package.

Each module in this package groups ratio functions by financial category
(liquidity, profitability, leverage, etc.). Every module exposes a
``RATIOS`` list of callables that accept a :class:`ValueStore` and return a
:class:`RatioResult`.
"""

from app.calculations.ratios.categories.liquidity import RATIOS as LIQUIDITY
from app.calculations.ratios.categories.profitability import RATIOS as PROFITABILITY
from app.calculations.ratios.categories.leverage import RATIOS as LEVERAGE
from app.calculations.ratios.categories.efficiency import RATIOS as EFFICIENCY
from app.calculations.ratios.categories.working_capital import RATIOS as WORKING_CAPITAL
from app.calculations.ratios.categories.cash_flow import RATIOS as CASH_FLOW
from app.calculations.ratios.categories.growth import RATIOS as GROWTH
from app.calculations.ratios.categories.accrual import RATIOS as ACCRUAL

ALL_RATIOS: list = (
    LIQUIDITY
    + PROFITABILITY
    + LEVERAGE
    + EFFICIENCY
    + WORKING_CAPITAL
    + CASH_FLOW
    + GROWTH
    + ACCRUAL
)

__all__ = ["ALL_RATIOS"]
