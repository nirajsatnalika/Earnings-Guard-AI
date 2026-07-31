# EarningsGuard™ AI
## PROJECT_MASTER_PLAN.md

**Version:** 1.0

**Project Status:** In Development

**Target MVP:** 31 July 2026

---

# 1. Vision

## Product

EarningsGuard™ AI is an AI-powered financial forensics platform that evaluates the quality of reported earnings and detects possible accounting manipulation using proprietary forensic models.

The platform is designed for:

- Equity Investors
- Investment Analysts
- Fund Managers
- Auditors
- Credit Analysts
- Researchers
- Students

---

# 2. Mission

Enable investors to look beyond reported profits and assess the integrity of financial statements through explainable AI and forensic accounting.

---

# 3. Proprietary Framework

## EFS™

Earnings Forensics Score™

The EFS™ framework evaluates earnings quality using a multi-layer forensic methodology.

Current Version

EFS™ v1.0

---

# 4. Product Modules

Frontend

- Dashboard
- Analyze Company
- Results
- Compare Companies
- History
- Watchlist
- Reports
- Settings

Backend

- Upload API
- Parser Engine
- Mapping Engine
- Validation Engine
- Ratio Engine
- Beneish Engine
- EFS Engine
- AI Report Engine

---

# 5. Technology Stack

## Frontend

React 19

TypeScript

Material UI

React Router

Axios

Recharts

Framer Motion

---

## Backend

FastAPI

Python 3.13

SQLAlchemy

Pydantic v2

SQLite

OpenPyXL

Pandas

NumPy

---

## AI

Ollama

(Default)

Future

OpenAI

Anthropic

Gemini

---

## Reporting

ReportLab

Excel

PDF

---

## Version Control

Git

GitHub

---

# 6. Folder Structure

earningsguard-ai/

frontend/

backend/

docs/

methodology/

sample_data/

tests/

---

Backend

app/

api/

core/

database/

models/

schemas/

services/

calculations/

efs/

beneish/

ratios/

mapping/

validation/

ai/

reports/

utils/

---

# 7. Development Roadmap

## Sprint 1

React Foundation

Status

Completed

---

## Sprint 2

Analyze Company Workflow

Status

Completed

---

## Sprint 3

Backend Foundation

Status

Completed

---

## Sprint 4

Upload API

Excel Parser

Mapping Engine

Validation Engine

Status

In Progress

---

## Sprint 5

Financial Ratio Engine

Status

Pending

---

## Sprint 6

Beneish M-Score

Status

Pending

---

## Sprint 7

EFS™ Engine

Status

Pending

---

## Sprint 8

AI Report Generator

Status

Pending

---

## Sprint 9

Authentication

Deployment

Docker

Status

Pending

---

# 8. API Roadmap

GET /

GET /health

GET /version

POST /api/v1/upload

POST /api/v1/parse

POST /api/v1/map

POST /api/v1/validate

POST /api/v1/ratios

POST /api/v1/beneish

POST /api/v1/efs

POST /api/v1/report

GET /api/v1/history

POST /api/v1/compare

---

# 9. Analysis Workflow

User Uploads Files

↓

Upload API

↓

Excel Parser

↓

Field Mapping

↓

Validation

↓

Ratio Engine

↓

Beneish Engine

↓

EFS™

↓

AI Report

↓

PDF Report

---

# 10. Upload Requirements

Accepted

xlsx

xls

csv

Maximum Size

25 MB

Statements

Balance Sheet

Profit & Loss

Cash Flow

---

# 11. Mapping Engine

Purpose

Convert different accounting terminologies into a standardized financial dictionary.

Example

Revenue from Operations

↓

Revenue

Trade Debtors

↓

Receivables

Turnover

↓

Revenue

Target

300–500 aliases

---

# 12. Validation Engine

Checks

Mandatory Fields

Duplicate Fields

Missing Values

Data Type

Negative Values

Financial Statement Consistency

Output

Pass

Warning

Error

---

# 13. Ratio Engine

Liquidity

Profitability

Leverage

Efficiency

Cash Flow

Growth

Working Capital

Accrual

Market

Forensic

Target

100+ Ratios

---

# 14. Beneish Engine

Compute

DSRI

GMI

AQI

SGI

DEPI

SGAI

LVGI

TATA

Output

Beneish Score

Manipulation Risk

Explanation

---

# 15. EFS™

The proprietary Earnings Forensics Score.

Framework

7 Pillars

100+ Variables

Weighted Scores

Final Rating

AAA

AA

A

BBB

BB

B

CCC

---

# 16. AI Report

Executive Summary

Strengths

Weaknesses

Red Flags

Questions for Management

Investor Takeaway

Recommendations

---

# 17. Database

Tables

Users

Analysis

Uploads

Parsed Statements

Ratios

EFS Results

Reports

History

Watchlist

---

# 18. Coding Standards

Python

PEP8

Type Hints

Docstrings

React

Functional Components

Hooks

Reusable Components

No Duplicate Logic

---

# 19. Testing Strategy

Unit Tests

Integration Tests

API Tests

UI Tests

Regression Tests

---

# 20. Future Roadmap

Authentication

PostgreSQL

Docker

Cloud Deployment

Industry Models

Sector Benchmarks

Time-Series Analysis

Peer Comparison

REST API

Mobile Application

Browser Extension

Excel Add-in

---

# 21. Guiding Principles

1. Explainability over complexity.

2. Every score must be auditable.

3. Financial logic must be transparent.

4. AI supports analysis but does not replace methodology.

5. Build modular components.

6. Maintain enterprise-grade code quality.

7. Product decisions take precedence over convenience.

---

# 22. Definition of MVP

The MVP is complete when a user can:

- Upload financial statements.
- Automatically map fields.
- Validate data quality.
- Calculate financial ratios.
- Calculate Beneish M-Score.
- Calculate EFS™.
- Generate an AI forensic report.
- Export results as PDF.
- Review historical analyses.

---

# 23. Change Log

## Version 1.0

- React frontend established.
- FastAPI backend established.
- Project architecture frozen.
- EFS™ framework initiated.