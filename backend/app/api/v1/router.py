"""Version 1 API router."""

from fastapi import APIRouter

from app.api.v1.system import router as system_router
from app.api.v1.uploads import router as upload_router

api_router = APIRouter()
api_router.include_router(system_router, tags=["system"])
api_router.include_router(upload_router, tags=["uploads"])
