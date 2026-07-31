import type { FieldMapping } from './types'

export const industries = ['Technology', 'Financial Services', 'Healthcare', 'Consumer Goods', 'Industrials', 'Energy']
export const countries = ['United States', 'United Kingdom', 'India', 'Canada', 'Germany', 'Singapore']
export const financialYears = ['FY 2025–26', 'FY 2024–25', 'FY 2023–24', 'FY 2022–23']

export const standardFields = ['Revenue', 'Receivables', 'PAT', 'Inventory', 'Depreciation', 'CFO', 'Total Assets', 'Total Debt', 'Equity']

export const initialMappings: FieldMapping[] = [
  { detectedColumn: 'Revenue', standardField: 'Revenue' },
  { detectedColumn: 'Trade Receivables', standardField: 'Receivables' },
  { detectedColumn: 'Net Profit', standardField: 'PAT' },
  { detectedColumn: 'Inventory', standardField: 'Inventory' },
  { detectedColumn: 'Depreciation & Amortisation', standardField: 'Depreciation' },
  { detectedColumn: 'Net Cash from Operations', standardField: 'CFO' },
]

export const analysisChecklist = [
  'Reading Statements',
  'Mapping Fields',
  'Calculating Financial Ratios',
  'Computing EFS™',
  'Running AI Analysis',
  'Generating Report',
]
