export interface Vertical {
  name: string
  icon: string
  msp_fit: number
  reason: string
}

export interface VerticalsResponse {
  sectors: string[]
  verticals: Record<string, Vertical[]>
  total: number
}

export interface VerticalRecommendation {
  name: string
  icon: string
  sector: string
  msp_fit: number
  reason: string
  local_count: number
  local_score: number
  density_label: string
}

export interface RecommendationsResponse {
  location: string
  recommendations: VerticalRecommendation[]
  has_api_key: boolean
  message: string | null
}
