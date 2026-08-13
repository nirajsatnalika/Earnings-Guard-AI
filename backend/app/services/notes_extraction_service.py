"""Notes & Disclosure Extraction Service for Annual Reports.

Deterministically extracts structured evidence for footnote and disclosure items:
- Revenue Concentration & Deferred Revenue (FSQ13, FSQ14, FSQ15)
- Receivables Ageing & Impairment (WCH12)
- Inventory Provisions & Write-downs (WCH13)
- Contract Assets (WCH14)
- Supplier Financing & Reverse Factoring (WCH15)
- Intangible Assets, Goodwill & Capitalization (BSI03, BSI04, BSI05, BSI06)
- Off-Balance-Sheet & Contingent Liabilities (BSI10, BSI11, GD10)
- Lease Liabilities & Pension Deficits (BSI12, BSI13)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
import fitz  # PyMuPDF


class DisclosureEvidenceItem:

    def __init__(
        self,
        item_id: str,
        category: str,
        canonical_field: str,
        mapped_efs_variable: str,
        raw_variable_key: str,
        evidence_text: str,
        extracted_value: Optional[float],
        unit: Optional[str],
        currency: Optional[str],
        source_filename: str,
        source_page: int,
        source_section: str,
        confidence: int,
        mapping_status: str,
    ):
        self.item_id = item_id
        self.category = category
        self.canonical_field = canonical_field
        self.mapped_efs_variable = mapped_efs_variable
        self.raw_variable_key = raw_variable_key
        self.evidence_text = evidence_text
        self.extracted_value = extracted_value
        self.unit = unit
        self.currency = currency
        self.source_filename = source_filename
        self.source_page = source_page
        self.source_section = source_section
        self.confidence = confidence
        self.mapping_status = mapping_status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.item_id,
            "category": self.category,
            "canonical_field": self.canonical_field,
            "mapped_efs_variable": self.mapped_efs_variable,
            "raw_variable_key": self.raw_variable_key,
            "evidence_text": self.evidence_text,
            "extracted_value": self.extracted_value,
            "unit": self.unit,
            "currency": self.currency,
            "source_filename": self.source_filename,
            "source_page": self.source_page,
            "source_section": self.source_section,
            "confidence": self.confidence,
            "mapping_status": self.mapping_status,
            "review_status": "PENDING",
        }


DISCLOSURE_PATTERNS = [
    {
        "category": "SUPPLIER_FINANCING",
        "canonical_field": "Supplier Finance Arrangement",
        "mapped_efs_variable": "WCH15",
        "raw_variable_key": "supplier_financing_indicators",
        "patterns": [
            re.compile(r"supplier\s+financ(ing|e)\s+arrangement", re.IGNORECASE),
            re.compile(r"reverse\s+factoring", re.IGNORECASE),
            re.compile(r"trade\s+payables\s+funded\s+by\s+bank", re.IGNORECASE),
        ],
    },
    {
        "category": "CONTINGENT_LIABILITIES",
        "canonical_field": "Contingent Liabilities",
        "mapped_efs_variable": "BSI11",
        "raw_variable_key": "contingent_liabilities",
        "patterns": [
            re.compile(r"contingent\s+liabilit(ies|y)", re.IGNORECASE),
            re.compile(r"claims\s+against\s+the\s+company\s+not\s+acknowledged", re.IGNORECASE),
        ],
    },
    {
        "category": "INVENTORY_PROVISION",
        "canonical_field": "Inventory Provision",
        "mapped_efs_variable": "WCH13",
        "raw_variable_key": "inventory_provision_coverage",
        "patterns": [
            re.compile(r"provision\s+for\s+obsolete\s+inventory", re.IGNORECASE),
            re.compile(r"write-?down\s+of\s+inventory\s+(?:to|of)\s*([\d,.]+)", re.IGNORECASE),
        ],
    },
    {
        "category": "REVENUE_CONCENTRATION",
        "canonical_field": "Revenue Concentration",
        "mapped_efs_variable": "FSQ13",
        "raw_variable_key": "revenue_concentration",
        "patterns": [
            re.compile(r"single\s+external\s+customer\s+represented\s*([\d.]+)%", re.IGNORECASE),
            re.compile(r"top\s+customer\s+accounts?\s+for\s*([\d.]+)%", re.IGNORECASE),
        ],
    },
    {
        "category": "CONTRACT_ASSETS",
        "canonical_field": "Contract Assets",
        "mapped_efs_variable": "WCH14",
        "raw_variable_key": "contract_assets",
        "patterns": [
            re.compile(r"contract\s+assets?\s+(?:totaled|of)\s*([\d,.]+)", re.IGNORECASE),
            re.compile(r"unbilled\s+revenue\s+(?:of|amounting\s+to)\s*([\d,.]+)", re.IGNORECASE),
        ],
    },
    {
        "category": "GOODWILL_INTANGIBLES",
        "canonical_field": "Goodwill and Intangibles",
        "mapped_efs_variable": "BSI04",
        "raw_variable_key": "goodwill",
        "patterns": [
            re.compile(r"goodwill\s+arising\s+on\s+acquisition\s*(?:of|is)\s*([\d,.]+)", re.IGNORECASE),
            re.compile(r"capitalized\s+software\s+development\s+costs?\s*(?:of|is)\s*([\d,.]+)", re.IGNORECASE),
        ],
    },
]


def extract_notes_disclosures(pdf_path: str, filename: str) -> List[DisclosureEvidenceItem]:
    """Extracts footnote and disclosure items from PDF text streams."""
    evidence_items: List[DisclosureEvidenceItem] = []

    try:
        doc = fitz.open(pdf_path)
    except Exception:
        return evidence_items

    item_counter = 1

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text") or ""
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

        for p_info in DISCLOSURE_PATTERNS:
            for pat in p_info["patterns"]:
                for line in lines:
                    match = pat.search(line)
                    if match:
                        # Attempt to extract numeric value if captured in regex group
                        num_val: Optional[float] = None
                        if match.groups():
                            raw_group = match.group(1).replace(",", "")
                            try:
                                num_val = float(raw_group)
                            except ValueError:
                                num_val = None

                        item = DisclosureEvidenceItem(
                            item_id=f"disc_{item_counter}",
                            category=p_info["category"],
                            canonical_field=p_info["canonical_field"],
                            mapped_efs_variable=p_info["mapped_efs_variable"],
                            raw_variable_key=p_info["raw_variable_key"],
                            evidence_text=line[:300],
                            extracted_value=num_val,
                            unit="%" if "%" in line else "Currency",
                            currency="INR" if "₹" in line or "INR" in line else "USD" if "USD" in line else None,
                            source_filename=filename,
                            source_page=page_idx + 1,
                            source_section="Notes to Accounts",
                            confidence=90 if num_val is not None else 80,
                            mapping_status="HIGH_CONFIDENCE_MATCH",
                        )
                        evidence_items.append(item)
                        item_counter += 1
                        break  # Prevent duplicate matches for same pattern on same page

    doc.close()
    return evidence_items
