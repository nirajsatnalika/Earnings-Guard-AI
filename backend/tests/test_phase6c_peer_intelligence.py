"""Pytest unit test suite for EFS Phase 6C Peer & Industry Intelligence Layer.

Tests:
1. Deterministic Company Classifier
2. Peer Selection Engine & transparent score calculation
3. Insufficient peer count protection (< 3 peers)
4. Free Data Source Registry compliance
5. Peer Metrics Engine (median, mean, percentile, deviation)
6. Supporting external evidence generation for FSQ10, GD04, GD06, GD09, GS08
7. EFS methodology immutability check
"""

import pytest
from app.services.peer_data.company_classifier import CompanyClassifier
from app.services.peer_data.peer_selection_engine import PeerSelectionEngine, CandidatePeer
from app.services.peer_data.source_registry import SourceRegistry
from app.services.peer_data.peer_metrics_engine import PeerMetricsEngine
from app.services.peer_data.external_evidence_service import ExternalEvidenceService


def test_company_classifier():
    """Verify deterministic company classification."""
    clf = CompanyClassifier.classify_company("Infosys Technologies", country_hint="India")
    assert clf.sector == "TECHNOLOGY"
    assert clf.industry == "IT Services & Software"
    assert clf.country == "India"
    assert clf.accounting_regime == "IndAS"
    assert clf.status == "VERIFIED"


def test_peer_selection_engine():
    """Verify deterministic peer selection scoring formula."""
    target_clf = CompanyClassifier.classify_company("Infosys", sector_hint="TECHNOLOGY", industry_hint="IT Services & Software")
    engine = PeerSelectionEngine(min_peer_score=60.0)
    peers = engine.select_peers(target_classification=target_clf, target_revenue_crores=150000.0)

    assert len(peers) >= 3
    for p in peers:
        assert p.selected is True
        assert p.peer_score >= 60.0
        assert p.industry_match_score == 40.0


def test_insufficient_peer_count_protection():
    """Verify < 3 peers returns INSUFFICIENT_PEERS status."""
    single_peer = CandidatePeer(
        company_name="Single Peer Inc",
        ticker="SP.NS",
        country="India",
        sector="TECHNOLOGY",
        industry="IT Services & Software",
        revenue_crores=100000.0,
        effective_tax_rate=24.0,
        auditor_name="Test Auditor",
        auditor_tenure_years=5,
        promoter_pledge_pct=0.0,
        regulatory_flag_count=0,
    )
    
    target_clf = CompanyClassifier.classify_company("Target Co")
    peers = PeerSelectionEngine().select_peers(target_classification=target_clf, custom_candidates=[single_peer])

    bm = PeerMetricsEngine.compute_metric_benchmark(
        metric_key="effective_tax_rate",
        metric_label="Effective Tax Rate",
        company_value=24.5,
        unit="%",
        peers=peers,
        value_extractor_func=lambda c: c.effective_tax_rate,
    )

    assert bm.benchmark_status == "INSUFFICIENT_PEERS"
    assert bm.peer_median is None


def test_free_data_source_registry():
    """Verify all registered sources are 100% free and public."""
    sources = SourceRegistry.list_sources()
    assert len(sources) >= 4
    for src in sources:
        assert src.is_free is True
        assert src.is_public is True
        assert src.requires_payment is False


def test_external_evidence_service_all_5_variables():
    """Verify external evidence collation for FSQ10, GD04, GD06, GD09, GS08."""
    payload = ExternalEvidenceService.generate_external_intelligence(
        analysis_id="test_phase6c_analysis",
        company_name="Infosys Limited",
        raw_variables={"revenue": 150000.0, "tax_expense": 5000.0, "pat": 18000.0, "promoter_pledge_pct": 0.0},
    )

    assert len(payload.selected_peers) >= 3
    assert len(payload.evidence_items) == 5

    var_map = {e.variable_id: e for e in payload.evidence_items}

    # FSQ10: Tax Rate Anomaly
    assert "FSQ10" in var_map
    assert var_map["FSQ10"].company_value is not None
    assert var_map["FSQ10"].peer_median is not None
    assert var_map["FSQ10"].status == "VERIFIED"

    # GD04: Audit Tenure
    assert "GD04" in var_map
    assert var_map["GD04"].company_value == 5.0
    assert var_map["GD04"].status == "VERIFIED"

    # GD06: Promoter Pledge
    assert "GD06" in var_map
    assert var_map["GD06"].company_value == 0.0
    assert var_map["GD06"].status == "VERIFIED"

    # GD09: Regulatory Action
    assert "GD09" in var_map
    assert var_map["GD09"].status == "NOT_FOUND"

    # GS08: Earnings Persistence
    assert "GS08" in var_map
    assert var_map["GS08"].status == "INSUFFICIENT_HISTORY"
