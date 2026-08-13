"""Ingestion Service — orchestrates Document Extraction, Normalization, Mapping, and Human Review.

Builds the canonical representation for uploaded financial documents (PDF, XLSX, XLS, CSV)
and enforces human review before final confirmation into raw_variables for EFSEngine.
"""

from __future__ import annotations

import pandas as pd
from typing import Any

from app.calculations.mapping.canonical_bridge import (
    STATUS_EXACT_MATCH,
    STATUS_HIGH_CONFIDENCE_MATCH,
    STATUS_REVIEW_REQUIRED,
    STATUS_UNMAPPED,
    get_efs_mapping,
)
from app.calculations.mapping.matcher import match_label
from app.calculations.normalizer import Normalizer
from app.core.exceptions import AnalysisNotFoundError
from app.core.logging import get_logger
from app.schemas.ingest import CanonicalExtractedItem, ConfirmReviewResponse, IngestResponse
from app.services.parser_service import ParserService

logger = get_logger(__name__)

# In-memory store: analysis_id -> list of CanonicalExtractedItem
_ingest_store: dict[str, list[CanonicalExtractedItem]] = {}


class IngestionService:
    """Orchestrates document extraction, normalization, canonical mapping, and review."""

    @staticmethod
    def process_ingestion(analysis_id: str) -> IngestResponse:
        # 1. Trigger parser engine
        parse_res = ParserService.parse(analysis_id)
        pdf_statuses = ParserService.get_pdf_status(analysis_id)

        # 2. Check for scanned PDF
        for pdf_stat in pdf_statuses:
            if pdf_stat.get("is_scanned"):
                logger.info("Analysis %s contains scanned PDF %s", analysis_id, pdf_stat.get("filename"))
                return IngestResponse(
                    analysis_id=analysis_id,
                    status="scanned_pdf_detected",
                    is_scanned_pdf=True,
                    scanned_pdf_message=pdf_stat.get("message")
                    or "Scanned PDF detected. OCR support will be available in a future release.",
                    extracted_items=[],
                )

        # 3. Retrieve frames and provenance
        frames = ParserService.get_frames(analysis_id)
        if frames is None:
            raise AnalysisNotFoundError(analysis_id)

        pdf_provenance = ParserService.get_provenance(analysis_id)
        extracted_items: list[CanonicalExtractedItem] = []
        item_counter = 1

        if pdf_provenance:
            # Process PDF extracted provenance records
            for prov in pdf_provenance:
                filename = prov.get("source_filename", "document.pdf")
                page_num = prov.get("source_page")
                raw_label = str(prov.get("original_label", "")).strip()
                raw_val = str(prov.get("raw_value", "")).strip()

                if not raw_label or not raw_val:
                    continue

                # Normalize raw value
                norm_cell = Normalizer._normalize_cell(raw_val, sheet_currency=None, sheet_unit=None, sheet_scale=1.0)
                
                # Match canonical field
                match_res = match_label(raw_label)
                canonical_field = match_res.canonical if match_res.matched else None
                confidence = match_res.confidence if match_res.matched else 0
                strategy = match_res.strategy

                raw_key, efs_id, mapping_status = get_efs_mapping(canonical_field, confidence, strategy)

                # Determine review necessity
                if norm_cell.notes and "unclear" in norm_cell.notes.lower():
                    mapping_status = STATUS_REVIEW_REQUIRED

                # Default initial status: exact matches auto-set to PENDING for user approval
                review_status = "PENDING"

                extracted_items.append(
                    CanonicalExtractedItem(
                        id=f"item_{item_counter}",
                        raw_label=raw_label,
                        raw_value=raw_val,
                        normalized_value=norm_cell.normalized_value,
                        unit=norm_cell.unit,
                        currency=norm_cell.currency,
                        period="FY 2025",
                        source_filename=filename,
                        source_page=page_num,
                        source_sheet=None,
                        canonical_field=canonical_field,
                        mapped_efs_variable=efs_id,
                        raw_variable_key=raw_key,
                        mapping_status=mapping_status,
                        confidence=confidence,
                        review_status=review_status,
                        notes=norm_cell.notes,
                    )
                )
                item_counter += 1
        else:
            # Process Excel / CSV frames
            for statement_label, sheets in frames.items():
                for sheet_name, frame in sheets.items():
                    if frame.empty:
                        continue
                    # First column is line item, subsequent columns are values
                    cols = frame.columns
                    label_col = cols[0]
                    for row_idx in range(len(frame)):
                        raw_label_val = frame.iat[row_idx, 0]
                        if pd.isna(raw_label_val) or not str(raw_label_val).strip():
                            continue
                        raw_label = str(raw_label_val).strip()

                        # Read first numeric value column
                        for col_idx in range(1, frame.shape[1]):
                            raw_val_cell = frame.iat[row_idx, col_idx]
                            if pd.isna(raw_val_cell) or not str(raw_val_cell).strip():
                                continue
                            raw_val = str(raw_val_cell).strip()

                            norm_cell = Normalizer._normalize_cell(raw_val_cell, None, None, 1.0)
                            match_res = match_label(raw_label)
                            canonical_field = match_res.canonical if match_res.matched else None
                            confidence = match_res.confidence if match_res.matched else 0
                            strategy = match_res.strategy

                            raw_key, efs_id, mapping_status = get_efs_mapping(canonical_field, confidence, strategy)

                            extracted_items.append(
                                CanonicalExtractedItem(
                                    id=f"item_{item_counter}",
                                    raw_label=raw_label,
                                    raw_value=raw_val,
                                    normalized_value=norm_cell.normalized_value,
                                    unit=norm_cell.unit,
                                    currency=norm_cell.currency,
                                    period="FY 2025",
                                    source_filename=f"{statement_label}.xlsx",
                                    source_page=None,
                                    source_sheet=sheet_name,
                                    canonical_field=canonical_field,
                                    mapped_efs_variable=efs_id,
                                    raw_variable_key=raw_key,
                                    mapping_status=mapping_status,
                                    confidence=confidence,
                                    review_status="PENDING",
                                    notes=norm_cell.notes,
                                )
                            )
                            item_counter += 1
                            break  # Process primary value column for each row

        _ingest_store[analysis_id] = extracted_items

        # Process Notes & Disclosure and Governance evidence for PDF documents
        for pdf_stat in pdf_statuses:
            pdf_filename = pdf_stat.get("filename", "annual_report.pdf")
            from app.core.config import settings
            pdf_path = str(settings.UPLOAD_DIR / analysis_id / pdf_filename)
            import os
            if os.path.exists(pdf_path):
                # 1. Footnote & Disclosures
                from app.services.notes_extraction_service import extract_notes_disclosures
                notes_items = extract_notes_disclosures(pdf_path, pdf_filename)
                for n_item in notes_items:
                    item_dict = n_item.to_dict()
                    extracted_items.append(
                        CanonicalExtractedItem(
                            id=f"disc_{item_counter}",
                            raw_label=item_dict["canonical_field"],
                            raw_value=str(item_dict["extracted_value"]) if item_dict["extracted_value"] is not None else item_dict["evidence_text"][:50],
                            normalized_value=item_dict["extracted_value"],
                            unit=item_dict["unit"],
                            currency=item_dict["currency"],
                            period="FY 2025",
                            evidence_category="NOTE_DISCLOSURE",
                            evidence_text=item_dict["evidence_text"],
                            source_filename=pdf_filename,
                            source_page=item_dict["source_page"],
                            source_section=item_dict["source_section"],
                            canonical_field=item_dict["canonical_field"],
                            mapped_efs_variable=item_dict["mapped_efs_variable"],
                            raw_variable_key=item_dict["raw_variable_key"],
                            mapping_status=item_dict["mapping_status"],
                            confidence=item_dict["confidence"],
                            review_status="PENDING",
                        )
                    )
                    item_counter += 1

                # 2. Governance & Auditor Evidence
                from app.services.governance_extraction_service import extract_governance_evidence
                gov_items = extract_governance_evidence(pdf_path, pdf_filename)
                for g_item in gov_items:
                    item_dict = g_item.to_dict()
                    extracted_items.append(
                        CanonicalExtractedItem(
                            id=f"gov_{item_counter}",
                            raw_label=item_dict["canonical_field"],
                            raw_value=item_dict["status_value"],
                            normalized_value=item_dict["numeric_value"],
                            unit="Categorical",
                            currency=None,
                            period="FY 2025",
                            evidence_category="GOVERNANCE_AUDITOR",
                            evidence_text=item_dict["evidence_text"],
                            source_filename=pdf_filename,
                            source_page=item_dict["source_page"],
                            source_section=item_dict["source_section"],
                            canonical_field=item_dict["canonical_field"],
                            mapped_efs_variable=item_dict["mapped_efs_variable"],
                            raw_variable_key=item_dict["raw_variable_key"],
                            mapping_status=item_dict["mapping_status"],
                            confidence=item_dict["confidence"],
                            review_status="PENDING",
                        )
                    )
                    item_counter += 1

        _ingest_store[analysis_id] = extracted_items
        logger.info("Analysis %s: extracted %d total canonical & evidence item(s) for review", analysis_id, len(extracted_items))

        return IngestResponse(
            analysis_id=analysis_id,
            status="ingested",
            is_scanned_pdf=False,
            scanned_pdf_message=None,
            extracted_items=extracted_items,
        )

    @staticmethod
    def get_extracted_items(analysis_id: str) -> list[CanonicalExtractedItem]:
        """Access extracted canonical items for an analysis."""
        return _ingest_store.get(analysis_id, [])

    @staticmethod
    def confirm_review(analysis_id: str, confirmed_items: list[CanonicalExtractedItem]) -> ConfirmReviewResponse:
        """Process human review confirmations into a final raw_variables payload."""
        _ingest_store[analysis_id] = confirmed_items

        raw_vars: dict[str, float] = {}

        for item in confirmed_items:
            # Only ACCEPTED or EDITED items with valid keys and normalized numeric values pass through
            if item.review_status in ("ACCEPTED", "EDITED") and item.raw_variable_key:
                if item.normalized_value is not None:
                    raw_vars[item.raw_variable_key] = float(item.normalized_value)

        logger.info(
            "Analysis %s: confirmed %d raw variable(s) for EFS assessment",
            analysis_id,
            len(raw_vars),
        )
        return ConfirmReviewResponse(
            analysis_id=analysis_id,
            confirmed_raw_variables=raw_vars,
        )
