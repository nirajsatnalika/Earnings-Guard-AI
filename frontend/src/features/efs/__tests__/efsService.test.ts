import { describe, it, expect, vi, beforeEach } from 'vitest'
import { EFSService } from '../../../services/api/efsService'
import { apiClient } from '../../../services/api/client'
import type { EFSResponse } from '../../../types/efs'

vi.mock('../../../services/api/client', () => ({
  apiClient: {
    post: vi.fn(),
  },
  extractApiError: vi.fn((_err: unknown, fallback: string) => fallback),
}))

describe('EFSService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('1. API success: returns EFSResponse payload when API call succeeds', async () => {
    const mockResponse: Partial<EFSResponse> = {
      assessment_id: 'efs_asm_123',
      analysis_id: 'analysis_001',
      status: 'COMPLETED',
      overall: {
        score: null,
        score_status: 'CALIBRATION_PENDING',
        risk_level: null,
        confidence: 85.5,
      },
    }

    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockResponse })

    const result = await EFSService.getAssessment('analysis_001')
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/efs/analysis_001', {})
    expect(result.assessment_id).toBe('efs_asm_123')
    expect(result.overall.score_status).toBe('CALIBRATION_PENDING')
  })

  it('2. API failure: throws formatted error on network failure', async () => {
    vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Network connection error'))

    await expect(EFSService.getAssessment('invalid_id')).rejects.toThrow('Failed to load EFS assessment for analysis ID invalid_id')
  })
})
