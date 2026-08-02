"""Normalizer package — Financial Data Normalizer.

Cleans and standardizes raw financial data from parsed statements:
- Multi-currency support (symbol + ISO code detection)
- Unit scaling (thousands, millions, billions, lakhs, crores)
- Negative bracket notation conversion
- Multi-year statement alignment
- Numeric coercion with provenance tracking
"""

from app.calculations.normalizer.normalizer import Normalizer

__all__ = ["Normalizer"]
