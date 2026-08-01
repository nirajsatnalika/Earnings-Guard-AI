"""Schemas for the Financial Statement Mapping workflow."""

from pydantic import BaseModel, ConfigDict, Field


class MappedField(BaseModel):
    """A single raw label mapped to a canonical field with a confidence score."""

    model_config = ConfigDict(extra="forbid")

    original: str
    mapped: str
    confidence: int = Field(ge=0, le=100)


class MapResponse(BaseModel):
    """Response returned after mapping all parsed statement labels."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: str
    mapped_fields: list[MappedField]
    unmapped_fields: list[str]
