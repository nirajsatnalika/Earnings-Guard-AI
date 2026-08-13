import { apiClient, extractApiError } from './client'

export interface CanonicalExtractedItem {
  id: string
  raw_label: string
  raw_value: string
  normalized_value: number | null
  unit: string | null
  currency: string | null
  period: string | null
  periods?: Record<string, number> | null
  evidence_category?: 'FINANCIAL_STATEMENT' | 'NOTE_DISCLOSURE' | 'GOVERNANCE_AUDITOR' | string | null
  evidence_text?: string | null
  source_filename: string
  source_page: number | null
  source_sheet: string | null
  source_section?: string | null
  canonical_field: string | null
  mapped_efs_variable: string | null
  raw_variable_key: string | null
  mapping_status: 'EXACT_MATCH' | 'HIGH_CONFIDENCE_MATCH' | 'REVIEW_REQUIRED' | 'UNMAPPED' | string
  confidence: number
  review_status: 'PENDING' | 'ACCEPTED' | 'EDITED' | 'REJECTED' | string
  notes: string | null
}

export interface IngestResponse {
  analysis_id: string
  status: string
  is_scanned_pdf: boolean
  scanned_pdf_message: string | null
  extracted_items: CanonicalExtractedItem[]
}

export interface ConfirmReviewResponse {
  analysis_id: string
  confirmed_raw_variables: Record<string, number>
}

export class IngestionService {
  static async processIngestion(analysisId: string): Promise<IngestResponse> {
    try {
      const { data } = await apiClient.post<IngestResponse>(`/api/v1/ingest/${analysisId}`)
      return data
    } catch (error) {
      throw new Error(extractApiError(error, 'Document ingestion failed. Please try again.'))
    }
  }

  static async confirmReview(
    analysisId: string,
    items: CanonicalExtractedItem[],
  ): Promise<ConfirmReviewResponse> {
    try {
      const { data } = await apiClient.post<ConfirmReviewResponse>(`/api/v1/ingest/${analysisId}/confirm`, {
        items,
      })
      return data
    } catch (error) {
      throw new Error(extractApiError(error, 'Failed to confirm review choices. Please try again.'))
    }
  }
}
