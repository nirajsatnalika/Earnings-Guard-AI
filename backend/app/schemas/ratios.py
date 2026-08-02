"""Schemas for the Financial Ratio Engine."""

from pydantic import BaseModel, ConfigDict, Field


class RatioResult(BaseModel):
    """A single computed ratio."""

    model_config = ConfigDict(extra="forbid")

    ratio: str
    category: str
    value: float | None = Field(description="Computed value, or null when inputs are missing/invalid.")
    status: str = Field(description="computed | missing_input | division_by_zero")
    benchmark: str = Field(description="Benchmark range or threshold used for interpretation.")
    interpretation: str


class RatioCategorySummary(BaseModel):
    """Per-category breakdown of ratio results."""

    model_config = ConfigDict(extra="forbid")

    category: str
    total: int
    computed: int
    missing_input: int
    division_by_zero: int


class RatioResponse(BaseModel):
    """Response returned after computing all ratios for an analysis."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: str
    total_ratios: int
    ratios: list[RatioResult]
    summary: dict[str, int] = Field(
        description="Counts per status: computed, missing_input, division_by_zero."
    )
    categories: list[RatioCategorySummary] = Field(
        description="Per-category breakdown of ratio results."
    )
