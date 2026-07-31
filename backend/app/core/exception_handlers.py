"""Global exception handlers for the HTTP application."""

import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def http_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Return a consistent response for expected HTTP exceptions."""
    _ = _request
    if not isinstance(exc, StarletteHTTPException):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def validation_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Return a consistent response for request validation failures."""
    _ = _request
    if not isinstance(exc, RequestValidationError):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return JSONResponse(status_code=422, content={"detail": "Request validation failed", "errors": exc.errors()})


async def unhandled_exception_handler(request: Request, _exc: Exception) -> JSONResponse:
    """Log unexpected failures without exposing internal implementation details."""
    logger.error(
        "Unhandled exception while processing %s %s",
        request.method,
        request.url.path,
        exc_info=(_exc.__class__, _exc, _exc.__traceback__),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
