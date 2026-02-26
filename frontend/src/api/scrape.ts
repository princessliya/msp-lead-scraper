import api from './client'
import type { ScrapeJob, ScrapeRequest } from '../types/scrape'

export async function startScrape(data: ScrapeRequest): Promise<ScrapeJob> {
  const res = await api.post<ScrapeJob>('/scrape/start', data)
  return res.data
}

export async function getScrapeStatus(jobId: number): Promise<ScrapeJob> {
  const res = await api.get<ScrapeJob>(`/scrape/${jobId}/status`)
  return res.data
}

export async function cancelScrape(jobId: number): Promise<void> {
  await api.post(`/scrape/${jobId}/cancel`)
}

export async function getScrapeHistory(page = 1, perPage = 20) {
  const res = await api.get<{ jobs: ScrapeJob[]; total: number }>('/scrape/history', {
    params: { page, per_page: perPage },
  })
  return res.data
}
