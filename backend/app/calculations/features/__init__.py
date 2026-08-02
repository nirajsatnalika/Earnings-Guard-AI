"""Feature Engineering package — derived metrics for downstream models.

Each module groups related derived features. Every feature is an independent
function that accepts a ValueStore and returns a DerivedMetric.
"""

from app.calculations.features.averages import RATIOS as AVERAGES
from app.calculations.features.working_capital import RATIOS as WORKING_CAPITAL
from app.calculations.features.accruals import RATIOS as ACCRUALS
from app.calculations.features.cash_flow import RATIOS as CASH_FLOW
from app.calculations.features.cycles import RATIOS as CYCLES
from app.calculations.features.growth import RATIOS as GROWTH

ALL_FEATURES: list = (
    AVERAGES
    + WORKING_CAPITAL
    + ACCRUALS
    + CASH_FLOW
    + CYCLES
    + GROWTH
)

__all__ = ["ALL_FEATURES"]
