"""Schemas for the upload workflow."""

from pydantic import BaseModel, ConfigDict


class UploadedFileResponse(BaseModel):
    """Metadata returned for one accepted statement file."""

    model_config = ConfigDict(extra="forbid")

    statement: str
    filename: str
    size: str
    extension: str


class UploadResponse(BaseModel):
    """Response returned after all statement files are stored."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: str
    uploaded_files: list[UploadedFileResponse]
