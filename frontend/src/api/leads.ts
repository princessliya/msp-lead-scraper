import api from './client'
import type { Lead, LeadFilters, LeadsResponse } from '../types/lead'

export async function getLeads(filters: LeadFilters = {}): Promise<LeadsResponse> {
  const res = await api.get<LeadsResponse>('/leads', { params: filters })
  return res.data
}

export async function getLead(id: number): Promise<Lead> {
  const res = await api.get<Lead>(`/leads/${id}`)
  return res.data
}

export async function updateLeadNotes(id: number, notes: string): Promise<Lead> {
  const res = await api.patch<Lead>(`/leads/${id}/notes`, { notes })
  return res.data
}

export async function deleteLead(id: number): Promise<void> {
  await api.delete(`/leads/${id}`)
}

export async function bulkDeleteLeads(leadIds: number[]): Promise<{ deleted_count: number }> {
  const res = await api.post<{ deleted_count: number }>('/leads/bulk-delete', { lead_ids: leadIds })
  return res.data
}
