"""System and service health endpoints."""

from fastapi import APIRouter

from app.schemas.system import HealthResponse, RootResponse, VersionResponse

router = APIRouter()


@router.get("/", response_model=RootResponse, summary="Service status")
def read_root() -> RootResponse:
    """Return the public service status."""
    return RootResponse(application="EarningsGuard AI", status="running")


@router.get("/health", response_model=HealthResponse, summary="Health check")
def read_health() -> HealthResponse:
    """Return the health status used by service probes."""
    return HealthResponse(status="healthy")


@router.get("/version", response_model=VersionResponse, summary="Application version")
def read_version() -> VersionResponse:
    """Return the deployed application version."""
    return VersionResponse(application="EarningsGuard AI", version="1.0.0")
