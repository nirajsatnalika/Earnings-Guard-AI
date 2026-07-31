export interface Kpi { label: string; value: string; tone: 'primary' | 'success' | 'warning' | 'error' }
export interface Pillar { id: string; name: string; score: number; explanation: string }
export interface Ratio { ratio: string; value: string; benchmark: string; status: 'Strong' | 'Watch' | 'Neutral'; interpretation: string }
export interface RedFlag { indicator: string; severity: 'High' | 'Medium' | 'Low'; observation: string; recommendation: string; status: 'Open' | 'Reviewed' }
export interface StatementRow { label: string; current: string; previous: string; change: string }

export const kpis: Kpi[] = [
  { label: 'EFS™ Score', value: '84', tone: 'primary' }, { label: 'Rating', value: 'AA', tone: 'success' },
  { label: 'Manipulation Risk', value: 'LOW', tone: 'success' }, { label: 'Confidence Score', value: '96%', tone: 'primary' },
  { label: 'Red Flags', value: '3', tone: 'warning' }, { label: 'Financial Health', value: 'STRONG', tone: 'success' },
]
export const pillars: Pillar[] = [
  { id: 'statement-quality', name: 'Financial Statement Quality', score: 91, explanation: 'Clear, consistent reporting with strong disclosure depth.' },
  { id: 'cash-flow-integrity', name: 'Cash Flow Integrity', score: 88, explanation: 'Operating cash generation is well supported by earnings.' },
  { id: 'accrual-quality', name: 'Accrual Quality', score: 82, explanation: 'Accrual movements remain within a healthy historical range.' },
  { id: 'working-capital', name: 'Working Capital Health', score: 79, explanation: 'Receivables are controlled, with inventory worth monitoring.' },
  { id: 'balance-sheet', name: 'Balance Sheet Integrity', score: 86, explanation: 'Leverage and asset quality remain resilient.' },
  { id: 'growth-sustainability', name: 'Growth Sustainability', score: 84, explanation: 'Growth is diversified and supported by recurring demand.' },
  { id: 'governance', name: 'Governance & Disclosure', score: 90, explanation: 'Governance disclosures are timely and comprehensive.' },
]
export const ratios: Ratio[] = [
  { ratio: 'DSRI', value: '0.94x', benchmark: '< 1.00x', status: 'Strong', interpretation: 'Receivables are growing in line with revenue.' },
  { ratio: 'GMI', value: '0.98x', benchmark: '> 1.00x', status: 'Neutral', interpretation: 'Gross margins are broadly stable.' },
  { ratio: 'AQI', value: '1.06x', benchmark: '< 1.10x', status: 'Strong', interpretation: 'Asset quality remains consistent.' },
  { ratio: 'SGI', value: '1.14x', benchmark: '> 1.00x', status: 'Strong', interpretation: 'Revenue growth is healthy.' },
  { ratio: 'DEPI', value: '0.91x', benchmark: '< 1.00x', status: 'Strong', interpretation: 'Depreciation policy is not aggressive.' },
  { ratio: 'SGAI', value: '1.03x', benchmark: '< 1.00x', status: 'Watch', interpretation: 'Admin costs have grown slightly faster than sales.' },
  { ratio: 'LVGI', value: '0.89x', benchmark: '< 1.00x', status: 'Strong', interpretation: 'Leverage has decreased year over year.' },
  { ratio: 'TATA', value: '0.02', benchmark: '< 0.05', status: 'Strong', interpretation: 'Accrual intensity is low.' },
  { ratio: 'Sloan Ratio', value: '4.8%', benchmark: '< 8.0%', status: 'Strong', interpretation: 'Earnings quality is supported by cash flows.' },
  { ratio: 'Cash Conversion', value: '1.08x', benchmark: '> 1.00x', status: 'Strong', interpretation: 'Cash conversion exceeds reported profit.' },
  { ratio: 'Current Ratio', value: '2.14x', benchmark: '1.50–2.50x', status: 'Strong', interpretation: 'Short-term liquidity is comfortable.' },
  { ratio: 'Quick Ratio', value: '1.86x', benchmark: '> 1.00x', status: 'Strong', interpretation: 'Liquid assets cover current liabilities.' },
  { ratio: 'ROE', value: '31.2%', benchmark: '> 15.0%', status: 'Strong', interpretation: 'Capital is being deployed efficiently.' },
  { ratio: 'ROA', value: '19.4%', benchmark: '> 8.0%', status: 'Strong', interpretation: 'Asset productivity is above benchmark.' },
  { ratio: 'Gross Margin', value: '30.8%', benchmark: '> 25.0%', status: 'Strong', interpretation: 'Pricing power remains resilient.' },
  { ratio: 'Operating Margin', value: '25.1%', benchmark: '> 15.0%', status: 'Strong', interpretation: 'Operating discipline is robust.' },
]
export const redFlags: RedFlag[] = [
  { indicator: 'Inventory days', severity: 'Medium', observation: 'Inventory days increased 8% year over year.', recommendation: 'Review inventory ageing and provisioning policy.', status: 'Open' },
  { indicator: 'SG&A growth', severity: 'Low', observation: 'Operating expenses grew marginally ahead of sales.', recommendation: 'Monitor cost leverage over the next two quarters.', status: 'Reviewed' },
  { indicator: 'Receivables concentration', severity: 'Low', observation: 'Top five customers represent 24% of receivables.', recommendation: 'Track collection cycles by customer segment.', status: 'Reviewed' },
]
export const statements: Record<string, StatementRow[]> = {
  'Balance Sheet': [{ label: 'Total Assets', current: '₹ 1,46,812 Cr', previous: '₹ 1,32,736 Cr', change: '+10.6%' }, { label: 'Cash & Equivalents', current: '₹ 39,812 Cr', previous: '₹ 35,145 Cr', change: '+13.3%' }, { label: 'Total Debt', current: '₹ 7,214 Cr', previous: '₹ 8,116 Cr', change: '-11.1%' }, { label: 'Shareholders’ Equity', current: '₹ 1,01,270 Cr', previous: '₹ 89,475 Cr', change: '+13.2%' }],
  'Profit & Loss': [{ label: 'Revenue', current: '₹ 1,62,672 Cr', previous: '₹ 1,53,670 Cr', change: '+5.9%' }, { label: 'Operating Profit', current: '₹ 40,816 Cr', previous: '₹ 38,512 Cr', change: '+6.0%' }, { label: 'PAT', current: '₹ 26,248 Cr', previous: '₹ 24,095 Cr', change: '+8.9%' }, { label: 'EPS', current: '₹ 63.14', previous: '₹ 57.92', change: '+9.0%' }],
  'Cash Flow Statement': [{ label: 'Cash From Operations', current: '₹ 31,744 Cr', previous: '₹ 29,280 Cr', change: '+8.4%' }, { label: 'Capital Expenditure', current: '₹ 4,286 Cr', previous: '₹ 3,912 Cr', change: '+9.6%' }, { label: 'Free Cash Flow', current: '₹ 27,458 Cr', previous: '₹ 25,368 Cr', change: '+8.2%' }, { label: 'Cash From Investing', current: '₹ 2,114 Cr', previous: '₹ 4,891 Cr', change: '-56.8%' }],
}
