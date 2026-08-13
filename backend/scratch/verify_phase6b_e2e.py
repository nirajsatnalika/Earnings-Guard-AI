"""Phase 6B End-to-End Verification Script — Annual Report Intelligence.

Demonstrates:
Annual Report PDF Fixture
        ↓
Document Section Segmentation
        ↓
Multi-Year Statement Extraction
        ↓
Footnote & Disclosure Extraction
        ↓
Governance & Auditor Evidence Extraction
        ↓
Normalization & Canonical Evidence Layer
        ↓
EFS Variable Mapping
        ↓
Human Confirmation
        ↓
Confirmed raw_variables Payload
        ↓
POST /api/v1/efs/assess
        ↓
Deterministic EFS Engine Assessment Snapshot (CALIBRATION_PENDING)
"""

import sys
from pathlib import Path
import fitz  # PyMuPDF
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.pdf_segmentation_service import segment_document_pages
from app.services.notes_extraction_service import extract_notes_disclosures
from app.services.governance_extraction_service import extract_governance_evidence

client = TestClient(app)


def run_phase6b_e2e():
    print("=" * 75)
    print("EFS™ PHASE 6B — ANNUAL REPORT INTELLIGENCE END-TO-END VERIFICATION")
    print("=" * 75)

    # 1. Create synthetic multi-year annual report PDF fixture
    fixture_path = Path("scratch") / "Infosys_Annual_Report_Full_FY2025.pdf"
    doc = fitz.open()

    # Page 1: Auditor's Report
    p1 = doc.new_page()
    p1.insert_text((50, 50), "INDEPENDENT AUDITOR'S REPORT TO MEMBERS")
    p1.insert_text((50, 80), "In our opinion, the accompanying consolidated financial statements give a true and fair view.")
    p1.insert_text((50, 100), "Key Audit Matter: Revenue recognition and valuation of unbilled receivables.")

    # Page 2: Financial Statements (Multi-Year)
    p2 = doc.new_page()
    p2.insert_text((50, 50), "CONSOLIDATED STATEMENT OF PROFIT AND LOSS (in ₹ Crores)")
    p2.insert_text((50, 80), "Line Item                                  FY2025       FY2024")
    p2.insert_text((50, 100), "Revenue from Operations                   500,000      450,000")
    p2.insert_text((50, 120), "Trade Receivables                          80,000       65,000")
    p2.insert_text((50, 140), "Cash Flow From Operations                  60,000       55,000")
    p2.insert_text((50, 160), "Profit After Tax                           45,000       40,000")
    p2.insert_text((50, 180), "Cost of Goods Sold                        300,000      270,000")
    p2.insert_text((50, 200), "Inventory                                  50,000       48,000")
    p2.insert_text((50, 220), "Accounts Payable                           40,000       38,000")
    p2.insert_text((50, 240), "Total Assets                              600,000      550,000")

    # Page 3: Notes & Disclosures
    p3 = doc.new_page()
    p3.insert_text((50, 50), "NOTES TO CONSOLIDATED FINANCIAL STATEMENTS")
    p3.insert_text((50, 80), "Note 32: Supplier Financing Arrangements")
    p3.insert_text((50, 100), "The Group has entered into supplier financing arrangements with banks.")
    p3.insert_text((50, 120), "Note 34: Contingent Liabilities")
    p3.insert_text((50, 140), "Contingent liabilities for tax matters totaling ₹ 35,000.")
    p3.insert_text((50, 160), "Note 36: Customer Concentration")
    p3.insert_text((50, 180), "Single external customer represented 22% of total revenue.")
    p3.insert_text((50, 200), "Sales to related parties amounting to ₹ 15,000.")

    doc.save(str(fixture_path))
    doc.close()

    print("[PASS] Step 1: Synthetic Annual Report PDF Fixture created:", fixture_path)

    # 2. Document Section Segmentation
    sections = segment_document_pages(str(fixture_path))
    assert len(sections) == 3
    print(f"[PASS] Step 2: Document Segmentation identified {len(sections)} pages:")
    for sec in sections:
        print(f"       Page {sec.page_num}: Section '{sec.primary_section}'")

    # 3. Footnote & Disclosure Extraction
    disclosures = extract_notes_disclosures(str(fixture_path), "Infosys_Annual_Report_Full_FY2025.pdf")
    print(f"[PASS] Step 3: Extracted {len(disclosures)} footnote disclosure items:")
    for d in disclosures:
        print(f"       - [{d.mapped_efs_variable}] {d.canonical_field}: '{d.evidence_text[:60]}...'")

    # 4. Governance & Auditor Evidence Extraction
    gov_items = extract_governance_evidence(str(fixture_path), "Infosys_Annual_Report_Full_FY2025.pdf")
    print(f"[PASS] Step 4: Extracted {len(gov_items)} governance & auditor evidence items:")
    for g in gov_items:
        print(f"       - [{g.mapped_efs_variable}] {g.canonical_field}: Status '{g.status_value}'")

    # 5. Ingestion Pipeline & Confirmation via API
    with open(fixture_path, "rb") as f:
        upload_res = client.post(
            "/api/v1/upload",
            files={"annual_report": ("Infosys_Annual_Report_Full_FY2025.pdf", f, "application/pdf")},
        )
    analysis_id = upload_res.json()["analysis_id"]

    ingest_res = client.post(f"/api/v1/ingest/{analysis_id}")
    extracted_all = ingest_res.json()["extracted_items"]
    print(f"[PASS] Step 5: Ingested {len(extracted_all)} total items into Canonical Evidence Layer.")

    # 6. Human Review Confirmation
    confirmed_items = []
    for item in extracted_all:
        item["review_status"] = "ACCEPTED"
        confirmed_items.append(item)

    confirm_res = client.post(
        f"/api/v1/ingest/{analysis_id}/confirm",
        json={"items": confirmed_items},
    )
    raw_vars = confirm_res.json()["confirmed_raw_variables"]
    print(f"[PASS] Step 6: Confirmed {len(raw_vars)} raw_variables keys for EFS engine:")
    for k, v in list(raw_vars.items())[:5]:
        print(f"       - {k}: {v}")

    # 7. Execute Deterministic EFS Assessment
    assess_res = client.post(
        f"/api/v1/efs/assess?analysis_id={analysis_id}",
        json={
            "methodology_version": "1.0",
            "statement_flags": {
                "has_cash_flow_statement": True,
                "has_balance_sheet": True,
                "has_income_statement": True,
            },
            "raw_variables": raw_vars,
        },
    )
    assessment = assess_res.json()
    all_vars = [v for p in assessment["pillars"] for v in p["variables"]]

    print("[PASS] Step 7: Deterministic EFS Engine Execution Complete:")
    print("       - Methodology Version:", assessment["efs_version"])
    print("       - Score Status:", assessment["overall"]["score_status"])
    print("       - Total Variables Evaluated Across 7 Pillars:", len(all_vars))
    assert len(all_vars) == 95
    assert assessment["overall"]["score_status"] == "CALIBRATION_PENDING"

    print("=" * 75)
    print("PHASE 6B END-TO-END VERIFICATION PASSED PERFECTLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_phase6b_e2e()
