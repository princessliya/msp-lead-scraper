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
