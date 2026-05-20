export type StreamMessage = {
  type: 'frame' | 'error'
  timestamp?: string
  image?: string
  event_type?: 'motion' | 'person' | null
  confidence?: number
  motion_intensity?: number
  message?: string
}

export type EventRecord = {
  id: number
  event_type: string
  confidence: number
  message: string
  created_at: string
}
