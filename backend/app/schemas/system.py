"""Response schemas for system endpoints."""

from pydantic import BaseModel, ConfigDict


class RootResponse(BaseModel):
    """Public service status response."""

    model_config = ConfigDict(extra="forbid")

    application: str
    status: str


class HealthResponse(BaseModel):
    """Health probe response."""

    model_config = ConfigDict(extra="forbid")

    status: str


class VersionResponse(BaseModel):
    """Application version response."""

    model_config = ConfigDict(extra="forbid")

    application: str
    version: str
