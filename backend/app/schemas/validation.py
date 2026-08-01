"""Schemas for the Financial Statement Validation workflow."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ValidationIssue(BaseModel):
    """A single issue surfaced by a validation rule."""

    model_config = ConfigDict(extra="forbid")

    validation_id: str
    category: str
    severity: Severity
    field: str
    message: str
    recommendation: str


class ValidationSummary(BaseModel):
    """Counts of checks by outcome."""

    model_config = ConfigDict(extra="forbid")

    passed: int = Field(ge=0)
    warnings: int = Field(ge=0)
    errors: int = Field(ge=0)
    critical: int = Field(ge=0)


class ValidationResponse(BaseModel):
    """Response returned after validating mapped statements."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: str
    summary: ValidationSummary
    issues: list[ValidationIssue]
    validation_score: int = Field(ge=0, le=100)
