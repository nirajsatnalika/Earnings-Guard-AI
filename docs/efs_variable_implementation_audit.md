# EFS™ Variable Implementation Audit Report

**Framework**: Earnings Forensics Score (EFS™) v1.0  
**Audit Method**: Direct Code-Inspection of `variable_engine.py` and `tests/`  
**Status**: Completed  
**Date**: August 10, 2026  

---

## 1. Summary Statistics

| Metric | Count | Description |
| :--- | :--- | :--- |
| **Total Variables Audited** | **95** | Full universe of frozen EFS v1.0 variables across 7 pillars. |
| **IMPLEMENTED** | **11** | Actual formula calculation exists in `_compute_formula_fallback` AND inputs defined AND tested in `tests/`. |
| **PARTIAL** | **57** | Parameter resolution exists via `_resolve_variable_value` lookup, but standalone statement arithmetic fallback is not coded. |
| **SOURCE_DATA_REQUIRED** | **10** | Multi-year CAGR or growth trend formula requiring multi-period historical financial statement series. |
| **DISCLOSURE_REQUIRED** | **17** | Qualitative / footnote / governance evidence requiring disclosure inputs rather than pure P&L/BS arithmetic. |
| **NOT_IMPLEMENTED** | **0** | No evaluation or resolution path exists in engine code. |
| **Tested Implementation Count** | **12** | Variables with explicit test assertions in `tests/`. |
| **Untested Implementation Count** | **83** | Variables evaluated dynamically via config parameters without standalone test assertions. |

---

## 2. Fully Implemented & Tested Variables (11)

These variables have explicit mathematical formula fallback logic coded in `VariableCalculationEngine._compute_formula_fallback` and are verified by unit tests in `tests/test_variable_coverage.py`:

| Variable ID | Variable Name | Pillar | Formula | Test Reference |
| :--- | :--- | :--- | :--- | :--- |
| `AQ01` | Total Accruals | Accrual & Accounting Quality | `PAT − CFO` | `tests/test_variable_coverage.py` |
| `BSI02` | AQI | Balance Sheet Integrity | `Beneish Asset Quality Index` | `tests/test_variable_coverage.py, tests/test_model_verification.py` |
| `CFI01` | CFO / PAT | Cash Flow Integrity | `CFO / PAT` | `tests/test_variable_coverage.py` |
| `FSQ01` | Revenue Growth | Financial Statement Quality | `YoY Revenue Growth` | `tests/test_efs_engine.py, tests/test_variable_coverage.py, tests/test_rule_engine_edge_cases.py` |
| `FSQ02` | Receivables Growth vs Revenue Growth | Financial Statement Quality | `AR growth − Revenue growth` | `tests/test_variable_coverage.py, tests/test_rule_engine_edge_cases.py` |
| `FSQ03` | DSRI | Financial Statement Quality | `Beneish Days Sales in Receivables Index` | `tests/test_efs_engine.py, tests/test_variable_coverage.py, tests/test_model_verification.py, tests/test_rule_engine_edge_cases.py` |
| `FSQ04` | Revenue Quality Ratio | Financial Statement Quality | `CFO / Revenue` | `tests/test_variable_coverage.py, tests/test_rule_engine_edge_cases.py` |
| `WCH01` | DSO | Working Capital Forensics | `Average AR / Revenue × 365` | `tests/test_variable_coverage.py, tests/test_rule_engine_edge_cases.py` |
| `WCH04` | Inventory Days | Working Capital Forensics | `Average Inventory / COGS × 365` | `tests/test_variable_coverage.py` |
| `WCH07` | DPO | Working Capital Forensics | `Average AP / COGS × 365` | `tests/test_variable_coverage.py` |
| `WCH10` | Operating WC / Revenue | Working Capital Forensics | `Operating WC / Revenue` | `tests/test_variable_coverage.py` |

---

## 3. Variables Requiring Historical Source Data (10)

These variables represent multi-year CAGR or multi-period trend metrics (`GS01`–`GS10`). They require a multi-year historical financial statement series input:

| Variable ID | Variable Name | Pillar | Methodology Formula | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `GS01` | Revenue CAGR | Earnings Sustainability & Growth Quality | `Multi-year revenue CAGR` | Multi-year CAGR or growth trend formula requires multi-period historical financial statement series. |
| `GS02` | PAT CAGR | Earnings Sustainability & Growth Quality | `Multi-year PAT CAGR` | Multi-year CAGR or growth trend formula requires multi-period historical financial statement series. |
| `GS03` | EBITDA CAGR | Earnings Sustainability & Growth Quality | `Multi-year EBITDA CAGR` | Multi-year CAGR or growth trend formula requires multi-period historical financial statement series. |
| `GS04` | Revenue Growth vs CFO Growth | Earnings Sustainability & Growth Quality | `Revenue growth − CFO growth` | Multi-year CAGR or growth trend formula requires multi-period historical financial statement series. |
| `GS05` | Revenue Growth vs WC Growth | Earnings Sustainability & Growth Quality | `Revenue growth − WC growth` | Multi-year CAGR or growth trend formula requires multi-period historical financial statement series. |
| `GS06` | Margin Sustainability | Earnings Sustainability & Growth Quality | `Multi-year margin trend/volatility` | Multi-year CAGR or growth trend formula requires multi-period historical financial statement series. |
| `GS07` | ROIC / ROCE Trend | Earnings Sustainability & Growth Quality | `Multi-year operating return trend` | Multi-year CAGR or growth trend formula requires multi-period historical financial statement series. |
| `GS08` | Earnings Persistence | Earnings Sustainability & Growth Quality | `Persistence of recurring operating earnings` | Multi-year CAGR or growth trend formula requires multi-period historical financial statement series. |
| `GS09` | Growth Funding Gap | Earnings Sustainability & Growth Quality | `Growth cash needs vs CFO/FCF` | Multi-year CAGR or growth trend formula requires multi-period historical financial statement series. |
| `GS10` | Organic vs Acquired Growth | Earnings Sustainability & Growth Quality | `Organic vs total growth` | Multi-year CAGR or growth trend formula requires multi-period historical financial statement series. |

---

## 4. Variables Requiring Note / Footnote Disclosures (17)

These variables represent qualitative governance, auditor, or footnote disclosure evidence (`GD01`–`GD10`, `FSQ13`–`FSQ15`, `WCH12`–`WCH15`). They require footnote parser outputs or manual user input:

| Variable ID | Variable Name | Pillar | Methodology Formula | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `FSQ13` | Revenue Concentration | Financial Statement Quality | `Top customer revenue / Total revenue` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `FSQ14` | Contract Liabilities / Revenue | Financial Statement Quality | `Contract liabilities / Revenue` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `FSQ15` | Deferred Revenue Change | Financial Statement Quality | `YoY deferred revenue change` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `GD01` | Qualified Audit Opinion | Governance, Disclosure & External Evidence | `Auditor opinion indicator` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `GD02` | Key Audit Matter Severity | Governance, Disclosure & External Evidence | `Revenue/estimate/impairment KAM assessment` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `GD03` | Auditor Change | Governance, Disclosure & External Evidence | `Auditor change + stated reason` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `GD04` | Audit Tenure / Rotation Anomaly | Governance, Disclosure & External Evidence | `Tenure/rotation indicator` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `GD05` | Related Party Transactions / Revenue | Governance, Disclosure & External Evidence | `Material RPTs / Revenue` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `GD06` | Promoter / Insider Pledge | Governance, Disclosure & External Evidence | `Pledged shares / Holdings` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `GD07` | Accounting Policy Change | Governance, Disclosure & External Evidence | `Material policy-change indicator` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `GD08` | Restatement / Prior Period Adjustments | Governance, Disclosure & External Evidence | `Count + materiality` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `GD09` | Regulatory / Enforcement Action | Governance, Disclosure & External Evidence | `Reporting-related enforcement indicator` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `GD10` | Litigation / Accounting Contingency Exposure | Governance, Disclosure & External Evidence | `Relevant litigation / Equity` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `WCH12` | Receivable Concentration Risk | Working Capital Forensics | `Major customer/receivable concentration` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `WCH13` | Inventory Provision Coverage | Working Capital Forensics | `Inventory provision / Gross inventory` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `WCH14` | Contract Asset / Revenue | Working Capital Forensics | `Contract assets / Revenue` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |
| `WCH15` | Supplier Financing Indicators | Working Capital Forensics | `Supplier-finance liabilities / Payables` | Requires qualitative, footnote, or governance disclosure evidence rather than pure single-period statement arithmetic. |

---

## 5. Partial & Incomplete Implementation Inventory (57)

These quantitative variables are resolved when pre-computed ratio or raw variable inputs are provided to `VariableCalculationEngine._resolve_variable_value`, but do not have standalone multi-period arithmetic fallbacks in code:

| Variable ID | Variable Name | Pillar | Source Fields Required | Status |
| :--- | :--- | :--- | :--- | :--- |
| `AQ02` | Total Accruals / Average Assets | Accrual & Accounting Quality | `aq02, total_accruals__per__average_assets` | `PARTIAL` |
| `AQ03` | Sloan Accrual Ratio | Accrual & Accounting Quality | `aq03, sloan_accrual_ratio` | `PARTIAL` |
| `AQ04` | Working Capital Accruals / Assets | Accrual & Accounting Quality | `aq04, working_capital_accruals__per__assets` | `PARTIAL` |
| `AQ05` | Non-Cash Earnings Ratio | Accrual & Accounting Quality | `aq05, non_cash_earnings_ratio` | `PARTIAL` |
| `AQ06` | Accrual Trend | Accrual & Accounting Quality | `aq06, accrual_trend` | `PARTIAL` |
| `AQ07` | Accrual Volatility | Accrual & Accounting Quality | `aq07, accrual_volatility` | `PARTIAL` |
| `AQ08` | Change in Net Operating Assets | Accrual & Accounting Quality | `aq08, change_in_net_operating_assets` | `PARTIAL` |
| `AQ09` | Accruals vs Revenue Growth | Accrual & Accounting Quality | `aq09, accruals_vs_revenue_growth` | `PARTIAL` |
| `AQ10` | Accruals vs CFO Divergence | Accrual & Accounting Quality | `aq10, accruals_vs_cfo_divergence` | `PARTIAL` |
| `AQ11` | Depreciation / CapEx | Accrual & Accounting Quality | `aq11, depreciation__per__capex` | `PARTIAL` |
| `AQ12` | D&A / Gross PPE | Accrual & Accounting Quality | `aq12, danda__per__gross_ppe` | `PARTIAL` |
| `AQ13` | Deferred Tax Contribution to PAT | Accrual & Accounting Quality | `aq13, deferred_tax_contribution_to_pat` | `PARTIAL` |
| `AQ14` | Provision / Expense Ratio | Accrual & Accounting Quality | `aq14, provision__per__expense_ratio` | `PARTIAL` |
| `AQ15` | Reserve Reversal Contribution | Accrual & Accounting Quality | `aq15, reserve_reversal_contribution` | `PARTIAL` |
| `BSI01` | Asset Growth | Balance Sheet Integrity | `bsi01, asset_growth` | `PARTIAL` |
| `BSI03` | Intangibles / Assets | Balance Sheet Integrity | `bsi03, intangibles__per__assets` | `PARTIAL` |
| `BSI04` | Goodwill / Assets | Balance Sheet Integrity | `bsi04, goodwill__per__assets` | `PARTIAL` |
| `BSI05` | Capitalized Development Costs / Assets | Balance Sheet Integrity | `bsi05, capitalized_development_costs__per__assets` | `PARTIAL` |
| `BSI06` | Capitalized Software / Revenue | Balance Sheet Integrity | `bsi06, capitalized_software__per__revenue` | `PARTIAL` |
| `BSI07` | PPE Growth vs Revenue Growth | Balance Sheet Integrity | `bsi07, ppe_growth_vs_revenue_growth` | `PARTIAL` |
| `BSI08` | CapEx / Depreciation | Balance Sheet Integrity | `bsi08, capex__per__depreciation` | `PARTIAL` |
| `BSI09` | Debt Growth vs Asset Growth | Balance Sheet Integrity | `bsi09, debt_growth_vs_asset_growth` | `PARTIAL` |
| `BSI10` | Off-Balance-Sheet Exposure | Balance Sheet Integrity | `bsi10, off_balance_sheet_exposure` | `PARTIAL` |
| `BSI11` | Contingent Liabilities / Equity | Balance Sheet Integrity | `bsi11, contingent_liabilities__per__equity` | `PARTIAL` |
| `BSI12` | Lease Liabilities / Assets | Balance Sheet Integrity | `bsi12, lease_liabilities__per__assets` | `PARTIAL` |
| `BSI13` | Pension / Post-Employment Deficit | Balance Sheet Integrity | `bsi13, pension__per__post_employment_deficit` | `PARTIAL` |
| `BSI14` | Asset Impairment Reversals / PAT | Balance Sheet Integrity | `bsi14, asset_impairment_reversals__per__pat` | `PARTIAL` |
| `BSI15` | Asset-to-Revenue Divergence | Balance Sheet Integrity | `bsi15, asset_to_revenue_divergence` | `PARTIAL` |
| `CFI02` | CFO / EBITDA | Cash Flow Integrity | `cfi02, cfo__per__ebitda` | `PARTIAL` |
| `CFI03` | CFO Margin | Cash Flow Integrity | `cfi03, cfo_margin` | `PARTIAL` |
| `CFI04` | Free Cash Flow | Cash Flow Integrity | `cfi04, free_cash_flow` | `PARTIAL` |
| `CFI05` | FCF Margin | Cash Flow Integrity | `cfi05, fcf_margin` | `PARTIAL` |
| `CFI06` | CFO Growth vs PAT Growth | Cash Flow Integrity | `cfi06, cfo_growth_vs_pat_growth` | `PARTIAL` |
| `CFI07` | CFO Volatility | Cash Flow Integrity | `cfi07, cfo_volatility` | `PARTIAL` |
| `CFI08` | Cash Interest Coverage | Cash Flow Integrity | `cfi08, cash_interest_coverage` | `PARTIAL` |
| `CFI09` | Cash Tax / Tax Expense | Cash Flow Integrity | `cfi09, cash_tax__per__tax_expense` | `PARTIAL` |
| `CFI10` | CFO Less CapEx / PAT | Cash Flow Integrity | `cfi10, cfo_less_capex__per__pat` | `PARTIAL` |
| `CFI11` | Cash Conversion Trend | Cash Flow Integrity | `cfi11, cash_conversion_trend` | `PARTIAL` |
| `CFI12` | Working Capital Contribution to CFO | Cash Flow Integrity | `cfi12, working_capital_contribution_to_cfo` | `PARTIAL` |
| `CFI13` | Non-Cash Operating Items / CFO | Cash Flow Integrity | `cfi13, non_cash_operating_items__per__cfo` | `PARTIAL` |
| `CFI14` | CFO / EBITDA Trend | Cash Flow Integrity | `cfi14, cfo__per__ebitda_trend` | `PARTIAL` |
| `CFI15` | Investing Cash Flow Anomaly | Cash Flow Integrity | `cfi15, investing_cash_flow_anomaly` | `PARTIAL` |
| `FSQ05` | Gross Margin Change | Financial Statement Quality | `fsq05, gross_margin_change` | `PARTIAL` |
| `FSQ06` | Operating Margin Change | Financial Statement Quality | `fsq06, operating_margin_change` | `PARTIAL` |
| `FSQ07` | Net Margin Change | Financial Statement Quality | `fsq07, net_margin_change` | `PARTIAL` |
| `FSQ08` | Other Income / PAT | Financial Statement Quality | `fsq08, other_income__per__pat` | `PARTIAL` |
| `FSQ09` | Exceptional Items / PAT | Financial Statement Quality | `fsq09, exceptional_items__per__pat` | `PARTIAL` |
| `FSQ10` | Tax Rate Anomaly | Financial Statement Quality | `fsq10, tax_rate_anomaly` | `PARTIAL` |
| `FSQ11` | Earnings vs Revenue Divergence | Financial Statement Quality | `fsq11, earnings_vs_revenue_divergence` | `PARTIAL` |
| `FSQ12` | EPS vs PAT Divergence | Financial Statement Quality | `fsq12, eps_vs_pat_divergence` | `PARTIAL` |
| `WCH02` | DSO Change | Working Capital Forensics | `wch02, dso_change` | `PARTIAL` |
| `WCH03` | Receivables / Revenue | Working Capital Forensics | `wch03, receivables__per__revenue` | `PARTIAL` |
| `WCH05` | Inventory Growth vs Revenue Growth | Working Capital Forensics | `wch05, inventory_growth_vs_revenue_growth` | `PARTIAL` |
| `WCH06` | Inventory Turnover | Working Capital Forensics | `wch06, inventory_turnover` | `PARTIAL` |
| `WCH08` | Payables Growth vs COGS Growth | Working Capital Forensics | `wch08, payables_growth_vs_cogs_growth` | `PARTIAL` |
| `WCH09` | Cash Conversion Cycle | Working Capital Forensics | `wch09, cash_conversion_cycle` | `PARTIAL` |
| `WCH11` | WC Growth vs Revenue Growth | Working Capital Forensics | `wch11, wc_growth_vs_revenue_growth` | `PARTIAL` |

---

## 6. Genuinely Not Implemented Variables (0)

None (0). All 95 methodology variables have resolution paths in `variable_engine.py`.
