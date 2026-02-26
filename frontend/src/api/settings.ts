import api from './client'

export interface APIKeysStatus {
  serper_key_set: boolean
  serpapi_key_set: boolean
  hunter_key_set: boolean
  apollo_key_set: boolean
}

export interface APIKeysUpdate {
  serper_key?: string
  serpapi_key?: string
  hunter_key?: string
  apollo_key?: string
}

export async function getAPIKeys(): Promise<APIKeysStatus> {
  const res = await api.get<APIKeysStatus>('/settings/api-keys')
  return res.data
}

export async function updateAPIKeys(keys: APIKeysUpdate): Promise<void> {
  await api.put('/settings/api-keys', keys)
}

export async function getScoringWeights(): Promise<Record<string, number>> {
  const res = await api.get<Record<string, number>>('/settings/scoring-weights')
  return res.data
}

export async function updateScoringWeights(weights: Record<string, number>): Promise<void> {
  await api.put('/settings/scoring-weights', { weights })
}
