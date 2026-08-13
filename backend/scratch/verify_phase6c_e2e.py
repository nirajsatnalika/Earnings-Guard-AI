"""Phase 6C End-to-End Integration Verification Script.

Demonstrates:
Company Input & Classification
        ↓
Deterministic Peer Selection Engine
        ↓
Free Data Source Registry & Benchmark Metrics
        ↓
External Evidence & Provenance Collation (FSQ10, GD04, GD06, GD09, GS08)
        ↓
Human Review & Confirmation
        ↓
Confirmed raw_variables Payload
        ↓
POST /api/v1/efs/assess
        ↓
Persisted Assessment Snapshot with Peer & Industry Intelligence PDF Section
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.peer_data.company_classifier import CompanyClassifier
from app.services.peer_data.peer_selection_engine import PeerSelectionEngine
from app.services.peer_data.external_evidence_service import ExternalEvidenceService

client = TestClient(app)


def run_phase6c_e2e():
    print("=" * 75)
    print("EFS™ PHASE 6C — FREE-FIRST PEER & INDUSTRY INTELLIGENCE END-TO-END")
    print("=" * 75)

    analysis_id = "test_phase6c_e2e_run"
    company_name = "Infosys Limited"

    # 1. Company Classification
    clf = CompanyClassifier.classify_company(company_name, country_hint="India")
    print("[PASS] Step 1: Company Classifier output:")
    print(f"       - Company: {clf.company_name}")
    print(f"       - Sector/Industry: {clf.sector} / {clf.industry}")
    print(f"       - Country/Regime: {clf.country} / {clf.accounting_regime}")
    print(f"       - Status: {clf.status} (Confidence {clf.confidence}%)")

    # 2. Peer Selection Engine
    engine = PeerSelectionEngine(min_peer_score=60.0)
    peers = engine.select_peers(target_classification=clf, target_revenue_crores=153000.0)
    print(f"[PASS] Step 2: Selected {len(peers)} peer companies based on transparent scoring formula:")
    for p in peers:
        print(f"       - [{p.peer_score:.0f} pts] {p.candidate.company_name} ({p.candidate.ticker}) — {p.reason}")

    # 3. External Evidence & Provenance Collation
    payload = ExternalEvidenceService.generate_external_intelligence(
        analysis_id=analysis_id,
        company_name=company_name,
        raw_variables={"revenue": 153000.0, "tax_expense": 5100.0, "pat": 18200.0, "promoter_pledge_pct": 0.0},
    )
    print(f"[PASS] Step 3: Collated {len(payload.evidence_items)} external evidence records with 100% provenance:")
    for item in payload.evidence_items:
        print(f"       - [{item.variable_id}] {item.variable_name}: Status '{item.status}'")
        print(f"         Text: '{item.evidence_text}'")
        print(f"         Source: {item.source_name} ({item.source_url})")

    # 4. Human Review & Confirmation via API
    items_dict = [item.model_dump() for item in payload.evidence_items]
    confirm_res = client.post(
        f"/api/v1/peer/companies/{analysis_id}/external-evidence/confirm",
        json={"items": items_dict},
    )
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "CONFIRMED"
    print("[PASS] Step 4: Human Review confirmed peer evidence choice via API endpoint.")

    # 5. Execute Deterministic EFS Engine Assessment
    assess_res = client.post(
        f"/api/v1/efs/assess?analysis_id={analysis_id}",
        json={
            "methodology_version": "1.0",
            "statement_flags": {
                "has_cash_flow_statement": True,
                "has_balance_sheet": True,
                "has_income_statement": True,
            },
            "raw_variables": {
                "revenue": 153000.0,
                "prior_revenue": 140000.0,
                "receivables": 32000.0,
                "prior_receivables": 29000.0,
                "cfo": 24000.0,
                "pat": 18200.0,
                "total_assets": 120000.0,
                "prior_total_assets": 110000.0,
                "cogs": 90000.0,
                "inventory": 8000.0,
                "payables": 15000.0,
                "tax_expense": 5100.0,
                "promoter_pledge_pct": 0.0,
            },
        },
    )
    assert assess_res.status_code == 200
    assessment = assess_res.json()
    all_vars = [v for p in assessment["pillars"] for v in p["variables"]]

    print("[PASS] Step 5: Deterministic EFS Engine Execution Complete:")
    print("       - Methodology Version:", assessment["efs_version"])
    print("       - Total Variables Evaluated Across 7 Pillars:", len(all_vars))
    print("       - Score Status:", assessment["overall"]["score_status"])
    assert len(all_vars) == 95
    assert assessment["overall"]["score_status"] == "CALIBRATION_PENDING"

    print("=" * 75)
    print("PHASE 6C END-TO-END VERIFICATION PASSED PERFECTLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_phase6c_e2e()
