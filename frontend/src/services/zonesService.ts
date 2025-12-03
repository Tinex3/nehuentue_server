import api from './api'
import type { Zone } from '@/types'

interface ZonesResponse {
  zones: Zone[]
  total: number
}

export const zonesService = {
  async getAll(): Promise<Zone[]> {
    const response = await api.get<ZonesResponse>('/zones')
    return response.data.zones
  },

  async getById(id: number, includeDevices = false): Promise<Zone> {
    const response = await api.get<Zone>(`/zones/${id}`, {
      params: { include_devices: includeDevices },
    })
    return response.data
  },

  async create(data: { name: string; description?: string }): Promise<Zone> {
    const response = await api.post<{ zone: Zone }>('/zones', data)
    return response.data.zone
  },

  async update(id: number, data: { name: string; description?: string }): Promise<Zone> {
    const response = await api.put<{ zone: Zone }>(`/zones/${id}`, data)
    return response.data.zone
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/zones/${id}`)
  },
}
