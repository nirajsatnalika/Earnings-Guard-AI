"""Production Exception Hierarchy for the EFS™ Assessment Framework.

Provides specialized domain exceptions for methodology loading, validation,
eligibility, pillar calculations, and configuration errors.
"""

from typing import Any, Dict, Optional


class EFSEngineError(Exception):
    """Base exception for all EFS Engine errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, details={self.details!r})"


class EFSConfigurationError(EFSEngineError):
    """Raised when there is an error loading or parsing methodology configuration JSON files."""

    pass


class EFSDataValidationError(EFSEngineError):
    """Raised when input payload fails structural or prerequisite data validation."""

    pass


class EFSEligibilityError(EFSEngineError):
    """Raised when financial statement prerequisites fail eligibility checks."""

    pass


class EFSPillarNotFoundError(EFSEngineError):
    """Raised when a requested pillar engine is not registered."""

    pass


class EFSCalculationError(EFSEngineError):
    """Raised when an unrecoverable error occurs during pillar or score calculation."""

    pass
