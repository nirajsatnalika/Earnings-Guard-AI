"""Alias dictionary — maps raw statement labels to canonical fields.

This is a flat dict of {alias: canonical_field}. Kept separate from the
canonical dictionary so it can grow to thousands of aliases without touching
the core schema. Aliases are stored in their original casing; the matching
utility normalizes both sides before comparison.
"""

ALIASES: dict[str, str] = {
    # --- Revenue ---
    "Revenue from Operations": "Revenue",
    "Sales": "Revenue",
    "Net Sales": "Revenue",
    "Turnover": "Revenue",
    "Operating Revenue": "Revenue",
    "Total Revenue": "Revenue",
    "Gross Sales": "Revenue",
    "Revenue from Sale of Products": "Revenue",
    "Revenue from Sale of Services": "Revenue",
    "Other Operating Revenue": "Revenue",

    # --- Receivables ---
    "Trade Debtors": "Receivables",
    "Sundry Debtors": "Receivables",
    "Debtors": "Receivables",
    "Accounts Receivable": "Receivables",
    "Trade Receivables": "Receivables",
    "Bills Receivable": "Receivables",

    # --- Inventory ---
    "Stock": "Inventory",
    "Closing Stock": "Inventory",
    "Stock in Trade": "Inventory",
    "Inventory": "Inventory",
    "Raw Materials": "Inventory",
    "Work in Progress": "Inventory",
    "Finished Goods": "Inventory",
    "Stores and Spares": "Inventory",

    # --- Cash and Cash Equivalents ---
    "Cash": "Cash and Cash Equivalents",
    "Cash and Bank": "Cash and Cash Equivalents",
    "Bank Balance": "Cash and Cash Equivalents",
    "Cash Equivalents": "Cash and Cash Equivalents",
    "Cash at Bank": "Cash and Cash Equivalents",
    "Cash in Hand": "Cash and Cash Equivalents",

    # --- Trade Payables ---
    "Trade Creditors": "Trade Payables",
    "Sundry Creditors": "Trade Payables",
    "Accounts Payable": "Trade Payables",
    "Bills Payable": "Trade Payables",
    "Payables": "Trade Payables",

    # --- Property Plant and Equipment ---
    "Fixed Assets": "Property Plant and Equipment",
    "Net Fixed Assets": "Property Plant and Equipment",
    "Property Plant Equipment": "Property Plant and Equipment",
    "PPE": "Property Plant and Equipment",
    "Plant and Equipment": "Property Plant and Equipment",
    "Tangible Fixed Assets": "Property Plant and Equipment",
    "Gross Fixed Assets": "Property Plant and Equipment",

    # --- Depreciation ---
    "Depreciation and Amortisation": "Depreciation",
    "Depreciation and Amortization": "Depreciation",
    "Amortisation": "Depreciation",
    "Amortization": "Depreciation",
    "Accumulated Depreciation": "Depreciation",
    "Depreciation Expense": "Depreciation",

    # --- EBIT ---
    "Operating Profit": "EBIT",
    "Earnings Before Interest and Tax": "EBIT",
    "Operating Income": "EBIT",
    "Profit from Operations": "EBIT",

    # --- EBITDA ---
    "Earnings Before Interest Tax Depreciation and Amortisation": "EBITDA",
    "Earnings Before Interest Tax Depreciation and Amortization": "EBITDA",
    "Operating Profit Before Depreciation": "EBITDA",

    # --- Finance Cost ---
    "Interest Expense": "Finance Cost",
    "Finance Charges": "Finance Cost",
    "Borrowing Costs": "Finance Cost",
    "Interest Paid": "Finance Cost",

    # --- Tax Expense ---
    "Income Tax": "Tax Expense",
    "Tax on Profit": "Tax Expense",
    "Provision for Tax": "Tax Expense",
    "Current Tax": "Tax Expense",
    "Deferred Tax": "Tax Expense",
    "Tax Provision": "Tax Expense",

    # --- PAT ---
    "Profit After Tax": "PAT",
    "Net Profit": "PAT",
    "Net Income": "PAT",
    "Profit for the Year": "PAT",
    "Net Earnings": "PAT",
    "Bottom Line": "PAT",

    # --- Operating Cash Flow ---
    "Cash from Operations": "Operating Cash Flow",
    "CFO": "Operating Cash Flow",
    "Net Cash from Operating Activities": "Operating Cash Flow",
    "Cash Generated from Operations": "Operating Cash Flow",

    # --- Investing Cash Flow ---
    "Cash from Investing": "Investing Cash Flow",
    "CFI": "Investing Cash Flow",
    "Net Cash from Investing Activities": "Investing Cash Flow",
    "Cash Used in Investing": "Investing Cash Flow",

    # --- Financing Cash Flow ---
    "Cash from Financing": "Financing Cash Flow",
    "CFF": "Financing Cash Flow",
    "Net Cash from Financing Activities": "Financing Cash Flow",
    "Cash Used in Financing": "Financing Cash Flow",

    # --- Current Assets ---
    "Total Current Assets": "Current Assets",
    "Current Assets Total": "Current Assets",

    # --- Current Liabilities ---
    "Total Current Liabilities": "Current Liabilities",
    "Current Liabilities Total": "Current Liabilities",
    "Short Term Liabilities": "Current Liabilities",

    # --- Non Current Assets ---
    "Non Current Assets Total": "Non Current Assets",
    "Total Non Current Assets": "Non Current Assets",
    "Fixed and Intangible Assets": "Non Current Assets",

    # --- Equity ---
    "Shareholders Equity": "Equity",
    "Shareholders Funds": "Equity",
    "Stockholders Equity": "Equity",
    "Net Worth": "Equity",
    "Owners Equity": "Equity",
    "Total Equity": "Equity",

    # --- Total Assets ---
    "Total Asset": "Total Assets",
    "Assets Total": "Total Assets",

    # --- Total Liabilities ---
    "Total Liability": "Total Liabilities",
    "Liabilities Total": "Total Liabilities",
    "Total Outside Liabilities": "Total Liabilities",
}
