// Tipos para el Sistema de Seguridad IoT

export interface User {
  user_id: number
  username: string
  email: string | null
  created_at: string
}

export interface Zone {
  zone_id: number
  user_id: number
  name: string
  description: string | null
  created_at: string
  device_count?: number
  devices?: Device[]
}

export interface DeviceType {
  device_type_id: number
  type_name: string
  description: string | null
  created_at: string
}

export interface Device {
  device_id: number
  name: string
  description: string | null
  device_type_id: number
  device_type: string | null
  zone_id: number | null
  zone_name: string | null
  user_id: number
  status: boolean
  params: Record<string, unknown>
  created_at: string
}

export interface Event {
  event_id: number
  device_id: number
  device_name: string | null
  zone_id: number | null
  zone_name: string | null
  event_type: string
  payload: Record<string, unknown> | null
  created_at: string
  evidence_count?: number
  evidences?: Evidence[]
}

export interface Evidence {
  evidence_id: number
  device_id: number | null
  zone_id: number | null
  event_id: number | null
  file_path: string
  ai_metadata: AIMetadata | null
  created_at: string
}

export interface AIMetadata {
  detections: Detection[]
  image_size: [number, number]
  persons_detected: number
  total_detections: number
  simulated?: boolean
}

export interface Detection {
  class: string
  class_id: number
  confidence: number
  bbox: [number, number, number, number]
}

export interface Measurement {
  measurement_id: number
  device_id: number
  device_name: string | null
  created_at: string
  recorded_at: string
  data: Record<string, number | string>
}

// API Response types
export interface LoginResponse {
  message: string
  user: User
  access_token: string
  refresh_token: string
}

export interface ApiError {
  error: string
  details?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
  total: number
  limit: number
  offset: number
  [key: string]: T[] | number
}
