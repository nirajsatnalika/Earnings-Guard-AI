"""Canonical EarningsGuard financial dictionary.

Each entry is a standard field that downstream engines (ratios, Beneish, EFS)
expect. This list is intentionally separate from the alias dictionary so the
canonical schema can evolve independently of how raw statements label things.
"""

CANONICAL_FIELDS: list[str] = [
    "Revenue",
    "Receivables",
    "Inventory",
    "Cash and Cash Equivalents",
    "Trade Payables",
    "Property Plant and Equipment",
    "Depreciation",
    "Gross Profit",
    "EBIT",
    "EBITDA",
    "Finance Cost",
    "Tax Expense",
    "PAT",
    "Operating Cash Flow",
    "Investing Cash Flow",
    "Financing Cash Flow",
    "Current Assets",
    "Current Liabilities",
    "Non Current Assets",
    "Equity",
    "Total Assets",
    "Total Liabilities",
]
