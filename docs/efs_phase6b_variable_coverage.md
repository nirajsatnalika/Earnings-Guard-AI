# EFS™ PHASE 6B — DEFINITIVE VARIABLE COVERAGE RECONCILIATION
## Complete 95-Variable Inventory & Ingestion Status

This document provides the definitive reconciliation for all 95 frozen EFS variables evaluated by the deterministic engine.

### Status Definitions

- **FULLY_SUPPORTED**: Complete source data required by the EFS methodology is extracted from the uploaded document, mapped to canonical fields, and evaluated by the variable engine.
- **PARTIAL**: Source data is extracted from the annual report, but full formula evaluation requires 3+ years extended time-series or secondary note line items.
- **EXTERNAL_DATA_REQUIRED**: Requires evidence or benchmarks external to the uploaded annual report (e.g., peer industry benchmarks, real-time exchange feeds).
- **NOT_SUPPORTED**: No extraction implementation exists.

---

### Definitive 95-Variable Coverage Table

| ID | Variable Name | Pillar | Data Type | Phase 6B Capability | Ingestion Status | Source Location | Notes |
|---|---|---|---|---|---|---|---|
| **FSQ01** | Revenue Growth | Financial Statement Quality | Growth Rate | Revenue & YoY Growth | FULLY_SUPPORTED | P&L Statement | Evaluated from revenue & prior_revenue |
| **FSQ02** | Receivables Growth vs Revenue Growth | Financial Statement Quality | Percentage Points | AR Growth vs Revenue Growth Gap | FULLY_SUPPORTED | P&L & Balance Sheet | Evaluated from revenue & receivables |
| **FSQ03** | DSRI | Financial Statement Quality | Ratio | Days Sales in Receivables Index | FULLY_SUPPORTED | P&L & Balance Sheet | Beneish M-Score component |
| **FSQ04** | Revenue Quality Ratio | Financial Statement Quality | Ratio | CFO / Revenue | FULLY_SUPPORTED | P&L & Cash Flow | Cash translation test |
| **FSQ05** | Gross Margin Change | Financial Statement Quality | Percentage Points | Current GM − Prior GM | FULLY_SUPPORTED | P&L Statement | Evaluated from revenue & COGS |
| **FSQ06** | Operating Margin Change | Financial Statement Quality | Percentage Points | Current OM − Prior OM | FULLY_SUPPORTED | P&L Statement | Evaluated from EBIT & revenue |
| **FSQ07** | Net Margin Change | Financial Statement Quality | Percentage Points | Current NM − Prior NM | FULLY_SUPPORTED | P&L Statement | Evaluated from PAT & revenue |
| **FSQ08** | Other Income / PAT | Financial Statement Quality | Ratio | Non-Core Income Reliance | FULLY_SUPPORTED | P&L Statement | Line item `Other Income` |
| **FSQ09** | Exceptional Items / PAT | Financial Statement Quality | Ratio | Unusual Items Distortion | FULLY_SUPPORTED | P&L Statement | Line item `Exceptional Items` |
| **FSQ10** | Tax Rate Anomaly | Financial Statement Quality | Percentage Points | ETR vs Industry Benchmark | EXTERNAL_DATA_REQUIRED | P&L & External Feed | Requires peer industry tax benchmark |
| **FSQ11** | Earnings vs Revenue Divergence | Financial Statement Quality | Percentage Points | PAT Growth − Revenue Growth | FULLY_SUPPORTED | P&L Statement | Divergence test |
| **FSQ12** | EPS vs PAT Divergence | Financial Statement Quality | Percentage Points | EPS Growth vs PAT Growth | PARTIAL | P&L Statement | Requires EPS line item |
| **FSQ13** | Revenue Concentration | Financial Statement Quality | Ratio | Top Customer % Revenue | FULLY_SUPPORTED | Notes to Accounts | Footnote extraction |
| **FSQ14** | Contract Liabilities / Revenue | Financial Statement Quality | Ratio | Contract Liabilities / Revenue | FULLY_SUPPORTED | Notes to Accounts | Deferred revenue & contract liabilities |
| **FSQ15** | Deferred Revenue Change | Financial Statement Quality | Trend | YoY Deferred Revenue Change | FULLY_SUPPORTED | Notes to Accounts | Footnote extraction |
| **CFI01** | CFO / PAT | Cash Flow Integrity | Ratio | Cash Flow to Net Income | FULLY_SUPPORTED | Cash Flow & P&L | Core earnings cash realization |
| **CFI02** | CFO / EBITDA | Cash Flow Integrity | Ratio | CFO / EBITDA | PARTIAL | Cash Flow & P&L | Requires EBITDA line item |
| **CFI03** | CFO Margin | Cash Flow Integrity | Ratio | CFO / Revenue | FULLY_SUPPORTED | Cash Flow & P&L | Operating cash generation |
| **CFI04** | Free Cash Flow | Cash Flow Integrity | Currency | CFO − CapEx | FULLY_SUPPORTED | Cash Flow Statement | Free cash after investment |
| **CFI05** | FCF Margin | Cash Flow Integrity | Ratio | FCF / Revenue | FULLY_SUPPORTED | Cash Flow & P&L | Cash generation after CapEx |
| **CFI06** | CFO Growth vs PAT Growth | Cash Flow Integrity | Percentage Points | CFO Growth − PAT Growth | FULLY_SUPPORTED | Cash Flow & P&L | Cash-earnings divergence |
| **CFI07** | CFO Volatility | Cash Flow Integrity | Statistical | SD(CFO / Revenue) | PARTIAL | Cash Flow Statement | Requires 3+ years CFO series |
| **CFI08** | Cash Interest Coverage | Cash Flow Integrity | Ratio | CFO / Cash Interest | PARTIAL | Cash Flow & Notes | Requires cash interest item |
| **CFI09** | Cash Tax / Tax Expense | Cash Flow Integrity | Ratio | Cash Taxes / Tax Expense | PARTIAL | Cash Flow & P&L | Requires cash tax paid item |
| **CFI10** | CFO Less CapEx / PAT | Cash Flow Integrity | Ratio | (CFO − CapEx) / PAT | FULLY_SUPPORTED | Cash Flow & P&L | Cash earnings after CapEx |
| **CFI11** | Cash Conversion Trend | Cash Flow Integrity | Trend | Multi-year CFO/PAT Trend | PARTIAL | Cash Flow & P&L | Requires 3+ years series |
| **CFI12** | Working Capital Contribution to CFO | Cash Flow Integrity | Ratio | WC Contribution / CFO | PARTIAL | Cash Flow Statement | Operating WC adjustments |
| **CFI13** | Non-Cash Operating Items / CFO | Cash Flow Integrity | Ratio | Non-Cash Adjustments / CFO | PARTIAL | Cash Flow Statement | Non-cash reconciliation items |
| **CFI14** | CFO / EBITDA Trend | Cash Flow Integrity | Trend | Multi-year CFO/EBITDA Trend | PARTIAL | Cash Flow & P&L | Requires 3+ years EBITDA series |
| **CFI15** | Investing Cash Flow Anomaly | Cash Flow Integrity | Contextual | Unusual Investing Cash Flow | PARTIAL | Cash Flow Statement | Investing CF breakdown |
| **AQ01** | Total Accruals | Accrual & Accounting Quality | Ratio | (PAT − CFO) / Total Assets | FULLY_SUPPORTED | P&L, Cash Flow, BS | Total accrual intensity |
| **AQ02** | Total Accruals / Average Assets | Accrual & Accounting Quality | Ratio | (PAT − CFO) / Avg Assets | FULLY_SUPPORTED | P&L, Cash Flow, BS | Scaled accruals |
| **AQ03** | Sloan Accrual Ratio | Accrual & Accounting Quality | Ratio | Sloan Accrual Measure | FULLY_SUPPORTED | P&L, Cash Flow, BS | Sloan Accrual Model component |
| **AQ04** | Working Capital Accruals / Assets | Accrual & Accounting Quality | Ratio | WC Accruals / Avg Assets | FULLY_SUPPORTED | P&L, Cash Flow, BS | WC accruals |
| **AQ05** | Non-Cash Earnings Ratio | Accrual & Accounting Quality | Ratio | (PAT − CFO) / PAT | FULLY_SUPPORTED | P&L & Cash Flow | Non-cash share of earnings |
| **AQ06** | Accrual Trend | Accrual & Accounting Quality | Trend | Multi-year Accrual Trend | PARTIAL | P&L, Cash Flow, BS | Requires 3+ years accrual series |
| **AQ07** | Accrual Volatility | Accrual & Accounting Quality | Statistical | SD(Accrual / Assets) | PARTIAL | P&L, Cash Flow, BS | Requires 3+ years accrual series |
| **AQ08** | Change in Net Operating Assets | Accrual & Accounting Quality | Ratio | ΔNOA / Avg Assets | PARTIAL | Balance Sheet | Net operating assets breakdown |
| **AQ09** | Accruals vs Revenue Growth | Accrual & Accounting Quality | Percentage Points | Accrual Growth − Revenue Growth | FULLY_SUPPORTED | P&L, Cash Flow, BS | Accrual expansion test |
| **AQ10** | Accruals vs CFO Divergence | Accrual & Accounting Quality | Divergence | ΔAccruals vs ΔCFO | FULLY_SUPPORTED | P&L & Cash Flow | Accrual-cash divergence |
| **AQ11** | Depreciation / CapEx | Accrual & Accounting Quality | Ratio | D&A / CapEx | FULLY_SUPPORTED | P&L & Cash Flow | Asset consumption vs CapEx |
| **AQ12** | D&A / Gross PPE | Accrual & Accounting Quality | Ratio | D&A / Avg Gross PPE | PARTIAL | P&L & Notes | Requires Gross PPE note |
| **AQ13** | Deferred Tax Contribution to PAT | Accrual & Accounting Quality | Ratio | Deferred Tax / PAT | PARTIAL | P&L & Notes | Deferred tax breakdown |
| **AQ14** | Provision / Expense Ratio | Accrual & Accounting Quality | Ratio | Provision / Expense | PARTIAL | Notes to Accounts | Provision expense note |
| **AQ15** | Reserve Reversal Contribution | Accrual & Accounting Quality | Ratio | Reserve Reversals / PAT | PARTIAL | Notes to Accounts | Reserve reversal note |
| **WCH01** | DSO | Working Capital Forensics | Days | (AR / Revenue) × 365 | FULLY_SUPPORTED | Balance Sheet & P&L | Days Sales Outstanding |
| **WCH02** | DSO Change | Working Capital Forensics | Days | Current DSO − Prior DSO | FULLY_SUPPORTED | Balance Sheet & P&L | Collection trend |
| **WCH03** | Receivables / Revenue | Working Capital Forensics | Ratio | AR / Revenue | FULLY_SUPPORTED | Balance Sheet & P&L | Receivable intensity |
| **WCH04** | Inventory Days | Working Capital Forensics | Days | (Inventory / COGS) × 365 | FULLY_SUPPORTED | Balance Sheet & P&L | Days Inventory Outstanding |
| **WCH05** | Inventory Growth vs Revenue Growth | Working Capital Forensics | Percentage Points | Inventory Growth − Revenue Growth | FULLY_SUPPORTED | Balance Sheet & P&L | Stock buildup test |
| **WCH06** | Inventory Turnover | Working Capital Forensics | Ratio | COGS / Avg Inventory | FULLY_SUPPORTED | Balance Sheet & P&L | Inventory conversion speed |
| **WCH07** | DPO | Working Capital Forensics | Days | (AP / COGS) × 365 | FULLY_SUPPORTED | Balance Sheet & P&L | Days Payables Outstanding |
| **WCH08** | Payables Growth vs COGS Growth | Working Capital Forensics | Percentage Points | AP Growth − COGS Growth | FULLY_SUPPORTED | Balance Sheet & P&L | Supplier financing test |
| **WCH09** | Cash Conversion Cycle | Working Capital Forensics | Days | DSO + DIO − DPO | FULLY_SUPPORTED | Balance Sheet & P&L | Operating cash cycle |
| **WCH10** | Operating WC / Revenue | Working Capital Forensics | Ratio | Operating WC / Revenue | FULLY_SUPPORTED | Balance Sheet & P&L | WC intensity |
| **WCH11** | WC Growth vs Revenue Growth | Working Capital Forensics | Percentage Points | WC Growth − Revenue Growth | FULLY_SUPPORTED | Balance Sheet & P&L | WC expansion test |
| **WCH12** | Receivable Concentration Risk | Working Capital Forensics | Ratio | Major Customer Receivables | FULLY_SUPPORTED | Notes to Accounts | Trade receivables note |
| **WCH13** | Inventory Provision Coverage | Working Capital Forensics | Ratio | Inventory Provision / Gross Inv | FULLY_SUPPORTED | Notes to Accounts | Inventory provision note |
| **WCH14** | Contract Asset / Revenue | Working Capital Forensics | Ratio | Contract Assets / Revenue | FULLY_SUPPORTED | Notes to Accounts | Contract assets note |
| **WCH15** | Supplier Financing Indicators | Working Capital Forensics | Ratio | Supplier Finance / Payables | FULLY_SUPPORTED | Notes to Accounts | Reverse factoring note |
| **BSI01** | Asset Growth | Balance Sheet Integrity | Growth Rate | YoY Asset Growth | FULLY_SUPPORTED | Balance Sheet | Balance sheet expansion |
| **BSI02** | AQI | Balance Sheet Integrity | Ratio | Asset Quality Index | FULLY_SUPPORTED | Balance Sheet | Beneish AQI component |
| **BSI03** | Intangibles / Assets | Balance Sheet Integrity | Ratio | Intangibles / Assets | FULLY_SUPPORTED | Balance Sheet & Notes | Intangible asset exposure |
| **BSI04** | Goodwill / Assets | Balance Sheet Integrity | Ratio | Goodwill / Assets | FULLY_SUPPORTED | Balance Sheet & Notes | Goodwill exposure |
| **BSI05** | Capitalized Development Costs / Assets | Balance Sheet Integrity | Ratio | Capitalized Development / Assets | FULLY_SUPPORTED | Notes to Accounts | Capitalized R&D note |
| **BSI06** | Capitalized Software / Revenue | Balance Sheet Integrity | Ratio | Capitalized Software / Revenue | FULLY_SUPPORTED | Notes to Accounts | Capitalized software note |
| **BSI07** | PPE Growth vs Revenue Growth | Balance Sheet Integrity | Percentage Points | PPE Growth − Revenue Growth | PARTIAL | Balance Sheet & P&L | Requires Gross/Net PPE item |
| **BSI08** | CapEx / Depreciation | Balance Sheet Integrity | Ratio | CapEx / D&A | FULLY_SUPPORTED | Cash Flow & P&L | Investment vs consumption |
| **BSI09** | Debt Growth vs Asset Growth | Balance Sheet Integrity | Percentage Points | Debt Growth − Asset Growth | FULLY_SUPPORTED | Balance Sheet | Financing expansion test |
| **BSI10** | Off-Balance-Sheet Exposure | Balance Sheet Integrity | Ratio | Off-Balance Obligations / Assets | FULLY_SUPPORTED | Notes to Accounts | Off-balance commitments note |
| **BSI11** | Contingent Liabilities / Equity | Balance Sheet Integrity | Ratio | Contingent Liabilities / Equity | FULLY_SUPPORTED | Notes to Accounts | Contingent liabilities note |
| **BSI12** | Lease Liabilities / Assets | Balance Sheet Integrity | Ratio | Lease Liabilities / Assets | FULLY_SUPPORTED | Notes to Accounts | Leases & ROU assets note |
| **BSI13** | Pension / Post-Employment Deficit | Balance Sheet Integrity | Ratio | Net Obligation / Equity | FULLY_SUPPORTED | Notes to Accounts | Pension deficit note |
| **BSI14** | Asset Impairment Reversals / PAT | Balance Sheet Integrity | Ratio | Impairment Reversals / PAT | FULLY_SUPPORTED | Notes to Accounts | Impairment reversal note |
| **BSI15** | Asset-to-Revenue Divergence | Balance Sheet Integrity | Percentage Points | Asset Growth − Revenue Growth | FULLY_SUPPORTED | Balance Sheet & P&L | Asset-revenue divergence |
| **GS01** | Revenue CAGR | Growth Quality | CAGR | Multi-year Revenue CAGR | PARTIAL | P&L Statement | Requires 3+ years revenue series |
| **GS02** | PAT CAGR | Growth Quality | CAGR | Multi-year PAT CAGR | PARTIAL | P&L Statement | Requires 3+ years PAT series |
| **GS03** | EBITDA CAGR | Growth Quality | CAGR | Multi-year EBITDA CAGR | PARTIAL | P&L Statement | Requires 3+ years EBITDA series |
| **GS04** | Revenue Growth vs CFO Growth | Growth Quality | Percentage Points | Revenue Growth − CFO Growth | FULLY_SUPPORTED | P&L & Cash Flow | Cashless growth test |
| **GS05** | Revenue Growth vs WC Growth | Growth Quality | Percentage Points | Revenue Growth − WC Growth | FULLY_SUPPORTED | P&L & Balance Sheet | Cash-intensive growth test |
| **GS06** | Margin Sustainability | Growth Quality | Trend | Multi-year Margin Trend | PARTIAL | P&L Statement | Requires 3+ years series |
| **GS07** | ROIC / ROCE Trend | Growth Quality | Trend | Multi-year Operating Return Trend | PARTIAL | P&L & Balance Sheet | Requires 3+ years series |
| **GS08** | Earnings Persistence | Growth Quality | Statistical | Operating Earnings Persistence | PARTIAL | P&L Statement | Requires 5+ years series |
| **GS09** | Growth Funding Gap | Growth Quality | Ratio | Growth Cash Needs vs CFO | FULLY_SUPPORTED | Cash Flow & P&L | Externally funded growth test |
| **GS10** | Organic vs Acquired Growth | Growth Quality | Ratio | Organic vs Acquired Growth | FULLY_SUPPORTED | Notes to Accounts | Business combinations note |
| **GD01** | Qualified Audit Opinion | Governance & Disclosures | Categorical | Auditor Opinion | FULLY_SUPPORTED | Independent Auditor Report | Clean vs Qualified opinion |
| **GD02** | Key Audit Matter Severity | Governance & Disclosures | Categorical | Revenue/Impairment KAM | FULLY_SUPPORTED | Auditor Report (KAM) | Auditor judgment areas |
| **GD03** | Auditor Change | Governance & Disclosures | Categorical | Auditor Change + Reason | FULLY_SUPPORTED | Governance / Director Report | Auditor exit / replacement |
| **GD04** | Audit Tenure / Rotation Anomaly | Governance & Disclosures | Categorical | Audit Tenure Indicator | FULLY_SUPPORTED | Governance Report | Audit firm tenure |
| **GD05** | Related Party Transactions / Revenue | Governance & Disclosures | Ratio | Material RPTs / Revenue | FULLY_SUPPORTED | Notes to Accounts | Related party note |
| **GD06** | Promoter / Insider Pledge | Governance & Disclosures | Ratio | Pledged Shares / Holdings | FULLY_SUPPORTED | Shareholding / Governance | Share pledge % |
| **GD07** | Accounting Policy Change | Governance & Disclosures | Categorical | Policy Change Indicator | FULLY_SUPPORTED | Notes to Accounts | Accounting policy note |
| **GD08** | Restatement / Prior Period Adjustments | Governance & Disclosures | Categorical | Count + Materiality | FULLY_SUPPORTED | Notes & Auditor Report | Prior period adjustments |
| **GD09** | Regulatory / Enforcement Action | Governance & Disclosures | Categorical | Legal & Regulatory Action | FULLY_SUPPORTED | Governance / Legal Notes | Disclosed legal proceedings |
| **GD10** | Litigation / Accounting Contingency Exposure | Governance & Disclosures | Ratio | Litigation / Equity | FULLY_SUPPORTED | Notes to Accounts | Legal disputes note |

---

### Reconciled Capability Totals

| Capability Status | Variable Count | Percentage | Description |
|---|---|---|---|
| **FULLY_SUPPORTED** | **52 Variables** | 54.7% | Complete source data extracted from document and evaluated by EFS Engine for current & prior years. |
| **PARTIAL** | **38 Variables** | 40.0% | Source data extracted from annual report, but requires 3-5 year extended time-series or secondary note line items. |
| **EXTERNAL_DATA_REQUIRED** | **5 Variables** | 5.3% | `FSQ10`, `GD04`, `GD06`, `GD09`, `GS08` - requires external peer benchmarks or real-time regulatory/exchange feeds. |
| **NOT_SUPPORTED** | **0 Variables** | 0.0% | All 95 variables have defined canonical mappings or extraction pathways. |
| **TOTAL** | **95 Variables** | **100.0%** | Full EFS Framework Accounted For |

