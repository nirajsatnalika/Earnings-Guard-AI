"""Free Data Source Registry for EFS™ Phase 6C.

Central registry tracking free, open-source, and public disclosure data sources.
Prohibits paid market terminals.
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class DataRegistrySource(BaseModel):
    source_id: str
    source_name: str
    source_type: str  # PUBLIC_FILING, REGULATOR_NOTICE, STOCK_EXCHANGE
    country: str
    url: str
    is_free: bool = True
    is_public: bool = True
    requires_payment: bool = False
    supported_metrics: List[str]
    reliability_level: str  # HIGH, MEDIUM


FREE_DATA_SOURCES: List[DataRegistrySource] = [
    DataRegistrySource(
        source_id="SRC_ANNUAL_REPORTS",
        source_name="Public Company Annual Reports & Investor Filings",
        source_type="PUBLIC_FILING",
        country="Global / India",
        url="https://www.bseindia.com / https://www.sec.gov/edgar",
        is_free=True,
        is_public=True,
        requires_payment=False,
        supported_metrics=["effective_tax_rate", "auditor_tenure", "promoter_pledge", "operating_earnings"],
        reliability_level="HIGH",
    ),
    DataRegistrySource(
        source_id="SRC_STOCK_EXCHANGE",
        source_name="BSE / NSE Official Corporate Disclosures",
        source_type="STOCK_EXCHANGE",
        country="India",
        url="https://www.bseindia.com/corporates/corporate_action.aspx",
        is_free=True,
        is_public=True,
        requires_payment=False,
        supported_metrics=["promoter_pledge", "auditor_change", "shareholding_pattern"],
        reliability_level="HIGH",
    ),
    DataRegistrySource(
        source_id="SRC_REGULATOR_NOTICES",
        source_name="Official Regulatory Orders & Orders Registry",
        source_type="REGULATOR_NOTICE",
        country="India / US",
        url="https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2",
        is_free=True,
        is_public=True,
        requires_payment=False,
        supported_metrics=["regulatory_enforcement", "legal_orders"],
        reliability_level="HIGH",
    ),
    DataRegistrySource(
        source_id="SRC_SEC_EDGAR",
        source_name="SEC EDGAR Company Filings (Free Public API)",
        source_type="PUBLIC_FILING",
        country="United States",
        url="https://data.sec.gov/api/xbrl/companyfacts/",
        is_free=True,
        is_public=True,
        requires_payment=False,
        supported_metrics=["effective_tax_rate", "auditor_tenure", "operating_earnings"],
        reliability_level="HIGH",
    ),
]


class SourceRegistry:
    """Registry manager for free data sources."""

    @staticmethod
    def list_sources() -> List[DataRegistrySource]:
        return [s for s in FREE_DATA_SOURCES if s.is_free and not s.requires_payment]

    @staticmethod
    def get_source_for_metric(metric: str) -> List[DataRegistrySource]:
        return [s for s in FREE_DATA_SOURCES if metric in s.supported_metrics and s.is_free]
