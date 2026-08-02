"""Beneish M-Score API endpoint: POST /api/v1/beneish/{analysis_id}"""

from fastapi import APIRouter

from app.core.logging import get_logger
from app.schemas.beneish import BeneishResponse
from app.services.beneish_service import BeneishService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/{analysis_id}", response_model=BeneishResponse, status_code=200)
async def calculate_beneish(analysis_id: str) -> BeneishResponse:
    """Compute the Beneish M-Score for a validated analysis."""
    logger.info("Beneish request received for analysis %s", analysis_id)
    return BeneishService.calculate(analysis_id)
