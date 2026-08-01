from fastapi import APIRouter

from app.api.v1.endpoints import mapping, parser, uploads

api_router = APIRouter()
api_router.include_router(uploads.router, prefix="/upload", tags=["upload"])
api_router.include_router(parser.router, prefix="/parse", tags=["parse"])
api_router.include_router(mapping.router, prefix="/map", tags=["map"])
