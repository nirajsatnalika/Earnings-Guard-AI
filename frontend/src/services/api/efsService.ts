import { apiClient, extractApiError } from './client'
import type { EFSRequestPayload, EFSResponse, EFSNarrativeResponse } from '../../types/efs'

export class EFSService {
  /**
   * Fetches the complete EFS assessment for a given analysis ID.
   */
  static async getAssessment(
    analysisId: string,
    payload: EFSRequestPayload = {}
  ): Promise<EFSResponse> {
    try {
      const response = await apiClient.post<EFSResponse>(
        `/api/v1/efs/${analysisId}`,
        payload
      )
      return response.data
    } catch (error) {
      const message = extractApiError(error, `Failed to load EFS assessment for analysis ID ${analysisId}`)
      throw new Error(message)
    }
  }

  /**
   * Fetches the AI Forensic Narrative explanation for a given analysis ID.
   */
  static async getNarrative(analysisId: string): Promise<EFSNarrativeResponse> {
    try {
      const response = await apiClient.post<EFSNarrativeResponse>(
        `/api/v1/efs/${analysisId}/narrative`
      )
      return response.data
    } catch (error) {
      const message = extractApiError(error, `Failed to generate AI narrative for analysis ID ${analysisId}`)
      throw new Error(message)
    }
  }
}
