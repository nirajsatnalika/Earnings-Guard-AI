import axios, { AxiosError, type AxiosInstance } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60_000,
  headers: { Accept: 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  config.metadata = { startTime: Date.now() }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status
    const url = error.config?.url ?? ''

    if (error.code === 'ECONNABORTED' || !error.response) {
      console.error(`[API] Network error reaching ${url}`)
    } else if (status && status >= 500) {
      console.error(`[API] Server error ${status} on ${url}`)
    } else if (status && status >= 400) {
      console.warn(`[API] Client error ${status} on ${url}`)
    }
    return Promise.reject(error)
  },
)

export interface ApiErrorResponse {
  detail?: string
  errors?: unknown[]
}

export function extractApiError(error: unknown, fallback = 'Something went wrong. Please try again.'): string {
  if (axios.isAxiosError<ApiErrorResponse>(error)) {
    if (error.response?.data?.detail) return String(error.response.data.detail)
    if (error.response?.data?.errors) return 'Request validation failed. Please review your inputs.'
    if (error.code === 'ECONNABORTED') return 'The request timed out. Please try again.'
    if (!error.response) return 'We could not reach the server. Check your connection and try again.'
  }
  if (error instanceof Error && error.message) return error.message
  return fallback
}
