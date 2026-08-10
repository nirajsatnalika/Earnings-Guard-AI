import { apiClient, extractApiError } from './client'
import type {
  AssessmentListItem,
  AssessmentListResponse,
  CompanyRecord,
  CompanyCreateRequest,
} from '../../types/efs'

export class AssessmentService {
  /**
   * List all persisted assessments (paginated), most recent first.
   */
  static async listAssessments(
    page: number = 1,
    limit: number = 50
  ): Promise<AssessmentListResponse> {
    try {
      const response = await apiClient.get<AssessmentListResponse>(
        `/api/v1/assessments?page=${page}&limit=${limit}`
      )
      return response.data
    } catch (error) {
      const message = extractApiError(error, 'Failed to load assessment history')
      throw new Error(message)
    }
  }

  /**
   * Get the full persisted assessment snapshot by assessment UUID.
   * Returns 404 if assessment not found or not completed.
   */
  static async getAssessmentById(assessmentId: string): Promise<Record<string, any>> {
    try {
      const response = await apiClient.get<Record<string, any>>(
        `/api/v1/assessments/${assessmentId}`
      )
      return response.data
    } catch (error) {
      const message = extractApiError(error, `Assessment '${assessmentId}' not found`)
      throw new Error(message)
    }
  }

  /**
   * Get all assessments for a specific company.
   */
  static async getCompanyAssessments(companyId: string): Promise<AssessmentListItem[]> {
    try {
      const response = await apiClient.get<AssessmentListItem[]>(
        `/api/v1/companies/${companyId}/assessments`
      )
      return response.data
    } catch (error) {
      const message = extractApiError(error, `Failed to load assessments for company ${companyId}`)
      throw new Error(message)
    }
  }
}

export class CompanyService {
  /**
   * Create a new company record.
   */
  static async createCompany(body: CompanyCreateRequest): Promise<CompanyRecord> {
    try {
      const response = await apiClient.post<CompanyRecord>('/api/v1/companies', body)
      return response.data
    } catch (error) {
      const message = extractApiError(error, 'Failed to create company')
      throw new Error(message)
    }
  }

  /**
   * List all companies.
   */
  static async listCompanies(): Promise<CompanyRecord[]> {
    try {
      const response = await apiClient.get<CompanyRecord[]>('/api/v1/companies')
      return response.data
    } catch (error) {
      const message = extractApiError(error, 'Failed to load companies')
      throw new Error(message)
    }
  }

  /**
   * Get a single company by ID.
   */
  static async getCompany(companyId: string): Promise<CompanyRecord> {
    try {
      const response = await apiClient.get<CompanyRecord>(`/api/v1/companies/${companyId}`)
      return response.data
    } catch (error) {
      const message = extractApiError(error, `Company '${companyId}' not found`)
      throw new Error(message)
    }
  }
}
