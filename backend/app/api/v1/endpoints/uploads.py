"""Upload API endpoint — existing endpoint, recreated faithfully."""

from fastapi import APIRouter, UploadFile

from app.core.logging import get_logger
from app.services.upload_service import UploadService
from app.schemas.upload import UploadResponse

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=UploadResponse, status_code=200)
async def upload_statements(
    balance_sheet: UploadFile | None = None,
    profit_loss: UploadFile | None = None,
    cash_flow: UploadFile | None = None,
) -> UploadResponse:
    """Accept up to three financial-statement uploads and store them on disk."""
    received: dict[str, tuple[str, bytes]] = {}
    for field_name, upload in (
        ("balance_sheet", balance_sheet),
        ("profit_loss", profit_loss),
        ("cash_flow", cash_flow),
    ):
        if upload is None or not upload.filename:
            continue
        content = await upload.read()
        if not content:
            continue
        received[field_name] = (upload.filename, content)

    logger.info("Upload request received with %d file(s)", len(received))
    return await UploadService.store_files(received)
