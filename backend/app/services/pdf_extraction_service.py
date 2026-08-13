"""PDF document extraction service — extracts financial statement text & tables locally.

Uses PyMuPDF (fitz) for fast layout/text stream extraction and pdfplumber for
table structure recognition. Preserves document provenance (filename, page, raw text,
original labels, and values). Detects scanned PDFs without extractable text streams
and defers gracefully without fabricating values.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import pandas as pd
import pdfplumber

from app.core.exceptions import FileParsingError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Regular expressions for detecting numbers in financial statement lines
_NUMERIC_PATTERN = re.compile(
    r"(?:\(?[\$€£₹]?\s*-?\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?\)?|\b\d+(?:\.\d+)?\b)"
)
_LINE_ITEM_REGEX = re.compile(
    r"^(?P<label>[A-Za-z\s&\-\/\(\)\.,']+?)\s{2,}(?P<values>(?:[\(\$\€\£\₹\-]?\s*\d[\d,]*\.?\d*\)?\s*)+)$"
)


class PDFExtractionResult:
    """Container for PDF extraction outputs across pages."""

    def __init__(
        self,
        filename: str,
        is_scanned: bool = False,
        message: str | None = None,
        frames: dict[str, pd.DataFrame] | None = None,
        provenance: list[dict[str, Any]] | None = None,
    ) -> None:
        self.filename = filename
        self.is_scanned = is_scanned
        self.message = message
        self.frames = frames or {}
        self.provenance = provenance or []


def _extract_page_rows_fitz(page: fitz.Page, page_num: int, filename: str) -> list[dict[str, Any]]:
    """Extract line item rows from a single PDF page using PyMuPDF."""
    rows: list[dict[str, Any]] = []
    text = page.get_text("text") or ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        # Check if line contains text label and numeric figures
        match = _LINE_ITEM_REGEX.match(line)
        if match:
            raw_label = match.group("label").strip()
            values_str = match.group("values").strip()
            num_matches = _NUMERIC_PATTERN.findall(values_str)
            if num_matches and len(raw_label) >= 2:
                current_val = num_matches[0]
                prior_val = num_matches[1] if len(num_matches) > 1 else None
                rows.append({
                    "source_filename": filename,
                    "source_page": page_num,
                    "raw_text": line,
                    "original_label": raw_label,
                    "raw_value": current_val,
                    "prior_raw_value": prior_val,
                })
        else:
            # Secondary check: split line by tabs or multiple spaces
            parts = [p.strip() for p in re.split(r"\s{2,}|\t", line) if p.strip()]
            if len(parts) >= 2:
                raw_label = parts[0]
                possible_nums = [p for p in parts[1:] if _NUMERIC_PATTERN.search(p)]
                if possible_nums and any(c.isalpha() for c in raw_label) and len(raw_label) >= 2:
                    rows.append({
                        "source_filename": filename,
                        "source_page": page_num,
                        "raw_text": line,
                        "original_label": raw_label,
                        "raw_value": possible_nums[0],
                        "prior_raw_value": possible_nums[1] if len(possible_nums) > 1 else None,
                    })

    return rows


def _extract_page_tables_plumber(pdf_path: str, page_num: int, filename: str) -> list[dict[str, Any]]:
    """Extract table rows from a PDF page using pdfplumber."""
    rows: list[dict[str, Any]] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_num <= len(pdf.pages):
                page = pdf.pages[page_num - 1]
                tables = page.extract_tables()
                for table in tables:
                    for r in table:
                        if not r:
                            continue
                        clean_cells = [str(c).strip() for c in r if c is not None and str(c).strip()]
                        if len(clean_cells) >= 2:
                            raw_label = clean_cells[0]
                            nums = [c for c in clean_cells[1:] if _NUMERIC_PATTERN.search(c)]
                            if nums and any(char.isalpha() for char in raw_label) and len(raw_label) >= 2:
                                rows.append({
                                    "source_filename": filename,
                                    "source_page": page_num,
                                    "raw_text": " | ".join(clean_cells),
                                    "original_label": raw_label,
                                    "raw_value": nums[0],
                                    "prior_raw_value": nums[1] if len(nums) > 1 else None,
                                })
    except Exception as exc:
        logger.debug("pdfplumber table extraction note for %s page %d: %s", filename, page_num, exc)
    return rows


def parse_pdf(path: str) -> PDFExtractionResult:
    """Parse a PDF financial report using PyMuPDF and pdfplumber.

    Returns a PDFExtractionResult containing extracted DataFrames and row provenance.
    If the document has 0 extractable text streams (scanned image PDF), returns
    is_scanned=True with an informative user-facing message.
    """
    file_path = Path(path)
    filename = file_path.name

    try:
        doc = fitz.open(str(file_path))
    except Exception as exc:
        raise FileParsingError(filename, f"Could not open PDF file: {exc}") from exc

    if doc.is_encrypted:
        raise FileParsingError(filename, "Password protected PDF files are not supported.")

    total_pages = len(doc)
    if total_pages == 0:
        raise FileParsingError(filename, "PDF file contains 0 pages.")

    # 1. Total text stream inspection across all pages
    all_text = ""
    for page in doc:
        all_text += page.get_text("text") or ""

    clean_text = all_text.strip()

    # If document contains no extractable text stream (< 20 non-space characters total)
    if len(clean_text) < 20:
        logger.info("PDF %s detected as scanned document (total text length: %d)", filename, len(clean_text))
        return PDFExtractionResult(
            filename=filename,
            is_scanned=True,
            message="Scanned PDF detected. OCR support will be available in a future release.",
        )

    # 2. Extract structured line items page by page
    all_provenance: list[dict[str, Any]] = []
    seen_keys: set[tuple[int, str, str]] = set()

    for page_num in range(1, total_pages + 1):
        page = doc[page_num - 1]
        
        # PyMuPDF line extraction
        fitz_rows = _extract_page_rows_fitz(page, page_num, filename)
        
        # pdfplumber table extraction
        plumber_rows = _extract_page_tables_plumber(str(file_path), page_num, filename)

        combined = fitz_rows + plumber_rows
        for item in combined:
            key = (page_num, item["original_label"], item["raw_value"])
            if key not in seen_keys:
                seen_keys.add(key)
                all_provenance.append(item)

    doc.close()

    # Build DataFrames for downstream normalizer/mapping engines
    if not all_provenance:
        # Fallback DataFrame if no structured line items detected
        df = pd.DataFrame(columns=["Line Item", "Value", "Prior Value"])
    else:
        records = [
            {
                "Line Item": item["original_label"],
                "Value": item["raw_value"],
                "Prior Value": item["prior_raw_value"],
            }
            for item in all_provenance
        ]
        df = pd.DataFrame(records)

    frames: dict[str, pd.DataFrame] = {"Financial Statement": df}

    return PDFExtractionResult(
        filename=filename,
        is_scanned=False,
        frames=frames,
        provenance=all_provenance,
    )
