"""Parser API endpoint: POST /api/v1/parse/{analysis_id}"""

from fastapi import APIRouter

from app.core.logging import get_logger
from app.services.parser_service import ParserService
from app.schemas.parse import ParseResponse

logger = get_logger(__name__)

router = APIRouter()


@router.post("/{analysis_id}", response_model=ParseResponse, status_code=200)
async def parse_statements(analysis_id: str) -> ParseResponse:
    """Parse all previously-uploaded statements for an analysis into DataFrames."""
    logger.info("Parse request received for analysis %s", analysis_id)
    return ParserService.parse(analysis_id)
