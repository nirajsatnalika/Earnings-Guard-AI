"""Schemas for the Financial Ratio Engine."""

from pydantic import BaseModel, ConfigDict, Field


class RatioResult(BaseModel):
    """A single computed ratio."""

    model_config = ConfigDict(extra="forbid")

    ratio: str
    category: str
    value: float | None = Field(description="Computed value, or null when inputs are missing/invalid.")
    status: str = Field(description="computed | missing_input | division_by_zero")
    interpretation: str


class RatioResponse(BaseModel):
    """Response returned after computing all ratios for an analysis."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: str
    ratios: list[RatioResult]
    summary: dict[str, int] = Field(
        description="Counts per status: computed, missing_input, division_by_zero."
    )
