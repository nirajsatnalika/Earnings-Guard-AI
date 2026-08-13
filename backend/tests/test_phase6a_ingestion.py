"""Comprehensive pytest suite for Phase 6A Data Ingestion, PDF/Excel/CSV extraction,
normalization, canonical mapping, source traceability, and human review confirmation.
"""

from pathlib import Path
import tempfile
import fitz  # PyMuPDF
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.calculations.mapping.canonical_bridge import (
    STATUS_EXACT_MATCH,
    STATUS_HIGH_CONFIDENCE_MATCH,
    STATUS_REVIEW_REQUIRED,
    STATUS_UNMAPPED,
    get_efs_mapping,
)
from app.calculations.mapping.matcher import match_label
from app.calculations.normalizer.brackets import detect_negative
from app.calculations.normalizer.currency import detect_currency
from app.calculations.normalizer.normalizer import Normalizer
from app.calculations.normalizer.units import detect_unit
from app.main import app
from app.services.pdf_extraction_service import parse_pdf
from app.services.ingestion_service import IngestionService
from app.schemas.ingest import CanonicalExtractedItem

client = TestClient(app)


def test_normalization_currencies_and_units():
    """Verify currency codes, magnitude units (crore, million, billion, lakhs), and brackets."""
    # Currencies
    assert detect_currency("₹ 1,25,000") == "INR"
    assert detect_currency("USD 500,000") == "USD"
    assert detect_currency("€ 45,000") == "EUR"
    assert detect_currency("£ 10,000") == "GBP"

    # Units
    unit_name, scale = detect_unit("in crores")
    assert unit_name == "crores"
    assert scale == 10_000_000.0

    unit_name, scale = detect_unit("USD in millions")
    assert unit_name == "millions"
    assert scale == 1_000_000.0

    unit_name, scale = detect_unit("in lakhs")
    assert unit_name == "lakhs"
    assert scale == 100_000.0

    unit_name, scale = detect_unit("in thousands")
    assert unit_name == "thousands"
    assert scale == 1_000.0

    # Brackets / Negative values
    is_neg, val_str = detect_negative("(4,250)")
    assert is_neg is True
    assert val_str == "4,250"

    cell = Normalizer._normalize_cell("(4,250)", None, None, 1.0)
    assert cell.is_negative is True
    assert cell.normalized_value == -4250.0

    # Clean string float
    cell_clean = Normalizer._normalize_cell("1,250.50", None, None, 1.0)
    assert cell_clean.normalized_value == 1250.50


def test_canonical_mapping_and_bridge():
    """Verify exact, alias, and fuzzy candidate matching to canonical fields and EFS variables."""
    # Exact Match
    match1 = match_label("Revenue")
    assert match1.matched is True
    assert match1.canonical == "Revenue"
    raw_key1, efs_id1, status1 = get_efs_mapping(match1.canonical, match1.confidence, match1.strategy)
    assert raw_key1 == "revenue"
    assert efs_id1 == "FSQ01"
    assert status1 == STATUS_EXACT_MATCH

    # Alias Match
    match2 = match_label("Revenue from Operations")
    assert match2.matched is True
    assert match2.canonical == "Revenue"
    raw_key2, efs_id2, status2 = get_efs_mapping(match2.canonical, match2.confidence, match2.strategy)
    assert raw_key2 == "revenue"
    assert efs_id2 == "FSQ01"
    assert status2 == STATUS_HIGH_CONFIDENCE_MATCH

    # Trade Receivables -> Receivables -> accounts_receivable -> FSQ02
    match3 = match_label("Trade Receivables")
    assert match3.matched is True
    assert match3.canonical == "Receivables"
    raw_key3, efs_id3, _ = get_efs_mapping(match3.canonical, match3.confidence, match3.strategy)
    assert raw_key3 == "accounts_receivable"
    assert efs_id3 == "FSQ02"

    # Cash Flow From Operating Activities -> Operating Cash Flow -> cfo -> CFI01
    match4 = match_label("Cash Flow From Operations")
    assert match4.matched is True
    assert match4.canonical == "Operating Cash Flow"
    raw_key4, efs_id4, _ = get_efs_mapping(match4.canonical, match4.confidence, match4.strategy)
    assert raw_key4 == "cfo"
    assert efs_id4 == "CFI01"

    # Unmapped Field
    match_unmapped = match_label("QWERTYUIOP123456")
    raw_key_u, efs_id_u, status_u = get_efs_mapping(match_unmapped.canonical, match_unmapped.confidence, match_unmapped.strategy)
    assert status_u == STATUS_UNMAPPED
    assert raw_key_u is None


def test_pdf_extraction_text_and_scanned():
    """Verify PyMuPDF text PDF extraction and scanned PDF detection."""
    # 1. Test Text-based PDF creation and extraction
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Infosys Limited Annual Financial Statement 2025")
    page.insert_text((50, 100), "Revenue from Operations                       500,000")
    page.insert_text((50, 120), "Trade Receivables                             80,000")
    page.insert_text((50, 140), "Cash Flow From Operations                     60,000")
    doc.save(pdf_path)
    doc.close()

    res = parse_pdf(pdf_path)
    assert res.is_scanned is False
    assert len(res.provenance) >= 2
    labels = [p["original_label"] for p in res.provenance]
    assert "Revenue from Operations" in labels
    assert "Trade Receivables" in labels

    # Path cleanup
    Path(pdf_path).unlink(missing_ok=True)

    # 2. Test Scanned PDF detection (blank page with no text stream)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_scanned:
        scanned_path = tmp_scanned.name

    doc_scanned = fitz.open()
    doc_scanned.new_page()  # empty page with 0 text
    doc_scanned.save(scanned_path)
    doc_scanned.close()

    scanned_res = parse_pdf(scanned_path)
    assert scanned_res.is_scanned is True
    assert "Scanned PDF detected" in scanned_res.message

    Path(scanned_path).unlink(missing_ok=True)


def test_human_review_confirmation_to_raw_variables():
    """Verify human review actions (accept, edit, reject) correctly filter raw_variables."""
    analysis_id = "test_review_analysis_1"
    items = [
        CanonicalExtractedItem(
            id="1",
            raw_label="Revenue from Operations",
            raw_value="500000",
            normalized_value=500000.0,
            unit=None,
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
        ),
        CanonicalExtractedItem(
            id="2",
            raw_label="Trade Receivables",
            raw_value="80000",
            normalized_value=85000.0,  # User edited
            unit=None,
            currency="INR",
            period="FY 2025",
            source_filename="report.pdf",
            source_page=1,
            source_sheet=None,
            canonical_field="Receivables",
            mapped_efs_variable="FSQ02",
            raw_variable_key="accounts_receivable",
            mapping_status="HIGH_CONFIDENCE_MATCH",
            confidence=95,
            review_status="EDITED",
        ),
        CanonicalExtractedItem(
            id="3",
            raw_label="Suspicious Item",
            raw_value="99999",
            normalized_value=99999.0,
            unit=None,
            currency=None,
            period=None,
            source_filename="report.pdf",
            source_page=1,
            source_sheet=None,
            canonical_field=None,
            mapped_efs_variable=None,
            raw_variable_key=None,
            mapping_status="UNMAPPED",
            confidence=0,
            review_status="REJECTED",
        ),
    ]

    confirm_res = IngestionService.confirm_review(analysis_id, items)
    confirmed = confirm_res.confirmed_raw_variables

    assert "revenue" in confirmed
    assert confirmed["revenue"] == 500000.0
    assert "accounts_receivable" in confirmed
    assert confirmed["accounts_receivable"] == 85000.0
    # Rejected & missing keys are not filled with zeros
    assert "cfo" not in confirmed
    assert "pat" not in confirmed
