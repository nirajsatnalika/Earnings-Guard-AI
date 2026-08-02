"""Financial Data Normalizer API endpoint: POST /api/v1/normalize/{analysis_id}"""

from fastapi import APIRouter

from app.core.logging import get_logger
from app.schemas.normalize import NormalizeResponse
from app.services.normalizer_service import NormalizerService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/{analysis_id}", response_model=NormalizeResponse, status_code=200)
async def normalize_analysis(analysis_id: str) -> NormalizeResponse:
    """Normalize all parsed financial statements for an analysis."""
    logger.info("Normalize request received for analysis %s", analysis_id)
    return NormalizerService.normalize(analysis_id)
