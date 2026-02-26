import api from './client'
import type { VerticalsResponse } from '../types/vertical'

export async function getVerticals(): Promise<VerticalsResponse> {
  const res = await api.get<VerticalsResponse>('/verticals/list')
  return res.data
}
