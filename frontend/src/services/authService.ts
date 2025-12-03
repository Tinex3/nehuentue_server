import api from './api'
import type { User, LoginResponse } from '@/types'

export const authService = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login', {
      username,
      password,
    })
    return response.data
  },

  async register(username: string, password: string, email?: string): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/register', {
      username,
      password,
      email,
    })
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  async updateUser(data: { email?: string; password?: string }): Promise<User> {
    const response = await api.put<{ user: User }>('/auth/me', data)
    return response.data.user
  },
}
