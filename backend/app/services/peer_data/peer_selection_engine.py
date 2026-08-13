"""Peer Selection Engine for EFS™ Phase 6C.

Deterministically ranks candidate peers using configurable scoring criteria:
Industry Match + Geography Match + Size Similarity + Data Availability.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.services.peer_data.company_classifier import CompanyClassification


class CandidatePeer(BaseModel):
    company_name: str
    ticker: str
    country: str
    sector: str
    industry: str
    revenue_crores: float
    effective_tax_rate: float
    auditor_name: str
    auditor_tenure_years: int
    promoter_pledge_pct: float
    regulatory_flag_count: int
    data_available: bool = True


class PeerSelectionResult(BaseModel):
    candidate: CandidatePeer
    peer_score: float
    industry_match_score: float
    geography_match_score: float
    size_similarity_score: float
    data_availability_score: float
    selected: bool
    reason: str


# Free public baseline peer database (Synthetic / Public Filing Fixtures)
PUBLIC_PEER_UNIVERSE: List[CandidatePeer] = [
    CandidatePeer(
        company_name="TCS (Tata Consultancy Services)",
        ticker="TCS.NS",
        country="India",
        sector="TECHNOLOGY",
        industry="IT Services & Software",
        revenue_crores=240000.0,
        effective_tax_rate=25.2,
        auditor_name="BSR & Co LLP",
        auditor_tenure_years=6,
        promoter_pledge_pct=0.0,
        regulatory_flag_count=0,
    ),
    CandidatePeer(
        company_name="Wipro Limited",
        ticker="WIPRO.NS",
        country="India",
        sector="TECHNOLOGY",
        industry="IT Services & Software",
        revenue_crores=90000.0,
        effective_tax_rate=22.8,
        auditor_name="Deloitte Haskins & Sells",
        auditor_tenure_years=4,
        promoter_pledge_pct=0.0,
        regulatory_flag_count=0,
    ),
    CandidatePeer(
        company_name="HCL Technologies",
        ticker="HCLTECH.NS",
        country="India",
        sector="TECHNOLOGY",
        industry="IT Services & Software",
        revenue_crores=110000.0,
        effective_tax_rate=23.5,
        auditor_name="S.R. Batliboi & Associates",
        auditor_tenure_years=5,
        promoter_pledge_pct=0.0,
        regulatory_flag_count=0,
    ),
    CandidatePeer(
        company_name="Tech Mahindra",
        ticker="TECHM.NS",
        country="India",
        sector="TECHNOLOGY",
        industry="IT Services & Software",
        revenue_crores=53000.0,
        effective_tax_rate=24.0,
        auditor_name="BSR & Co LLP",
        auditor_tenure_years=3,
        promoter_pledge_pct=0.0,
        regulatory_flag_count=0,
    ),
    CandidatePeer(
        company_name="LTIMindtree",
        ticker="LTIM.NS",
        country="India",
        sector="TECHNOLOGY",
        industry="IT Services & Software",
        revenue_crores=35000.0,
        effective_tax_rate=24.5,
        auditor_name="Price Waterhouse Chartered Accountants",
        auditor_tenure_years=2,
        promoter_pledge_pct=0.0,
        regulatory_flag_count=0,
    ),
    CandidatePeer(
        company_name="Dr. Reddy's Laboratories",
        ticker="DRREDDY.NS",
        country="India",
        sector="HEALTHCARE",
        industry="Pharmaceuticals & Biotech",
        revenue_crores=28000.0,
        effective_tax_rate=21.0,
        auditor_name="S.R. Batliboi & Associates",
        auditor_tenure_years=7,
        promoter_pledge_pct=0.0,
        regulatory_flag_count=0,
    ),
]


class PeerSelectionEngine:
    """Selects and scores peers for a target company."""

    def __init__(self, min_peer_score: float = 60.0, max_peers: int = 5):
        self.min_peer_score = min_peer_score
        self.max_peers = max_peers

    def select_peers(
        self,
        target_classification: CompanyClassification,
        target_revenue_crores: Optional[float] = None,
        custom_candidates: Optional[List[CandidatePeer]] = None,
    ) -> List[PeerSelectionResult]:
        candidates = custom_candidates or PUBLIC_PEER_UNIVERSE
        results: List[PeerSelectionResult] = []

        for candidate in candidates:
            # Skip self
            if candidate.company_name.lower() == target_classification.company_name.lower():
                continue

            # 1. Industry Match Score (Max 40)
            if candidate.industry == target_classification.industry:
                ind_score = 40.0
            elif candidate.sector == target_classification.sector:
                ind_score = 20.0
            else:
                ind_score = 0.0

            # 2. Geography Match Score (Max 20)
            geo_score = 20.0 if candidate.country.lower() == target_classification.country.lower() else 10.0

            # 3. Size Similarity Score (Max 20)
            size_score = 20.0
            if target_revenue_crores and target_revenue_crores > 0:
                ratio = candidate.revenue_crores / target_revenue_crores
                if 0.5 <= ratio <= 2.0:
                    size_score = 20.0
                elif 0.2 <= ratio <= 5.0:
                    size_score = 10.0
                else:
                    size_score = 5.0

            # 4. Data Availability Score (Max 20)
            data_score = 20.0 if candidate.data_available else 0.0

            total_score = ind_score + geo_score + size_score + data_score

            selected = total_score >= self.min_peer_score and ind_score > 0
            reason = "SELECTED" if selected else ("REJECTED_INDUSTRY_MISMATCH" if ind_score == 0 else "REJECTED_LOW_SCORE")

            results.append(
                PeerSelectionResult(
                    candidate=candidate,
                    peer_score=total_score,
                    industry_match_score=ind_score,
                    geography_match_score=geo_score,
                    size_similarity_score=size_score,
                    data_availability_score=data_score,
                    selected=selected,
                    reason=reason,
                )
            )

        # Sort selected by total peer score descending
        results.sort(key=lambda x: x.peer_score, reverse=True)
        return results[: self.max_peers]
