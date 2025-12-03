import api from './api'
import type { Event } from '@/types'

interface EventsResponse {
  events: Event[]
  total: number
  limit: number
  offset: number
}

interface EventStatsResponse {
  stats: Record<string, number>
  period_hours: number
}

export const eventsService = {
  async getAll(filters?: {
    zone_id?: number
    device_id?: number
    event_type?: string
    hours?: number
    limit?: number
    offset?: number
  }): Promise<EventsResponse> {
    const response = await api.get<EventsResponse>('/events', { params: filters })
    return response.data
  },

  async getById(id: number): Promise<Event> {
    const response = await api.get<Event>(`/events/${id}`)
    return response.data
  },

  async getStats(hours = 24): Promise<EventStatsResponse> {
    const response = await api.get<EventStatsResponse>('/events/stats', {
      params: { hours },
    })
    return response.data
  },
}
