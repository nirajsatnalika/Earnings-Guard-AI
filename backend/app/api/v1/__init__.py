from fastapi import APIRouter

from app.api.v1.endpoints import mapping, parser, ratios, uploads, validation

api_router = APIRouter()
api_router.include_router(uploads.router, prefix="/upload", tags=["upload"])
api_router.include_router(parser.router, prefix="/parse", tags=["parse"])
api_router.include_router(mapping.router, prefix="/map", tags=["map"])
api_router.include_router(validation.router, prefix="/validate", tags=["validate"])
api_router.include_router(ratios.router, prefix="/ratios", tags=["ratios"])
