export interface Lead {
  id: number
  job_id: number
  business_name: string
  category: string
  address: string
  phone: string
  website: string
  domain: string
  rating: number
  reviews: number
  emails_found: string
  hunter_email: string
  hunter_name: string
  hunter_confidence: number
  apollo_email: string
  apollo_name: string
  apollo_title: string
  company_size: string
  industry: string
  tech_stack: string
  has_it_mention: boolean
  has_existing_msp: boolean
  compliance_mention: boolean
  ssl_valid: boolean
  score: number
  scrape_status: string
  notes: string
  is_archived: boolean
  created_at: string
}

export interface LeadsResponse {
  leads: Lead[]
  total: number
  page: number
  per_page: number
}

export interface LeadFilters {
  job_id?: number
  min_score?: number
  max_score?: number
  has_email?: boolean
  has_it_mention?: boolean
  category?: string
  search?: string
  sort_by?: string
  sort_dir?: string
  page?: number
  per_page?: number
}
