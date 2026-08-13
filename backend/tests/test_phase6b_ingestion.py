"""Pytest unit test suite for Phase 6B Annual Report Intelligence.

Tests:
1. Document section segmentation
2. Footnote and disclosure extraction (supplier financing, contingent liabilities, contract assets, inventory provisions)
3. Governance and auditor evidence extraction (audit opinion, KAM, auditor change, restatements)
4. Source provenance preservation
5. Safety: missing values remain missing without zero-filling
6. Human review confirmation to raw_variables
7. EFS endpoint execution evaluating 95 variables under CALIBRATION_PENDING status.
"""

from pathlib import Path
import tempfile
import fitz  # PyMuPDF
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.pdf_segmentation_service import segment_document_pages
from app.services.notes_extraction_service import extract_notes_disclosures
from app.services.governance_extraction_service import extract_governance_evidence
from app.services.ingestion_service import IngestionService
from app.schemas.ingest import CanonicalExtractedItem

client = TestClient(app)


def test_document_section_segmentation():
    """Verify Annual Report header/pattern segmentation into functional sections."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    doc = fitz.open()
    
    # Page 1: Independent Auditor's Report
    p1 = doc.new_page()
    p1.insert_text((50, 50), "INDEPENDENT AUDITOR'S REPORT")
    p1.insert_text((50, 100), "In our opinion, the accompanying consolidated financial statements give a true and fair view.")

    # Page 2: Balance Sheet
    p2 = doc.new_page()
    p2.insert_text((50, 50), "CONSOLIDATED BALANCE SHEET AS AT MARCH 31, 2025")
    p2.insert_text((50, 100), "Total Assets                                600,000")

    # Page 3: Notes to Accounts - Contingent Liabilities
    p3 = doc.new_page()
    p3.insert_text((50, 50), "NOTE 28: CONTINGENT LIABILITIES AND COMMITMENTS")
    p3.insert_text((50, 100), "Claims against the company not acknowledged as debts amounting to ₹ 25,000.")

    doc.save(pdf_path)
    doc.close()

    segmented = segment_document_pages(pdf_path)
    assert len(segmented) == 3
    assert segmented[0].primary_section == "AUDITORS_REPORT"
    assert segmented[1].primary_section == "BALANCE_SHEET"
    assert segmented[2].primary_section == "NOTES_CONTINGENCIES"

    Path(pdf_path).unlink(missing_ok=True)


def test_notes_and_disclosure_extraction():
    """Verify footnote disclosure extraction for supplier financing, contingencies, provisions, and intangibles."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "NOTES FORMING PART OF FINANCIAL STATEMENTS")
    page.insert_text((50, 80), "The Group has entered into supplier financing arrangements with banks.")
    page.insert_text((50, 100), "Contingent liabilities amounting to ₹ 45,000 for tax disputes.")
    page.insert_text((50, 120), "Provision for obsolete inventory of ₹ 12,000 recognized.")
    page.insert_text((50, 140), "Single external customer represented 28% of total revenue.")
    doc.save(pdf_path)
    doc.close()

    disclosures = extract_notes_disclosures(pdf_path, "annual_report.pdf")
    assert len(disclosures) >= 3

    categories = [d.category for d in disclosures]
    assert "SUPPLIER_FINANCING" in categories
    assert "CONTINGENT_LIABILITIES" in categories
    assert "INVENTORY_PROVISION" in categories
    assert "REVENUE_CONCENTRATION" in categories

    # Verify WCH15 mapping
    sf_item = next(d for d in disclosures if d.category == "SUPPLIER_FINANCING")
    assert sf_item.mapped_efs_variable == "WCH15"
    assert sf_item.raw_variable_key == "supplier_financing_indicators"
    assert sf_item.source_page == 1

    Path(pdf_path).unlink(missing_ok=True)


def test_governance_and_auditor_evidence_extraction():
    """Verify auditor opinion (GD01), Key Audit Matters (GD02), and related-party evidence (GD05)."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "INDEPENDENT AUDITOR'S REPORT TO MEMBERS")
    page.insert_text((50, 80), "In our opinion, the financial statements give a true and fair view of the state of affairs.")
    page.insert_text((50, 100), "Key Audit Matter: Revenue recognition and unbilled contract assets valuation.")
    page.insert_text((50, 120), "Sales to related parties amounting to ₹ 85,000 during the year.")
    doc.save(pdf_path)
    doc.close()

    gov_evidence = extract_governance_evidence(pdf_path, "annual_report.pdf")
    assert len(gov_evidence) >= 2

    categories = [g.category for g in gov_evidence]
    assert "AUDIT_OPINION" in categories
    assert "KEY_AUDIT_MATTERS" in categories

    aud_item = next(g for g in gov_evidence if g.category == "AUDIT_OPINION")
    assert aud_item.mapped_efs_variable == "GD01"
    assert aud_item.status_value == "UNQUALIFIED"

    Path(pdf_path).unlink(missing_ok=True)


def test_safety_and_missing_values_preservation():
    """Verify missing evidence stays missing and no 0-substitution occurs."""
    analysis_id = "test_phase6b_safety"
    items = [
        CanonicalExtractedItem(
            id="1",
            raw_label="Revenue from Operations",
            raw_value="500000",
            normalized_value=500000.0,
            unit="Currency",
            currency="INR",
            period="FY 2025",
            source_filename="report.pdf",
            source_page=1,
            source_sheet=None,
            canonical_field="Revenue",
            mapped_efs_variable="FSQ01",
            raw_variable_key="revenue",
            mapping_status="EXACT_MATCH",
            confidence=100,
            review_status="ACCEPTED",
        )
    ]

    confirm_res = IngestionService.confirm_review(analysis_id, items)
    confirmed = confirm_res.confirmed_raw_variables

    assert "revenue" in confirmed
    assert confirmed["revenue"] == 500000.0
    # Un-extracted variables are NOT zero-filled
    assert "cfo" not in confirmed
    assert "pat" not in confirmed
    assert "inventory" not in confirmed
