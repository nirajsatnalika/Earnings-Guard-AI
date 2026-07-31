export interface CompanyComparison {
  id: string
  name: string
  shortName: string
  ticker: string
  score: number
  rating: string
  risk: 'Low' | 'Moderate' | 'High'
  health: 'Strong' | 'Stable' | 'Watch'
  confidence: number
  pillars: number[]
}

export const pillarNames = ['Financial Statement Quality', 'Cash Flow Integrity', 'Accrual Quality', 'Working Capital', 'Balance Sheet Integrity', 'Growth Sustainability', 'Governance']

export const companies: CompanyComparison[] = [
  { id: 'infosys', name: 'Infosys', shortName: 'Infosys', ticker: 'INFY', score: 84, rating: 'AA', risk: 'Low', health: 'Strong', confidence: 96, pillars: [91, 88, 82, 79, 86, 84, 90] },
  { id: 'tcs', name: 'TCS', shortName: 'TCS', ticker: 'TCS', score: 81, rating: 'AA', risk: 'Low', health: 'Strong', confidence: 94, pillars: [88, 92, 78, 76, 83, 81, 87] },
  { id: 'hcl', name: 'HCL Technologies', shortName: 'HCL', ticker: 'HCLTECH', score: 77, rating: 'A', risk: 'Moderate', health: 'Stable', confidence: 91, pillars: [80, 79, 69, 74, 78, 82, 81] },
  { id: 'wipro', name: 'Wipro', shortName: 'Wipro', ticker: 'WIPRO', score: 73, rating: 'A', risk: 'Moderate', health: 'Stable', confidence: 89, pillars: [76, 72, 75, 70, 76, 71, 78] },
  { id: 'tech-mahindra', name: 'Tech Mahindra', shortName: 'Tech Mahindra', ticker: 'TECHM', score: 69, rating: 'BBB', risk: 'Moderate', health: 'Watch', confidence: 86, pillars: [71, 67, 62, 68, 73, 69, 72] },
  { id: 'reliance', name: 'Reliance', shortName: 'Reliance', ticker: 'RELIANCE', score: 78, rating: 'A', risk: 'Low', health: 'Strong', confidence: 93, pillars: [83, 81, 76, 80, 75, 79, 82] },
  { id: 'hdfc', name: 'HDFC Bank', shortName: 'HDFC Bank', ticker: 'HDFCBANK', score: 86, rating: 'AA', risk: 'Low', health: 'Strong', confidence: 97, pillars: [94, 90, 85, 88, 89, 82, 92] },
  { id: 'icici', name: 'ICICI Bank', shortName: 'ICICI Bank', ticker: 'ICICIBANK', score: 83, rating: 'AA', risk: 'Low', health: 'Strong', confidence: 95, pillars: [90, 87, 83, 85, 86, 80, 89] },
]

export const defaultCompanyIds = ['infosys', 'tcs', 'hcl']
