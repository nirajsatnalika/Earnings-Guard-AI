"""Mapping API endpoint: POST /api/v1/map/{analysis_id}"""

from fastapi import APIRouter

from app.core.logging import get_logger
from app.schemas.mapping import MapResponse
from app.services.mapping_service import MappingService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/{analysis_id}", response_model=MapResponse, status_code=200)
async def map_statements(analysis_id: str) -> MapResponse:
    """Map parsed financial statement labels to the canonical dictionary."""
    logger.info("Map request received for analysis %s", analysis_id)
    return MappingService.map(analysis_id)
