"""Feature Engineering API endpoint: POST /api/v1/features/{analysis_id}"""

from fastapi import APIRouter

from app.core.logging import get_logger
from app.schemas.features import FeatureResponse
from app.services.feature_service import FeatureService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/{analysis_id}", response_model=FeatureResponse, status_code=200)
async def engineer_features(analysis_id: str) -> FeatureResponse:
    """Derive all engineered features for a validated analysis."""
    logger.info("Feature engineering request received for analysis %s", analysis_id)
    return FeatureService.engineer(analysis_id)
