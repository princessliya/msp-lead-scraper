export interface ScrapeRequest {
  category: string
  location: string
  use_mock?: boolean
}

export interface ScrapeJob {
  id: number
  user_id: number
  category: string
  location: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  lead_count: number
  error_message: string | null
  created_at: string
  completed_at: string | null
}

export interface ScrapeEvent {
  type: 'started' | 'searching' | 'search_complete' | 'lead_processed' | 'completed' | 'failed' | 'cancelled'
  data: Record<string, unknown>
  timestamp: string
}
