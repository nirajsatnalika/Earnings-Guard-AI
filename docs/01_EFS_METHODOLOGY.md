EFS™ v1.0 — Methodology

Product: EarningsGuard™ AIFramework: Earnings Forensics Score (EFS™)Version: 1.0Status: Frozen for v1.0 implementation

1. Purpose

EFS™ is a financial-forensics assessment framework designed to evaluate whether a company's reported financial performance and financial statements appear to faithfully represent its underlying economic reality.

The framework is specifically designed to identify:

potential aggressive accounting;

earnings-quality deterioration;

unusual revenue recognition patterns;

accrual-driven earnings;

weak earnings-to-cash conversion;

working-capital anomalies;

questionable asset quality or capitalization;

unsustainable reported growth;

governance, audit and disclosure red flags; and

patterns that warrant deeper forensic investigation.

Core question

How much confidence should we have that the company's reported earnings and financial statements faithfully represent its underlying economic reality?

EFS™ is a forensic screening and assessment framework. A high-risk result or triggered rule is not proof that fraud has occurred.

2. What EFS™ Is — and Is Not

EFS™ is

a structured financial-forensics assessment;

an explainable scoring framework;

a combination of financial-statement variables, established financial models and proprietary forensic rules;

designed to identify patterns requiring investigation;

evidence-driven and auditable.

EFS™ is not

a legal determination of fraud;

a probability-of-fraud model unless separately calibrated and explicitly labelled as such;

a stock recommendation;

a valuation model;

a generic credit rating;

a bankruptcy prediction model;

a replacement for audit;

a substitute for professional forensic investigation.

3. EFS™ v1.0 Architecture

EFS™ v1.0 contains exactly seven pillars.

#

Pillar

Core Question

1

Financial Statement Quality

Are reported revenues, expenses and earnings being presented faithfully?

2

Cash Flow Integrity

Are reported earnings converting into operating cash?

3

Accrual & Accounting Quality

How much of reported earnings depends on accruals, estimates and accounting judgments?

4

Working Capital Forensics

Are receivables, inventory and payables creating evidence of earnings-quality problems?

5

Balance Sheet Integrity

Are reported assets, liabilities and capitalized costs economically credible?

6

Earnings Sustainability & Growth Quality

Is reported growth supported by recurring economics, cash and sustainable operating performance?

7

Governance, Disclosure & External Evidence

Are audit, governance, regulatory and disclosure signals increasing forensic risk?

The seven pillars are frozen for EFS™ v1.0.

4. EFS™ Evidence Architecture

The EFS™ engine uses three principal evidence layers.

Layer 1 — Financial Variables

The v1.0 Variable Library contains 95 variables across the seven pillars.

The 95 variables are the proprietary EFS™ working variable universe.

They cover:

revenue quality;

earnings quality;

cash conversion;

accruals;

working capital;

asset quality;

growth sustainability; and

governance/disclosure evidence.

The authoritative variable definitions are maintained in:

02_EFS_VARIABLE_LIBRARY.xlsx

Layer 2 — Established Models

EFS™ v1.0 incorporates five established models/signals:

Beneish M-Score

Sloan Accrual Model

Altman Z-Score

Piotroski F-Score

Ohlson O-Score

These models are not simply added together.

Their role is determined by the EFS™ methodology:

Model

Primary Role

Beneish M-Score

Supporting forensic evidence

Sloan Accrual Model

Supporting accrual-quality evidence

Altman Z-Score

Cross-validation / distress context

Piotroski F-Score

Cross-validation / financial-quality context

Ohlson O-Score

Cross-validation / distress-default context

Important

A model result does not independently prove manipulation.

For example:

Altman Z-Score indicates financial distress context;

Piotroski indicates financial strength/quality context;

Ohlson indicates default/distress context.

These may increase or decrease confidence in the broader EFS interpretation, but they are not themselves fraud scores.

5. Beneish M-Score

Beneish M-Score is a foundational component of the EFS™ forensic framework because it specifically addresses patterns associated with earnings manipulation.

The relevant Beneish components include:

DSRI — Days Sales in Receivables Index

GMI — Gross Margin Index

AQI — Asset Quality Index

SGI — Sales Growth Index

DEPI — Depreciation Index

SGAI — Sales, General & Administrative Expense Index

LVGI — Leverage Index

TATA — Total Accruals to Total Assets

The overall Beneish M-Score must remain separately visible in the EFS™ Assessment.

The canonical Beneish interpretation must not be represented as a definitive fraud determination.

6. Sloan Accrual Model

The Sloan accrual model provides an established earnings-quality/accrual signal.

It is used to assess whether reported earnings contain a significant accrual component relative to cash-supported performance.

The exact operational definition and calculation must be frozen to the selected methodology/reference before production calibration.

Sloan should not be mechanically double-counted with all proprietary accrual variables.

7. Altman Z-Score

Altman Z-Score is included in EFS™ v1.0 as financial-distress context.

Its purpose within EFS™ is to help determine whether financial distress may be present alongside other forensic signals.

It is not treated as:

an accounting-fraud score;

a standalone EFS pillar;

a standalone EFS score.

Its output remains separately visible.

8. Piotroski F-Score

Piotroski F-Score is included as financial-quality / cross-validation evidence.

It can help determine whether a company's underlying financial condition corroborates or challenges the forensic assessment.

It is not treated as:

a fraud score;

a standalone EFS pillar;

nine additional EFS points.

Its component evidence may be used for interpretation and cross-validation.

9. Ohlson O-Score

Ohlson O-Score is included as distress/default cross-validation evidence.

It can provide additional context around financial distress and default risk.

It is not treated as:

a fraud score;

a standalone EFS pillar;

an independent EFS score that is simply added to other models.

10. Seven Pillars

Pillar 1 — Financial Statement Quality

Question

Are reported revenues, expenses and earnings being presented faithfully?

Key areas include:

revenue growth;

receivables relative to revenue;

DSRI;

revenue quality;

gross margin;

operating margin;

net margin;

other income;

exceptional items;

tax effects;

EPS/PAT divergence;

revenue concentration;

contract liabilities;

deferred revenue.

Pillar 2 — Cash Flow Integrity

Question

Are reported earnings actually converting into operating cash?

Key areas include:

CFO/PAT;

CFO/EBITDA;

CFO margin;

free cash flow;

FCF margin;

CFO growth vs PAT growth;

cash interest coverage;

cash tax;

cash conversion trend;

working-capital contribution to CFO;

non-cash operating items;

investing cash-flow anomalies.

Pillar 3 — Accrual & Accounting Quality

Question

How much of reported earnings depends on accruals, estimates and accounting judgments?

Key areas include:

total accruals;

accruals/assets;

Sloan accrual signal;

working-capital accruals;

non-cash earnings;

accrual trends;

accrual volatility;

net operating assets;

accrual vs revenue growth;

accrual vs CFO divergence;

depreciation;

deferred tax;

provisions;

reserve reversals.

Pillar 4 — Working Capital Forensics

Question

Are receivables, inventory and payables creating evidence of earnings-quality problems?

Key areas include:

DSO;

DSO change;

receivables/revenue;

inventory days;

inventory growth;

inventory turnover;

DPO;

payables growth;

cash conversion cycle;

operating working capital;

receivable concentration;

inventory provisions;

contract assets;

supplier financing.

Pillar 5 — Balance Sheet Integrity

Question

Are reported assets, liabilities and capitalized costs economically credible?

Key areas include:

asset growth;

AQI;

intangible assets;

goodwill;

capitalized development costs;

capitalized software;

PPE growth;

CapEx/depreciation;

debt growth;

off-balance-sheet exposure;

contingent liabilities;

lease liabilities;

pension obligations;

impairment reversals;

asset/revenue divergence.

Pillar 6 — Earnings Sustainability & Growth Quality

Question

Is reported growth supported by recurring economics, cash and sustainable operating performance?

Key areas include:

revenue CAGR;

PAT CAGR;

EBITDA CAGR;

revenue vs CFO growth;

revenue vs working-capital growth;

margin sustainability;

ROIC/ROCE trend;

earnings persistence;

growth funding gap;

organic vs acquired growth.

Pillar 7 — Governance, Disclosure & External Evidence

Question

Are audit, governance, regulatory and disclosure signals increasing forensic risk?

Key areas include:

qualified audit opinion;

Key Audit Matters;

auditor changes;

audit tenure/rotation;

related-party transactions;

promoter/insider pledging;

accounting policy changes;

restatements;

regulatory/enforcement actions;

accounting-related litigation/contingencies.

11. Scoring Philosophy

EFS™ uses a structured 0–100 scoring framework at the variable/pillar level.

The current scoring architecture uses:

0 — Critical / very adverse

25 — Weak

50 — Moderate

75 — Good

100 — Strong

These are assessment bands, not probabilities.

A score of 75 does not mean 75% probability of clean reporting.

A score of 25 does not mean 25% probability of fraud.

12. Weights

Final variable and pillar weights are intentionally not frozen until calibration.

The scoring engine must therefore support:

variable weights;

pillar weights;

model signals;

rule triggers.

But it must not invent weights merely to produce a number.

Until calibrated, the system must be able to return:

score_status = CALIBRATION_PENDING

rather than generating a false precision score.

13. Double-Counting Principle

A major methodological rule is:

Do not count the same economic signal multiple times merely because it appears in multiple formulas.

For example, receivable deterioration can appear through:

AR growth vs revenue growth;

DSRI;

DSO;

DSO change;

AR/revenue;

accrual measures.

These are useful corroborating signals, but the scoring engine must avoid blindly assigning full independent weight to every correlated variable.

Established models must also not simply be summed with their underlying component variables.

14. Variable Roles

Every variable/model signal is assigned a role.

Core Scoring

Directly contributes to the relevant pillar score after calibration.

Supporting Evidence

Displayed and used for corroboration and/or forensic rules, but may not independently receive additional weight where its information is already represented elsewhere.

Examples:

Beneish M-Score;

Sloan;

audit/disclosure evidence.

Rule-Only

Triggers a forensic finding but does not directly alter the numerical score.

Cross-Validation

Used to corroborate or challenge the EFS conclusion.

Examples:

Altman Z-Score;

Piotroski F-Score;

Ohlson O-Score.

15. Forensic Rule Engine

The EFS™ Rule Engine converts combinations of evidence into explainable forensic findings.

The rule flow is:

Evidence
   ↓
Rule Trigger
   ↓
Severity
   ↓
Forensic Finding
   ↓
Why It Matters
   ↓
Recommended Investigation
   ↓
Management Question

The authoritative rulebook is:

04_EFS_FORENSIC_RULEBOOK.xlsx

Rules can be:

single-variable;

model-based;

multi-variable;

cross-pillar;

corroborative.

16. Compound Forensic Rules

EFS™ should give greater importance to converging independent evidence than to isolated ratios.

Examples include:

Receivables + Revenue Divergence

Receivables growth materially exceeds revenue growth, combined with elevated DSRI and/or DSO deterioration.

Profit Growth Without Cash Support

PAT growth materially exceeds CFO growth while CFO/PAT remains weak or deteriorates.

Accrual-Driven Earnings Expansion

Accrual intensity rises while accrual growth exceeds revenue growth and CFO does not keep pace.

Inventory Build-Up + Weak Cash

Inventory growth exceeds revenue growth, inventory days deteriorate and earnings-to-cash conversion weakens.

Supplier-Financed Operating Cash

Payables growth materially exceeds COGS growth while CFO is significantly supported by working-capital movements.

Asset Quality Deterioration

AQI deteriorates alongside material intangible/goodwill exposure.

Growth Without Economic Support

Revenue grows faster than CFO/working capital while ROIC/ROCE deteriorates.

Beneish + Accrual Corroboration

Beneish manipulation-risk signal and accrual-quality indicators point in the same direction.

Distress + Reporting Risk

Distress signals coincide with qualified audit opinions or material restatement history.

Financial Quality vs Forensic Risk Divergence

Piotroski and Beneish produce materially different signals, requiring component-level investigation.

17. Severity

Forensic rules use severity levels.

Severity

Meaning

Critical

Multiple corroborating signals or high-value external evidence requiring immediate enhanced investigation

High

Material adverse signal requiring investigation

Medium

Meaningful anomaly that may be explainable

Low

Early warning or minor anomaly

Context

Model/context signal requiring interpretation rather than a direct fraud finding

Severity does not mean probability of fraud.

18. Evidence States

Every variable and rule should have an explicit evidence state.

State

Meaning

Triggered

Rule condition is satisfied

Not Triggered

Required data exists and condition is not satisfied

Not Evaluated

Required inputs are unavailable/invalid

Not Applicable

Rule does not apply to the company/business

Insufficient Evidence

Data exists but is inadequate for reliable assessment

Critical rule

Missing data must never automatically become a zero score or negative finding.

19. Confidence

Confidence is separate from the EFS risk assessment.

Confidence should reflect:

completeness of financial statements;

availability of variables;

validation quality;

source-data quality;

model availability;

rule-evaluation completeness;

mapping quality.

The system should return:

confidence score;

confidence level;

confidence factors;

limitations.

Confidence is not another fraud score.

20. Data Quality

The EFS™ engine must distinguish between:

missing;

unavailable;

not disclosed;

not applicable;

invalid;

insufficient evidence.

The system must preserve the reason a variable could not be evaluated.

This prevents data limitations from being misinterpreted as negative financial evidence.

21. Auditability

Every EFS™ assessment must preserve an audit trail.

Minimum metadata:

assessment_id;

analysis_id;

EFS methodology version;

scoring-rule version;

rulebook version;

engine version;

timestamp;

variables evaluated;

variables available;

rules evaluated;

rules triggered;

calculation time.

Every finding should be traceable back to the underlying financial data and calculation.

22. Deterministic Calculation Principle

The numerical EFS™ engine must be deterministic.

For the same:

company;

financial data;

methodology version;

scoring-rule version;

rulebook version;

the engine should produce the same calculation result.

AI must not:

calculate financial ratios;

determine variable scores;

decide whether a rule triggered;

alter severity;

invent evidence;

invent missing data.

AI may subsequently be used to explain already-computed evidence.

23. AI Layer

The intended architecture is:

Financial Data
      ↓
Validation
      ↓
Deterministic Calculations
      ↓
EFS Variables
      ↓
Established Models
      ↓
Scoring
      ↓
Forensic Rules
      ↓
Structured Evidence
      ↓
AI Explanation Layer

The AI explanation layer may generate:

executive summary;

explanation of key red flags;

explanation of pillar scores;

management questions;

investigation priorities;

plain-English interpretation.

It must be grounded exclusively in the deterministic evidence generated by the EFS engine.

24. Assessment Output

The final assessment should contain:

Assessment
│
├── Overall EFS Score
├── Score Status
├── Risk Level
├── Confidence
│
├── Seven Pillars
│   ├── Pillar Score
│   ├── Drivers
│   ├── Variables
│   └── Data Quality
│
├── Established Models
│   ├── Beneish M-Score
│   ├── Sloan Accrual Model
│   ├── Altman Z-Score
│   ├── Piotroski F-Score
│   └── Ohlson O-Score
│
├── Forensic Findings
├── Red Flags
├── Investigation Priorities
├── Management Questions
├── Limitations
└── Audit Trail

25. EFS™ Positioning

The intended product positioning is:

EFS™ is an explainable financial-forensics assessment that combines established earnings-quality models with a broader proprietary evidence framework to identify potential accounting manipulation, aggressive accounting, earnings-quality deterioration and financial reporting risk.

The product should position EFS™ as an enhanced forensic assessment, rather than merely another version of the Beneish M-Score.

26. Methodology Governance

The following are frozen for EFS™ v1.0:

seven pillars;

95-variable universe;

inclusion of Beneish;

inclusion of Sloan;

inclusion of Altman;

inclusion of Piotroski;

inclusion of Ohlson;

forensic rulebook approach;

evidence-state framework;

deterministic calculation principle;

separation of score from confidence;

no automatic fraud determination.

Changes should be versioned rather than silently modifying the v1.0 methodology.

27. Current EFS™ v1.0 Artifact Set

The methodology is implemented through four primary artifacts:

01_EFS_METHODOLOGY.md
02_EFS_VARIABLE_LIBRARY.xlsx
03_EFS_SCORING_RULES.xlsx
04_EFS_FORENSIC_RULEBOOK.xlsx

These artifacts together form the methodology source of truth for EFS™ v1.0.

Final North Star

EFS™ exists to answer one question:

Does the company's financial reporting appear economically credible, or does the evidence indicate elevated risk of aggressive accounting, earnings manipulation or financial-reporting quality problems that warrant forensic investigation?

EFS™ is a risk-identification and forensic-assessment framework — not a declaration of fraud.