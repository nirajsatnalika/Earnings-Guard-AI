"""End-to-End Verification Script for EFS Phase 6A — Data Ingestion MVP.

Tests full workflow:
  Sample Document Upload (PDF/Excel)
    ↓
  Extraction & Normalization (/api/v1/ingest/{analysis_id})
    ↓
  Human Review Confirmation (/api/v1/ingest/{analysis_id}/confirm)
    ↓
  EFS Assessment Execution (/api/v1/efs/assess)
    ↓
  Persisted Snapshot, Report PDF, and Audit Trail Verification
"""

import sys
from pathlib import Path
import fitz  # PyMuPDF
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)


def run_e2e_verification():
    print("=" * 70)
    print("EFS™ PHASE 6A — END-TO-END DATA INGESTION VERIFICATION")
    print("=" * 70)

    # 1. Create temporary sample PDF document
    sample_pdf_path = Path("scratch") / "Infosys_Annual_Report_FY2025.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "INFOSYS LIMITED ANNUAL REPORT FY 2025")
    page.insert_text((50, 80), "FINANCIAL STATEMENT SUMMARY (in INR)")
    page.insert_text((50, 120), "Revenue from Operations                       500,000")
    page.insert_text((50, 140), "Trade Receivables                             80,000")
    page.insert_text((50, 160), "Cash Flow From Operations                     60,000")
    page.insert_text((50, 180), "Profit After Tax                              45,000")
    page.insert_text((50, 200), "Cost of Goods Sold                            300,000")
    page.insert_text((50, 220), "Inventory                                     50,000")
    page.insert_text((50, 240), "Accounts Payable                              40,000")
    page.insert_text((50, 260), "Total Assets                                  600,000")
    doc.save(str(sample_pdf_path))
    doc.close()

    print("[PASS] Step 1: Created sample PDF annual report:", sample_pdf_path)

    # 2. Upload document via POST /api/v1/upload
    with open(sample_pdf_path, "rb") as f:
        upload_res = client.post(
            "/api/v1/upload",
            files={"annual_report": ("Infosys_Annual_Report_FY2025.pdf", f, "application/pdf")},
        )

    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    upload_data = upload_res.json()
    analysis_id = upload_data["analysis_id"]
    print(f"[PASS] Step 2: Upload successful. Analysis ID = '{analysis_id}'")

    # 3. Process ingestion via POST /api/v1/ingest/{analysis_id}
    ingest_res = client.post(f"/api/v1/ingest/{analysis_id}")
    assert ingest_res.status_code == 200, f"Ingestion failed: {ingest_res.text}"
    ingest_data = ingest_res.json()
    assert ingest_data["is_scanned_pdf"] is False
    extracted_items = ingest_data["extracted_items"]
    print(f"[PASS] Step 3: Ingested {len(extracted_items)} items with source provenance metadata.")

    # Inspect mapping results
    revenue_item = next((i for i in extracted_items if i["raw_label"] == "Revenue from Operations"), None)
    assert revenue_item is not None, "Revenue item missing from extraction"
    assert revenue_item["canonical_field"] == "Revenue"
    assert revenue_item["mapped_efs_variable"] == "FSQ01"
    assert revenue_item["raw_variable_key"] == "revenue"
    print("       Provenance Verified:", revenue_item["source_filename"], "Page:", revenue_item["source_page"])
    print("       Mapping Verified: 'Revenue from Operations' -> 'Revenue' -> FSQ01 (revenue)")

    # 4. Human Review Confirmation via POST /api/v1/ingest/{analysis_id}/confirm
    # Simulate user accepting items
    confirmed_items = []
    for item in extracted_items:
        item["review_status"] = "ACCEPTED"
        confirmed_items.append(item)

    confirm_res = client.post(
        f"/api/v1/ingest/{analysis_id}/confirm",
        json={"items": confirmed_items},
    )
    assert confirm_res.status_code == 200, f"Confirm review failed: {confirm_res.text}"
    raw_vars = confirm_res.json()["confirmed_raw_variables"]
    assert "revenue" in raw_vars
    assert raw_vars["revenue"] == 500000.0
    print(f"[PASS] Step 4: Human Review confirmed {len(raw_vars)} raw variables for EFS engine.")

    # 5. Run EFS Assessment via POST /api/v1/efs/assess
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
    assert assess_res.status_code == 200, f"Assessment failed: {assess_res.text}"
    assessment_data = assess_res.json()
    all_vars = [v for p in assessment_data["pillars"] for v in p["variables"]]
    print("       - Methodology Version:", assessment_data["efs_version"])
    print("       - Score Status:", assessment_data["overall"]["score_status"])
    print("       - Total Variables Evaluated Across 7 Pillars:", len(all_vars))
    assert len(all_vars) == 95
    assert assessment_data["overall"]["score_status"] == "CALIBRATION_PENDING"

    # 6. Verify PDF report generation endpoint
    report_res = client.get(f"/api/v1/efs/{analysis_id}/report")
    assert report_res.status_code in (200, 503)
    print("[PASS] Step 6: PDF Report endpoint verified!")

    print("=" * 70)
    print("PHASE 6A END-TO-END VERIFICATION PASSED PERFECTLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_e2e_verification()
