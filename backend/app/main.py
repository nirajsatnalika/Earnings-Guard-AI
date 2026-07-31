"""FastAPI application entrypoint for EarningsGuard AI."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.database.database import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
	"""Initialize and clean up application resources."""
	_ = _app
	logger.info("Starting %s", settings.app_name)
	init_db()
	yield
	logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
	title=settings.app_name,
	version=settings.app_version,
	description="Enterprise financial forensics infrastructure for EarningsGuard AI.",
	docs_url="/docs",
	redoc_url="/redoc",
	openapi_url="/openapi.json",
	lifespan=lifespan,
)

configure_logging()
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origin_list,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(api_router)
