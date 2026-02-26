import api from './client'
import type { RecommendationsResponse, VerticalsResponse } from '../types/vertical'

export async function getVerticals(): Promise<VerticalsResponse> {
  const res = await api.get<VerticalsResponse>('/verticals/list')
  return res.data
}

export async function getRecommendations(location: string): Promise<RecommendationsResponse> {
  const res = await api.get<RecommendationsResponse>('/verticals/recommendations', {
    params: { location },
  })
  return res.data
}
