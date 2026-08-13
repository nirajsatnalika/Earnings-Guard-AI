import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { HumanReviewTable } from '../components/HumanReviewTable'
import type { CanonicalExtractedItem } from '../../../services/api'

const sampleItems: CanonicalExtractedItem[] = [
  {
    id: '1',
    raw_label: 'Revenue from Operations',
    raw_value: '500000',
    normalized_value: 500000,
    unit: null,
    currency: 'INR',
    period: 'FY 2025',
    source_filename: 'infosys_annual_report.pdf',
    source_page: 14,
    source_sheet: null,
    canonical_field: 'Revenue',
    mapped_efs_variable: 'FSQ01',
    raw_variable_key: 'revenue',
    mapping_status: 'EXACT_MATCH',
    confidence: 100,
    review_status: 'PENDING',
    notes: null,
  },
  {
    id: '2',
    raw_label: 'Trade Receivables',
    raw_value: '80000',
    normalized_value: 80000,
    unit: null,
    currency: 'INR',
    period: 'FY 2025',
    source_filename: 'infosys_annual_report.pdf',
    source_page: 14,
    source_sheet: null,
    canonical_field: 'Receivables',
    mapped_efs_variable: 'FSQ02',
    raw_variable_key: 'accounts_receivable',
    mapping_status: 'HIGH_CONFIDENCE_MATCH',
    confidence: 95,
    review_status: 'PENDING',
    notes: null,
  },
]

describe('HumanReviewTable', () => {
  it('renders extracted document items and provenance metadata', () => {
    const onItemChange = vi.fn()
    render(<HumanReviewTable items={sampleItems} onItemChange={onItemChange} />)

    expect(screen.getByText('Revenue from Operations')).toBeInTheDocument()
    expect(screen.getByText('Trade Receivables')).toBeInTheDocument()
    expect(screen.getAllByText('Source: infosys_annual_report.pdf (Page 14)')[0]).toBeInTheDocument()
    expect(screen.getByText('FSQ01')).toBeInTheDocument()
    expect(screen.getByText('FSQ02')).toBeInTheDocument()
  })

  it('triggers item acceptance when accept button is clicked', () => {
    const onItemChange = vi.fn()
    render(<HumanReviewTable items={sampleItems} onItemChange={onItemChange} />)

    const acceptButtons = screen.getAllByTitle('Accept Item')
    fireEvent.click(acceptButtons[0])

    expect(onItemChange).toHaveBeenCalledWith([
      { ...sampleItems[0], review_status: 'ACCEPTED' },
      sampleItems[1],
    ])
  })

  it('accepts all high confidence matches on button click', () => {
    const onItemChange = vi.fn()
    render(<HumanReviewTable items={sampleItems} onItemChange={onItemChange} />)

    const acceptAllBtn = screen.getByText('Accept High Confidence Matches')
    fireEvent.click(acceptAllBtn)

    expect(onItemChange).toHaveBeenCalledWith([
      { ...sampleItems[0], review_status: 'ACCEPTED' },
      { ...sampleItems[1], review_status: 'ACCEPTED' },
    ])
  })
})
