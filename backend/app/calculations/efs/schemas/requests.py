"""API Request schemas for the EFS™ Engine module."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class EFSRequest(BaseModel):
    """Request payload schema for EFS calculation endpoint."""

    model_config = ConfigDict(extra="forbid")

    methodology_version: str = Field(default="1.0", description="Target methodology version (default: 1.0).")
    validation_output: Optional[Dict[str, Any]] = Field(
        default=None, description="Output object from Validation Engine."
    )
    feature_output: Optional[Dict[str, Any]] = Field(
        default=None, description="Output object from Feature Engineering."
    )
    ratio_output: Optional[Dict[str, Any]] = Field(
        default=None, description="Output object from Ratio Engine."
    )
    beneish_output: Optional[Dict[str, Any]] = Field(
        default=None, description="Output object from Beneish Engine."
    )
    statement_flags: Optional[Dict[str, bool]] = Field(
        default=None, description="Availability flags for Cash Flow, Balance Sheet, Income Statement."
    )
