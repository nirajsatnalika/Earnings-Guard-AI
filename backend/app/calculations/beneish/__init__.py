"""Beneish M-Score calculation package."""

from app.calculations.beneish.components import COMPONENT_FUNCTIONS
from app.calculations.beneish.model import (
    MANIPULATOR_THRESHOLD,
    compute_m_score,
    interpret_m_score,
)

__all__ = [
    "COMPONENT_FUNCTIONS",
    "MANIPULATOR_THRESHOLD",
    "compute_m_score",
    "interpret_m_score",
]
