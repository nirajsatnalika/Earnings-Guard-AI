"""Version 1 API router."""

from fastapi import APIRouter

from app.api.v1.system import router as system_router
from app.api.v1.uploads import router as upload_router
from app.api.v1.endpoints.ratios import router as ratios_router
from app.api.v1.endpoints.beneish import router as beneish_router
from app.api.v1.endpoints.normalize import router as normalize_router
from app.api.v1.endpoints.features import router as features_router
from app.calculations.efs.router import router as efs_router
from app.reports.report import router as report_router
from app.api.v1.endpoints.peer_intelligence import router as peer_intelligence_router

api_router = APIRouter()
api_router.include_router(system_router, tags=["system"])
api_router.include_router(upload_router, tags=["uploads"])
api_router.include_router(ratios_router, prefix="/ratios", tags=["ratios"])
api_router.include_router(beneish_router, prefix="/beneish", tags=["beneish"])
api_router.include_router(normalize_router, prefix="/normalize", tags=["normalize"])
api_router.include_router(features_router, prefix="/features", tags=["features"])
api_router.include_router(efs_router)
api_router.include_router(report_router)
api_router.include_router(peer_intelligence_router, prefix="/peer", tags=["peer_intelligence"])
