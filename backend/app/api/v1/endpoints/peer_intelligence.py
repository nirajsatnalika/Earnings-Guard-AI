"""API Endpoints for Peer & Industry Intelligence (Phase 6C).

Provides REST endpoints for fetching peer groups, external evidence, and confirming peer review choices.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.peer_data.external_evidence_service import (
    ExternalEvidenceService,
    ExternalIntelligencePayload,
    ExternalEvidenceItem,
)
from app.services.peer_data.peer_selection_engine import PeerSelectionResult

router = APIRouter()

# In-memory store for peer evidence per analysis_id
_peer_intelligence_store: Dict[str, ExternalIntelligencePayload] = {}


class ConfirmPeerReviewRequest(BaseModel):
    items: List[ExternalEvidenceItem]
    custom_peers: Optional[List[PeerSelectionResult]] = None


@router.get("/companies/{analysis_id}/peer-group", response_model=ExternalIntelligencePayload)
def get_company_peer_group(
    analysis_id: str,
    company_name: str = Query(default="Target Company"),
    sector: Optional[str] = Query(default=None),
    industry: Optional[str] = Query(default=None),
):
    """Retrieves classified peer group and external metrics for a company analysis."""
    if analysis_id in _peer_intelligence_store:
        return _peer_intelligence_store[analysis_id]

    payload = ExternalEvidenceService.generate_external_intelligence(
        analysis_id=analysis_id,
        company_name=company_name,
        raw_variables={"revenue": 100000.0, "tax_expense": 2400.0, "pat": 7600.0},
        sector_hint=sector,
        industry_hint=industry,
    )
    _peer_intelligence_store[analysis_id] = payload
    return payload


@router.post("/companies/{analysis_id}/peer-group/recalculate", response_model=ExternalIntelligencePayload)
def recalculate_peer_group(
    analysis_id: str,
    company_name: str = Query(default="Target Company"),
    sector: Optional[str] = Query(default=None),
    industry: Optional[str] = Query(default=None),
):
    """Recalculates peer selection and benchmarks."""
    payload = ExternalEvidenceService.generate_external_intelligence(
        analysis_id=analysis_id,
        company_name=company_name,
        raw_variables={"revenue": 100000.0, "tax_expense": 2400.0, "pat": 7600.0},
        sector_hint=sector,
        industry_hint=industry,
    )
    _peer_intelligence_store[analysis_id] = payload
    return payload


@router.get("/companies/{analysis_id}/external-evidence", response_model=List[ExternalEvidenceItem])
def get_external_evidence(analysis_id: str):
    """Retrieves external evidence items for human review."""
    if analysis_id in _peer_intelligence_store:
        return _peer_intelligence_store[analysis_id].evidence_items

    # Generate default if not present
    payload = ExternalEvidenceService.generate_external_intelligence(
        analysis_id=analysis_id,
        company_name="Target Company",
        raw_variables={},
    )
    _peer_intelligence_store[analysis_id] = payload
    return payload.evidence_items


@router.post("/companies/{analysis_id}/external-evidence/confirm")
def confirm_peer_evidence_review(analysis_id: str, req: ConfirmPeerReviewRequest):
    """Confirms human review choices for peer evidence and candidate peer set."""
    if analysis_id not in _peer_intelligence_store:
        payload = ExternalEvidenceService.generate_external_intelligence(
            analysis_id=analysis_id,
            company_name="Target Company",
            raw_variables={},
        )
        _peer_intelligence_store[analysis_id] = payload

    payload = _peer_intelligence_store[analysis_id]
    payload.evidence_items = req.items
    if req.custom_peers:
        payload.selected_peers = req.custom_peers

    return {
        "analysis_id": analysis_id,
        "status": "CONFIRMED",
        "confirmed_items_count": len(req.items),
    }
