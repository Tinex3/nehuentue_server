import api from './api'
import type { Evidence } from '@/types'

interface EvidencesResponse {
  evidences: Evidence[]
  total: number
  limit: number
  offset: number
}

export const evidencesService = {
  async getAll(filters?: {
    zone_id?: number
    device_id?: number
    event_id?: number
    limit?: number
    offset?: number
  }): Promise<EvidencesResponse> {
    const response = await api.get<EvidencesResponse>('/evidences', { params: filters })
    return response.data
  },

  async getById(id: number): Promise<Evidence> {
    const response = await api.get<Evidence>(`/evidences/${id}`)
    return response.data
  },

  getFileUrl(id: number): string {
    return `/api/evidences/${id}/file`
  },

  async getAIResult(id: number): Promise<{ evidence_id: number; ai_metadata: unknown; processed: boolean }> {
    const response = await api.get(`/evidences/${id}/ai`)
    return response.data
  },
}
