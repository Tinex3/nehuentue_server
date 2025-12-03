import api from './api'
import type { Measurement } from '@/types'

interface MeasurementsResponse {
  measurements: Measurement[]
  total: number
  limit: number
  offset: number
  period_hours: number
}

interface DeviceMeasurementsResponse {
  device_id: number
  device_name: string
  measurements: Measurement[]
  total: number
  period_hours: number
}

interface MeasurementsSummary {
  summary: Array<{
    device_id: number
    device_name: string
    device_type: string | null
    measurement_count: number
    latest_data: Record<string, number | string> | null
    latest_recorded_at: string | null
  }>
  period_hours: number
}

export const measurementsService = {
  async getAll(filters?: {
    device_id?: number
    hours?: number
    limit?: number
    offset?: number
  }): Promise<MeasurementsResponse> {
    const response = await api.get<MeasurementsResponse>('/measurements', { params: filters })
    return response.data
  },

  async getByDevice(deviceId: number, hours = 24, limit = 100): Promise<DeviceMeasurementsResponse> {
    const response = await api.get<DeviceMeasurementsResponse>(
      `/measurements/device/${deviceId}`,
      { params: { hours, limit } }
    )
    return response.data
  },

  async getLatest(deviceId: number): Promise<{ device_id: number; device_name: string; measurement: Measurement | null }> {
    const response = await api.get(`/measurements/device/${deviceId}/latest`)
    return response.data
  },

  async getSummary(hours = 24): Promise<MeasurementsSummary> {
    const response = await api.get<MeasurementsSummary>('/measurements/summary', {
      params: { hours },
    })
    return response.data
  },
}
