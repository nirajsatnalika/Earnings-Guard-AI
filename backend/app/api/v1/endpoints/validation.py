"""Validation API endpoint: POST /api/v1/validate/{analysis_id}"""

from fastapi import APIRouter, Query

from app.core.logging import get_logger
from app.schemas.validation import ValidationResponse
from app.services.validation_service import DEFAULT_CONFIDENCE_THRESHOLD, ValidationService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/{analysis_id}", response_model=ValidationResponse, status_code=200)
async def validate_statements(
    analysis_id: str,
    confidence_threshold: int = Query(
        DEFAULT_CONFIDENCE_THRESHOLD, ge=0, le=100, description="Minimum mapping confidence to accept."
    ),
) -> ValidationResponse:
    """Validate mapped financial statements before ratio calculations."""
    logger.info("Validate request received for analysis %s (threshold %d%%)", analysis_id, confidence_threshold)
    return ValidationService.validate(analysis_id, confidence_threshold=confidence_threshold)
