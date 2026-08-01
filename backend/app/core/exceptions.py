"""Application-specific exceptions and a shared FastAPI exception handler."""

from fastapi import Request
from fastapi.responses import JSONResponse


class EarningsGuardError(Exception):
    """Base error for all application-specific failures."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AnalysisNotFoundError(EarningsGuardError):
    def __init__(self, analysis_id: str) -> None:
        super().__init__(
            f"Analysis '{analysis_id}' not found. Upload statements before parsing.",
            status_code=404,
        )


class NoFilesFoundError(EarningsGuardError):
    def __init__(self, analysis_id: str) -> None:
        super().__init__(
            f"No statement files found for analysis '{analysis_id}'.",
            status_code=404,
        )


class UnsupportedFileFormatError(EarningsGuardError):
    def __init__(self, filename: str) -> None:
        super().__init__(
            f"Unsupported file format for '{filename}'. Only .xlsx, .xls, and .csv are accepted.",
            status_code=422,
        )


class FileParsingError(EarningsGuardError):
    def __init__(self, filename: str, detail: str) -> None:
        super().__init__(
            f"Failed to parse '{filename}': {detail}",
            status_code=422,
        )


async def earnings_guard_exception_handler(request: Request, exc: EarningsGuardError) -> JSONResponse:
    """Shared handler that normalizes all app errors to a consistent shape."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
