"""Ratio API endpoint: POST /api/v1/ratios/{analysis_id}"""

from fastapi import APIRouter

from app.core.logging import get_logger
from app.schemas.ratios import RatioResponse
from app.services.ratio_service import RatioService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/{analysis_id}", response_model=RatioResponse, status_code=200)
async def calculate_ratios(analysis_id: str) -> RatioResponse:
    """Compute all financial ratios for a validated analysis."""
    logger.info("Ratio request received for analysis %s", analysis_id)
    return RatioService.calculate(analysis_id)
