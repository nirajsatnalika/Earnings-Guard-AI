"""Upload service — stores statement files on disk keyed by analysis_id.

This is the existing upload service, recreated faithfully. It is intentionally
left untouched by the parsing work; the parser only reads from the directory
this service writes to.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import EarningsGuardError
from app.core.logging import get_logger
from app.schemas.upload import UploadResponse, UploadedFileResponse

class UploadValidationError(EarningsGuardError):
    """Raised when uploaded file validation fails."""
    pass


logger = get_logger(__name__)

# Field names expected by the multipart upload, mapped to a human statement label.
STATEMENT_FIELDS: dict[str, str] = {
    "balance_sheet": "Balance Sheet",
    "profit_loss": "Profit & Loss Statement",
    "cash_flow": "Cash Flow Statement",
}

ACCEPTED_EXTENSIONS: tuple[str, ...] = (".xlsx", ".xls", ".csv")


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


class UploadService:
    """Stores uploaded statement files under uploads/{analysis_id}/."""

    @staticmethod
    async def store_files(files: dict[str, tuple[str, bytes]]) -> UploadResponse:
        analysis_id = uuid.uuid4().hex
        target_dir = settings.UPLOAD_DIR / analysis_id
        target_dir.mkdir(parents=True, exist_ok=True)

        uploaded: list[UploadedFileResponse] = []
        for field_name, (filename, content) in files.items():
            statement = STATEMENT_FIELDS.get(field_name, field_name)
            ext = Path(filename).suffix.lower()
            if ext not in ACCEPTED_EXTENSIONS:
                raise EarningsGuardError(
                    f"Unsupported file format for '{filename}'. Only .xlsx, .xls, and .csv are accepted.",
                    status_code=422,
                )
            dest = target_dir / f"{field_name}{ext}"
            dest.write_bytes(content)
            uploaded.append(
                UploadedFileResponse(
                    statement=statement,
                    filename=filename,
                    size=_human_size(len(content)),
                    extension=ext,
                )
            )
            logger.info("Stored %s as %s (%s bytes)", filename, dest, len(content))

        logger.info("Analysis %s: stored %d file(s)", analysis_id, len(uploaded))
        return UploadResponse(analysis_id=analysis_id, status="uploaded", uploaded_files=uploaded)
