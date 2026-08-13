"""Canonical Field Bridge — maps Canonical Financial Fields to EFS raw_variables and variable IDs.

Implements the multi-stage mapping pipeline:
  Document Label -> Canonical Field -> EFS Variable Key & Primary Variable ID
"""

from __future__ import annotations

from typing import Any

CANONICAL_TO_EFS: dict[str, tuple[str, str]] = {
    # Core Financial Statements
    "Revenue": ("revenue", "FSQ01"),
    "Prior Revenue": ("prior_revenue", "FSQ01"),
    "Receivables": ("accounts_receivable", "FSQ02"),
    "Prior Receivables": ("prior_accounts_receivable", "FSQ02"),
    "Operating Cash Flow": ("cfo", "CFI01"),
    "PAT": ("pat", "FSQ07"),
    "Cost of Goods Sold": ("cogs", "FSQ05"),
    "Inventory": ("inventory", "WCH04"),
    "Trade Payables": ("accounts_payable", "WCH07"),
    "Total Assets": ("total_assets", "BSI01"),
    "Prior Total Assets": ("prior_total_assets", "BSI01"),
    "Depreciation": ("depreciation", "AQ11"),
    "CapEx": ("capex", "CFI04"),
    "Total Debt": ("total_debt", "BSI09"),
    "Equity": ("equity", "BSI11"),
    "EBIT": ("ebit", "FSQ06"),

    # Footnotes & Disclosures
    "Revenue Concentration": ("revenue_concentration", "FSQ13"),
    "Contract Liabilities": ("contract_liabilities", "FSQ14"),
    "Deferred Revenue": ("deferred_revenue", "FSQ15"),
    "Receivable Concentration": ("receivables_concentration", "WCH12"),
    "Inventory Provision": ("inventory_provision_coverage", "WCH13"),
    "Contract Assets": ("contract_assets", "WCH14"),
    "Supplier Finance Arrangement": ("supplier_financing_indicators", "WCH15"),
    "Intangibles": ("intangibles", "BSI03"),
    "Goodwill": ("goodwill", "BSI04"),
    "Goodwill and Intangibles": ("goodwill", "BSI04"),
    "Capitalized Development": ("capitalized_development", "BSI05"),
    "Capitalized Software": ("capitalized_software", "BSI06"),
    "Off-Balance-Sheet Exposure": ("off_balance_sheet_exposure", "BSI10"),
    "Contingent Liabilities": ("contingent_liabilities", "BSI11"),
    "Lease Liabilities": ("lease_liabilities", "BSI12"),
    "Pension Deficit": ("pension_deficit", "BSI13"),

    # Governance & Auditor Evidence
    "Auditor Opinion": ("qualified_audit_opinion", "GD01"),
    "Key Audit Matters": ("key_audit_matter_severity", "GD02"),
    "Auditor Change": ("auditor_change", "GD03"),
    "Audit Tenure": ("audit_tenure", "GD04"),
    "Related Party Transactions": ("related_party_transactions", "GD05"),
    "Promoter Share Pledge": ("promoter_pledge", "GD06"),
    "Accounting Policy Change": ("accounting_policy_change", "GD07"),
    "Restatement of Financials": ("restatement_adjustments", "GD08"),
    "Regulatory Action": ("regulatory_action", "GD09"),
    "Litigation Exposure": ("litigation_exposure", "GD10"),
}

# Mapping status definitions
STATUS_EXACT_MATCH = "EXACT_MATCH"
STATUS_HIGH_CONFIDENCE_MATCH = "HIGH_CONFIDENCE_MATCH"
STATUS_REVIEW_REQUIRED = "REVIEW_REQUIRED"
STATUS_UNMAPPED = "UNMAPPED"


def get_efs_mapping(canonical_field: str | None, confidence: int, strategy: str) -> tuple[str | None, str | None, str]:
    """Resolve EFS raw_variable key, primary EFS variable ID, and mapping status."""
    if not canonical_field or canonical_field not in CANONICAL_TO_EFS:
        return None, None, STATUS_UNMAPPED

    raw_key, efs_id = CANONICAL_TO_EFS[canonical_field]

    if confidence >= 100:
        status = STATUS_EXACT_MATCH
    elif confidence >= 90:
        status = STATUS_HIGH_CONFIDENCE_MATCH
    else:
        status = STATUS_REVIEW_REQUIRED

    return raw_key, efs_id, status
