import { EventRecord } from '../types'

const backendUrl = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000'

export const wsUrl = backendUrl.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws/stream'

export async function fetchEventHistory(limit = 50): Promise<EventRecord[]> {
  const response = await fetch(`${backendUrl}/api/events?limit=${limit}`)
  if (!response.ok) {
    throw new Error('Failed to load event history')
  }
  return response.json()
}
