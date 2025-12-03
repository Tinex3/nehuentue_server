import api from './api'
import type { Device, DeviceType } from '@/types'

interface DevicesResponse {
  devices: Device[]
  total: number
}

interface DeviceTypesResponse {
  device_types: DeviceType[]
  total: number
}

export const devicesService = {
  async getAll(filters?: { zone_id?: number; device_type_id?: number; status?: boolean }): Promise<Device[]> {
    const response = await api.get<DevicesResponse>('/devices', { params: filters })
    return response.data.devices
  },

  async getById(id: number): Promise<Device> {
    const response = await api.get<Device>(`/devices/${id}`)
    return response.data
  },

  async create(data: {
    name: string
    description?: string
    device_type_id: number
    zone_id?: number
    params?: Record<string, unknown>
  }): Promise<Device> {
    const response = await api.post<{ device: Device }>('/devices', data)
    return response.data.device
  },

  async update(id: number, data: Partial<{
    name: string
    description: string
    device_type_id: number
    zone_id: number | null
    status: boolean
    params: Record<string, unknown>
  }>): Promise<Device> {
    const response = await api.put<{ device: Device }>(`/devices/${id}`, data)
    return response.data.device
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/devices/${id}`)
  },

  async sendCommand(id: number, command: string, payload?: Record<string, unknown>): Promise<void> {
    await api.post(`/devices/${id}/command`, { command, payload })
  },

  async getTypes(): Promise<DeviceType[]> {
    const response = await api.get<DeviceTypesResponse>('/device-types')
    return response.data.device_types
  },
}
