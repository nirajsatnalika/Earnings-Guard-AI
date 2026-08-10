"""FastAPI application entrypoint for EarningsGuard AI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import (
    EarningsGuardError,
    earnings_guard_exception_handler,
)
from app.core.logging import configure_logging, get_logger

from app.database.database import init_db

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_upload_dir()
    init_db()
    logger.info("%s backend starting up", settings.PROJECT_NAME)
    yield
    logger.info("%s backend shutting down", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI-powered Financial Forensics platform for detecting earnings manipulation.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(EarningsGuardError, earnings_guard_exception_handler)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.PROJECT_NAME}
