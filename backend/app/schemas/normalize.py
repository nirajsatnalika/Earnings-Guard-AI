"""Schemas for the Financial Data Normalizer."""

from pydantic import BaseModel, ConfigDict, Field


class NormalizedCell(BaseModel):
    """A single normalized cell value with provenance metadata."""

    model_config = ConfigDict(extra="forbid")

    raw_value: str = Field(description="The original raw cell value as read from the file.")
    normalized_value: float | None = Field(
        description="Numeric value after normalization, or null if unparseable."
    )
    currency: str | None = Field(description="Detected currency code (e.g. USD, EUR), or null.")
    unit: str | None = Field(description="Detected unit scale (e.g. thousands, millions), or null.")
    scale_factor: float = Field(description="Multiplier applied (e.g. 1000 for thousands).")
    is_negative: bool = Field(description="True if the value was expressed in brackets or with a minus sign.")
    is_parseable: bool = Field(description="True if the raw value could be converted to a number.")
    notes: str = Field(description="Any normalization warnings or transformations applied.")


class NormalizedSheetResult(BaseModel):
    """Normalization results for a single sheet within a statement."""

    model_config = ConfigDict(extra="forbid")

    sheet_name: str
    statement: str
    detected_currency: str | None = Field(description="Currency detected for this sheet, or null.")
    detected_unit: str | None = Field(description="Unit scale detected for this sheet, or null.")
    rows: int
    columns: int
    cells: list[list[NormalizedCell]] = Field(
        description="Grid of normalized cells matching the original DataFrame shape."
    )


class NormalizedStatementResult(BaseModel):
    """Normalization results for a single uploaded statement."""

    model_config = ConfigDict(extra="forbid")

    statement: str
    filename: str
    sheets: list[NormalizedSheetResult]


class NormalizeResponse(BaseModel):
    """Response returned after normalizing all statements for an analysis."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: str
    total_cells: int
    normalized_cells: int
    unparseable_cells: int
    statements: list[NormalizedStatementResult]
