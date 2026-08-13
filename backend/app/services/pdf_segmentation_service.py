"""Document Section Segmentation Service for Annual Reports.

Deterministically segments PDF pages and text streams into functional report sections:
- Financial Statements (Balance Sheet, Profit & Loss, Cash Flow)
- Notes to Accounts (Revenue, Receivables, Inventory, Provisions, Related Parties, Contingencies, Intangibles, Supplier Financing)
- Auditor's Report & Key Audit Matters (KAM)
- Governance & Director Disclosures
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional
import fitz  # PyMuPDF


SECTION_PATTERNS: Dict[str, List[re.Pattern]] = {
    "BALANCE_SHEET": [
        re.compile(r"consolidated\s+balance\s+sheet", re.IGNORECASE),
        re.compile(r"balance\s+sheet", re.IGNORECASE),
        re.compile(r"statement\s+of\s+financial\s+position", re.IGNORECASE),
    ],
    "PROFIT_LOSS": [
        re.compile(r"statement\s+of\s+profit\s+and\s+loss", re.IGNORECASE),
        re.compile(r"income\s+statement", re.IGNORECASE),
        re.compile(r"statement\s+of\s+comprehensive\s+income", re.IGNORECASE),
    ],
    "CASH_FLOW": [
        re.compile(r"statement\s+of\s+cash\s+flows?", re.IGNORECASE),
        re.compile(r"cash\s+flow\s+statement", re.IGNORECASE),
    ],
    "AUDITORS_REPORT": [
        re.compile(r"independent\s+auditor'?s\s+report", re.IGNORECASE),
        re.compile(r"report\s+of\s+the\s+independent\s+auditor", re.IGNORECASE),
        re.compile(r"statutory\s+auditor'?s\s+report", re.IGNORECASE),
    ],
    "KEY_AUDIT_MATTERS": [
        re.compile(r"key\s+audit\s+matters", re.IGNORECASE),
        re.compile(r"matters\s+that\s+involved\s+auditor\s+judgment", re.IGNORECASE),
    ],
    "NOTES_REVENUE": [
        re.compile(r"note\s*\d*.*revenue\s+from\s+operations", re.IGNORECASE),
        re.compile(r"revenue\s+recognition\s+policy", re.IGNORECASE),
        re.compile(r"contract\s+assets?\s+and\s+liabilities", re.IGNORECASE),
    ],
    "NOTES_RECEIVABLES": [
        re.compile(r"note\s*\d*.*trade\s+receivables", re.IGNORECASE),
        re.compile(r"receivables\s+ageing", re.IGNORECASE),
        re.compile(r"allowance\s+for\s+credit\s+losses", re.IGNORECASE),
    ],
    "NOTES_INVENTORY": [
        re.compile(r"note\s*\d*.*inventories", re.IGNORECASE),
        re.compile(r"inventory\s+provision", re.IGNORECASE),
        re.compile(r"write-?down\s+of\s+inventories", re.IGNORECASE),
    ],
    "NOTES_SUPPLIER_FINANCE": [
        re.compile(r"supplier\s+financ(ing|e)\s+arrangement", re.IGNORECASE),
        re.compile(r"reverse\s+factoring", re.IGNORECASE),
        re.compile(r"trade\s+payables\s+financing", re.IGNORECASE),
    ],
    "NOTES_RELATED_PARTIES": [
        re.compile(r"note\s*\d*.*related\s+party\s+disclosures", re.IGNORECASE),
        re.compile(r"related\s+party\s+transactions", re.IGNORECASE),
    ],
    "NOTES_CONTINGENCIES": [
        re.compile(r"note\s*\d*.*contingent\s+liabilities", re.IGNORECASE),
        re.compile(r"litigation\s+and\s+claims", re.IGNORECASE),
        re.compile(r"commitments\s+and\s+contingencies", re.IGNORECASE),
    ],
    "NOTES_INTANGIBLES": [
        re.compile(r"note\s*\d*.*goodwill\s+and\s+intangible\s+assets", re.IGNORECASE),
        re.compile(r"capitalized\s+software", re.IGNORECASE),
        re.compile(r"development\s+costs", re.IGNORECASE),
    ],
    "GOVERNANCE": [
        re.compile(r"corporate\s+governance\s+report", re.IGNORECASE),
        re.compile(r"board\s+of\s+directors\s+report", re.IGNORECASE),
        re.compile(r"promoter\s+shareholding", re.IGNORECASE),
    ],
}


class SegmentedPage:

    def __init__(self, page_num: int, primary_section: str, matched_patterns: List[str], text_snippet: str):
        self.page_num = page_num
        self.primary_section = primary_section
        self.matched_patterns = matched_patterns
        self.text_snippet = text_snippet

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_num": self.page_num,
            "primary_section": self.primary_section,
            "matched_patterns": self.matched_patterns,
            "text_snippet": self.text_snippet[:200],
        }


def segment_document_pages(pdf_path: str) -> List[SegmentedPage]:
    """Scans all pages in a PDF and assigns section labels based on header/pattern matching."""
    segmented: List[SegmentedPage] = []

    try:
        doc = fitz.open(pdf_path)
    except Exception:
        return segmented

    current_section = "GENERAL"

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text") or ""
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

        matched_sections: List[str] = []
        for section_key, patterns in SECTION_PATTERNS.items():
            for pat in patterns:
                if any(pat.search(line) for line in lines[:10]):  # Search page headers
                    matched_sections.append(section_key)
                    break

        if matched_sections:
            current_section = matched_sections[0]

        first_snippet = text[:300].replace("\n", " ")
        segmented.append(
            SegmentedPage(
                page_num=page_idx + 1,
                primary_section=current_section,
                matched_patterns=matched_sections,
                text_snippet=first_snippet,
            )
        )

    doc.close()
    return segmented
