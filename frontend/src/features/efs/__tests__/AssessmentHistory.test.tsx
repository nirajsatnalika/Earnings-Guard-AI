import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material'
import { theme } from '../../../theme'
import { History } from '../../../pages/History'

// Mock the assessment service
vi.mock('../../../services/api/assessmentService', () => ({
  AssessmentService: {
    listAssessments: vi.fn(),
    getCompanyAssessments: vi.fn(),
  },
  CompanyService: {
    getCompany: vi.fn(),
    listCompanies: vi.fn(),
  },
}))

const { AssessmentService } = await import('../../../services/api/assessmentService')

const mockCalibrationItem = {
  id: 'asm-001',
  analysis_id: 'sample_analysis_001',
  company_id: 'co-001',
  assessment_status: 'COMPLETED' as const,
  score_status: 'CALIBRATION_PENDING' as const,
  overall_score: null,
  risk_level: null,
  confidence_score: 72.5,
  confidence_level: 'Medium',
  rules_triggered: 3,
  variables_evaluated: 95,
  efs_version: '1.0',
  methodology_version: '1.0',
  created_at: '2026-08-10T12:00:00Z',
  completed_at: '2026-08-10T12:00:05Z',
  input_snapshot_hash: 'abc123def456',
  assessment_snapshot_hash: 'xyz789uvw012',
}

const mockCompletedItem = {
  ...mockCalibrationItem,
  id: 'asm-002',
  analysis_id: 'other_analysis_002',
  score_status: 'COMPLETED' as const,
  overall_score: 78.5,
  risk_level: 'Moderate',
}

const renderHistory = () =>
  render(
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <History />
      </BrowserRouter>
    </ThemeProvider>
  )

describe('AssessmentHistory (History Page)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('1. renders loading state initially', () => {
    vi.mocked(AssessmentService.listAssessments).mockImplementation(
      () => new Promise(() => {})  // never resolves — keeps loading
    )
    renderHistory()
    expect(screen.getByRole('progressbar')).toBeTruthy()
  })

  it('2. renders calibration pending correctly (no score shown)', async () => {
    vi.mocked(AssessmentService.listAssessments).mockResolvedValue({
      items: [mockCalibrationItem],
      total: 1,
      page: 1,
      limit: 20,
    })
    renderHistory()
    await waitFor(() => {
      expect(screen.getByText('Calibration Pending')).toBeTruthy()
    })
    // Must NOT show a zero score
    expect(screen.queryByText('0')).toBeNull()
    expect(screen.queryByText('0.0')).toBeNull()
  })

  it('3. renders real score when completed', async () => {
    vi.mocked(AssessmentService.listAssessments).mockResolvedValue({
      items: [mockCompletedItem],
      total: 1,
      page: 1,
      limit: 20,
    })
    renderHistory()
    await waitFor(() => {
      expect(screen.getByText('78.5')).toBeTruthy()
    })
  })

  it('4. error state renders alert', async () => {
    vi.mocked(AssessmentService.listAssessments).mockRejectedValue(
      new Error('Network error')
    )
    renderHistory()
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeTruthy()
    })
  })

  it('5. empty state renders when no assessments', async () => {
    vi.mocked(AssessmentService.listAssessments).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      limit: 20,
    })
    renderHistory()
    await waitFor(() => {
      // Empty state renders when no items
      expect(screen.queryByRole('progressbar')).toBeNull()
    })
  })
})
