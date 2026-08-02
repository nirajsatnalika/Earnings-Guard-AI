"""Schemas for the Beneish M-Score engine."""

from pydantic import BaseModel, ConfigDict, Field


class BeneishComponentResult(BaseModel):
    """A single component of the Beneish M-Score (one of the 8 variables)."""

    model_config = ConfigDict(extra="forbid")

    component: str = Field(description="Name of the component (e.g. DSRI, GMI).")
    value: float | None = Field(description="Computed component value, or null when inputs are missing.")
    status: str = Field(description="computed | missing_input | division_by_zero")
    formula: str = Field(description="The official formula used.")
    inputs: dict[str, float | None] = Field(description="Input values used in the calculation.")
    interpretation: str = Field(description="Plain-language explanation of the component value.")


class BeneishResponse(BaseModel):
    """Full Beneish M-Score response for an analysis."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: str = Field(description="computed | missing_input | division_by_zero")
    m_score: float | None = Field(description="The Beneish M-Score, or null if any component is missing.")
    threshold: float = Field(description="The manipulator threshold (-1.78).")
    is_manipulator: bool | None = Field(
        description="True if M-Score > -1.78 (likely manipulator). Null if score is missing."
    )
    components: list[BeneishComponentResult]
    summary: dict[str, int] = Field(
        description="Counts per status: computed, missing_input, division_by_zero."
    )
    interpretation: str = Field(description="Overall plain-language assessment.")
