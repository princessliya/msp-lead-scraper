import api from './client'
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/auth'

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>('/auth/login', data)
  return res.data
}

export async function register(data: RegisterRequest): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>('/auth/register', data)
  return res.data
}

export async function getMe(): Promise<User> {
  const res = await api.get<User>('/auth/me')
  return res.data
}

export async function refreshToken(token: string): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>('/auth/refresh', { refresh_token: token })
  return res.data
}
