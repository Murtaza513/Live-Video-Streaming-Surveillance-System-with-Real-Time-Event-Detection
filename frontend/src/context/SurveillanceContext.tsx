import { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { EventRecord, StreamMessage } from '../types'
import { fetchEventHistory, wsUrl } from '../services/api'

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

type SurveillanceContextValue = {
  frameSrc: string | null
  alerts: EventRecord[]
  events: EventRecord[]
  connectionStatus: ConnectionStatus
  latestMotion: number
}

const SurveillanceContext = createContext<SurveillanceContextValue | undefined>(undefined)

export function SurveillanceProvider({ children }: { children: React.ReactNode }) {
  const [frameSrc, setFrameSrc] = useState<string | null>(null)
  const [alerts, setAlerts] = useState<EventRecord[]>([])
  const [events, setEvents] = useState<EventRecord[]>([])
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting')
  const [latestMotion, setLatestMotion] = useState(0)
  const nextId = useRef(0)

  const createTempId = () => {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID()
    }
    return `temp-${Date.now()}-${Math.random().toString(16).slice(2)}-${nextId.current++}`
  }

  useEffect(() => {
    let mounted = true
    fetchEventHistory()
      .then((data) => {
        if (mounted) {
          setEvents(data)
          setAlerts(data.filter((e) => e.event_type === 'motion' || e.event_type === 'person').slice(0, 10))
        }
      })
      .catch(() => undefined)
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    const socket = new WebSocket(wsUrl)
    setConnectionStatus('connecting')

    socket.onopen = () => setConnectionStatus('connected')
    socket.onclose = () => setConnectionStatus('disconnected')
    socket.onerror = () => setConnectionStatus('error')

    socket.onmessage = (event) => {
      const payload: StreamMessage = JSON.parse(event.data)
      if (payload.type === 'frame' && payload.image) {
        setFrameSrc(`data:image/jpeg;base64,${payload.image}`)
        setLatestMotion(payload.motion_intensity ?? 0)

        if (payload.event_type && payload.timestamp) {
          const item: EventRecord = {
            id: createTempId(),
            event_type: payload.event_type,
            confidence: payload.confidence ?? 0,
            message:
              payload.event_type === 'person'
                ? `Person detected with confidence ${(payload.confidence ?? 0).toFixed(2)}`
                : `Motion detected with intensity ${(payload.motion_intensity ?? 0).toFixed(2)}%`,
            created_at: payload.timestamp,
          }

          setAlerts((prev) => [item, ...prev].slice(0, 20))
          setEvents((prev) => [item, ...prev].slice(0, 100))
        }
      }
    }

    return () => {
      socket.close()
    }
  }, [])

  const value = useMemo(
    () => ({ frameSrc, alerts, events, connectionStatus, latestMotion }),
    [frameSrc, alerts, events, connectionStatus, latestMotion],
  )

  return <SurveillanceContext.Provider value={value}>{children}</SurveillanceContext.Provider>
}

export function useSurveillance() {
  const context = useContext(SurveillanceContext)
  if (!context) {
    throw new Error('useSurveillance must be used within SurveillanceProvider')
  }
  return context
}
