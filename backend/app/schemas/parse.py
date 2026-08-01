"""Schemas for the Excel/CSV parsing workflow."""

from pydantic import BaseModel, ConfigDict, Field


class ParsedSheet(BaseModel):
    """Summary of a single sheet parsed from a workbook or CSV."""

    model_config = ConfigDict(extra="forbid")

    name: str
    rows: int = Field(ge=0)
    columns: int = Field(ge=0)


class ParsedStatement(BaseModel):
    """Summary of all sheets parsed from one uploaded statement."""

    model_config = ConfigDict(extra="forbid")

    statement: str
    filename: str
    sheets: list[ParsedSheet]


class ParseResponse(BaseModel):
    """Response returned after parsing all uploaded statements."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: str
    statements: list[ParsedStatement]
