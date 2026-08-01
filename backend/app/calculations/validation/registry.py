"""Validation rule registry.

All rules are instantiated once and exposed via ``RULES``. To add a new rule,
create a module in this package and append its instance here — no other code
needs to change.
"""

from __future__ import annotations

from app.calculations.validation.base import ValidationRule
from app.calculations.validation.confidence_validation import ConfidenceValidationRule
from app.calculations.validation.data_type import DataTypeValidationRule
from app.calculations.validation.duplicate_detection import DuplicateDetectionRule
from app.calculations.validation.financial_consistency import FinancialConsistencyRule
from app.calculations.validation.mandatory_fields import MandatoryFieldsRule
from app.calculations.validation.missing_values import MissingValuesRule
from app.calculations.validation.negative_values import NegativeValueRule
from app.calculations.validation.period_consistency import PeriodConsistencyRule

RULES: list[ValidationRule] = [
    MandatoryFieldsRule(),
    DataTypeValidationRule(),
    MissingValuesRule(),
    DuplicateDetectionRule(),
    FinancialConsistencyRule(),
    NegativeValueRule(),
    PeriodConsistencyRule(),
    ConfidenceValidationRule(),
]
