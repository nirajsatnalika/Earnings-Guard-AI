import { apiClient, extractApiError } from './client'

export interface UploadedFileResult {
  statement: string
  filename: string
  size: string
  extension: string
}

export interface UploadResult {
  analysisId: string
  status: string
  uploadedFiles: UploadedFileResult[]
}

export interface StatementFile {
  statementType: string
  file: File
}

export interface UploadProgress {
  statementType: string
  progress: number
}

export class UploadService {
  static async uploadStatements(
    files: StatementFile[],
    onProgress?: (progress: UploadProgress) => void,
  signal?: AbortSignal,
  ): Promise<UploadResult> {
    const formData = new FormData()
    const fieldMap: Record<string, string> = {
      'Balance Sheet': 'balance_sheet',
      'Profit & Loss Statement': 'profit_loss',
      'Cash Flow Statement': 'cash_flow',
    }

    for (const { statementType, file } of files) {
      const fieldName = fieldMap[statementType]
      if (!fieldName) throw new Error(`Unsupported statement type: ${statementType}`)
      formData.append(fieldName, file)
    }

    try {
      const { data } = await apiClient.post('/api/v1/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        signal,
        onUploadProgress: (event) => {
          if (!onProgress || !event.total) return
          const progress = Math.round((event.loaded / event.total) * 100)
          files.forEach(({ statementType }) => onProgress({ statementType, progress }))
        },
      })
      return {
        analysisId: data.analysis_id,
        status: data.status,
        uploadedFiles: data.uploaded_files,
      }
    } catch (error) {
      throw new Error(extractApiError(error, 'Upload failed. Please try again.'))
    }
  }
}
