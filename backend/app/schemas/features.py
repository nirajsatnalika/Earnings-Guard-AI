"""Schemas for the Feature Engineering engine."""

from pydantic import BaseModel, ConfigDict, Field


class DerivedMetric(BaseModel):
    """A single derived feature with provenance."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Canonical feature name (e.g. average_assets).")
    category: str = Field(description="Feature category: averages | working_capital | accruals | cash_flow | cycles | growth.")
    value: float | None = Field(description="Computed value, or null when inputs are missing/invalid.")
    status: str = Field(description="computed | missing_input | division_by_zero")
    formula: str = Field(description="Formula used to derive the metric.")
    inputs: dict[str, float | None] = Field(description="Input values used in the calculation.")
    interpretation: str = Field(description="Plain-language explanation of the value.")


class FeatureGroupSummary(BaseModel):
    """Per-category breakdown of derived features."""

    model_config = ConfigDict(extra="forbid")

    category: str
    total: int
    computed: int
    missing_input: int
    division_by_zero: int


class FeatureResponse(BaseModel):
    """Full feature engineering response for an analysis."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: str = Field(description="computed | partial | missing_input")
    total_features: int
    features: list[DerivedMetric]
    dataset: dict[str, float | None] = Field(
        description="Flat key-value map of feature name -> value, ready for downstream models."
    )
    summary: dict[str, int] = Field(
        description="Counts per status: computed, missing_input, division_by_zero."
    )
    groups: list[FeatureGroupSummary] = Field(
        description="Per-category breakdown of derived features."
    )
