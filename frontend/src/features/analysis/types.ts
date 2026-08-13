export interface CompanyDetails {
  companyName: string
  stockSymbol: string
  industry: string
  country: string
  financialYear: string
}

export interface UploadedStatement {
  type: 'Balance Sheet' | 'Profit & Loss Statement' | 'Cash Flow Statement' | 'Annual Report' | 'Annual Report / Financial Statement'
  file: File | null
  progress: number
}

export interface FieldMapping {
  detectedColumn: string
  standardField: string
}

export type AnalysisStep = 0 | 1 | 2 | 3 | 4
