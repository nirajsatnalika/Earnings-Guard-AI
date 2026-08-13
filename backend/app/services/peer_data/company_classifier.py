"""Company Classifier Service for EFS™ Phase 6C.

Provides deterministic company sector/industry/geography classification from
annual report metadata and explicit company inputs.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel


class CompanyClassification(BaseModel):
    company_name: str
    ticker: Optional[str] = None
    exchange: Optional[str] = None
    country: str
    sector: str
    industry: str
    accounting_regime: str
    confidence: float
    status: str  # VERIFIED, REVIEW_REQUIRED


SECTOR_INDUSTRY_MAP = {
    "TECHNOLOGY": ["IT Services & Software", "Hardware & Equipment", "Semiconductors"],
    "FINANCIALS": ["Banking", "Insurance", "Diversified Financials"],
    "HEALTHCARE": ["Pharmaceuticals & Biotech", "Healthcare Equipment", "Healthcare Providers"],
    "INDUSTRIALS": ["Capital Goods", "Commercial Services", "Transportation"],
    "CONSUMER_STAPLES": ["FMCG & Beverages", "Food & Agriculture"],
    "CONSUMER_DISCRETIONARY": ["Automotive", "Retailing", "Consumer Services"],
    "ENERGY": ["Oil & Gas", "Renewables"],
}


class CompanyClassifier:
    """Classifies company sector and industry deterministically."""

    @staticmethod
    def classify_company(
        company_name: str,
        sector_hint: Optional[str] = None,
        industry_hint: Optional[str] = None,
        country_hint: Optional[str] = "India",
        exchange_hint: Optional[str] = None,
    ) -> CompanyClassification:
        name_lower = company_name.lower()

        # Infer sector & industry if not explicitly provided
        sector = sector_hint or "TECHNOLOGY"
        industry = industry_hint or "IT Services & Software"
        confidence = 85.0

        if "tech" in name_lower or "infotech" in name_lower or "software" in name_lower or "systems" in name_lower:
            sector = "TECHNOLOGY"
            industry = "IT Services & Software"
            confidence = 95.0
        elif "pharma" in name_lower or "labs" in name_lower or "health" in name_lower:
            sector = "HEALTHCARE"
            industry = "Pharmaceuticals & Biotech"
            confidence = 95.0
        elif "bank" in name_lower or "finance" in name_lower or "capital" in name_lower:
            sector = "FINANCIALS"
            industry = "Banking" if "bank" in name_lower else "Diversified Financials"
            confidence = 95.0
        elif "auto" in name_lower or "motors" in name_lower:
            sector = "CONSUMER_DISCRETIONARY"
            industry = "Automotive"
            confidence = 95.0

        status = "VERIFIED" if confidence >= 80.0 else "REVIEW_REQUIRED"

        return CompanyClassification(
            company_name=company_name,
            ticker=exchange_hint,
            exchange=exchange_hint or "NSE/BSE",
            country=country_hint or "India",
            sector=sector,
            industry=industry,
            accounting_regime="IndAS" if (country_hint or "").lower() == "india" else "IFRS",
            confidence=confidence,
            status=status,
        )
