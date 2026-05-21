import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useReducer,
  useRef,
} from 'react'
import { fetchEvents } from '../services/api'
import { createWsClient } from '../services/wsClient'

// ---------------------------------------------------------------------------
// State shape
// ---------------------------------------------------------------------------

/** @type {SurveillanceState} */
const initialState = {
  /** 'connecting' | 'connected' | 'disconnected' | 'error' */
  connectionStatus: 'disconnected',

  /** base64 JPEG string of the latest frame */
  latestFrame: null,

  motionDetected: false,
  personDetected: false,
  motionRatio: 0,
  jpegQuality: 75,
  scale: 1.0,

  /** Most recent alert: { message, timestamp, type } — shown prominently */
  activeAlert: null,

  /** Rolling list of the last 50 live alerts (newest first) */
  alerts: [],

  /** Event records fetched from the REST API */
  events: [],
  eventsTotal: 0,
}

// ---------------------------------------------------------------------------
// Reducer
// ---------------------------------------------------------------------------

function reducer(state, action) {
  switch (action.type) {
    case 'SET_STATUS':
      return { ...state, connectionStatus: action.payload }

    case 'FRAME_RECEIVED': {
      const d = action.payload

      // Append to alert history when an alert message is present
      const updatedAlerts = d.alert
        ? [
            {
              message: d.alert,
              timestamp: d.timestamp,
              type: d.person_detected ? 'person' : 'motion',
            },
            ...state.alerts,
          ].slice(0, 50)
        : state.alerts

      return {
        ...state,
        latestFrame: d.frame || state.latestFrame,
        motionDetected: d.motion_detected,
        personDetected: d.person_detected,
        motionRatio: d.motion_ratio,
        jpegQuality: d.jpeg_quality,
        scale: d.scale,
        activeAlert: d.alert
          ? { message: d.alert, timestamp: d.timestamp }
          : state.activeAlert,
        alerts: updatedAlerts,
      }
    }

    case 'SET_EVENTS':
      return {
        ...state,
        events: action.payload.events,
        eventsTotal: action.payload.total,
      }

    default:
      return state
  }
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

const SurveillanceContext = createContext(null)

export function SurveillanceProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState)
  const wsRef = useRef(null)

  // Load initial event history from the backend REST API
  const loadEvents = useCallback(async () => {
    try {
      const data = await fetchEvents({ page: 1, pageSize: 50 })
      dispatch({ type: 'SET_EVENTS', payload: data })
    } catch (err) {
      console.error('[SurveillanceContext] Failed to load events:', err)
    }
  }, [])

  useEffect(() => {
    loadEvents()
  }, [loadEvents])

  // Establish WebSocket connection and handle lifecycle
  useEffect(() => {
    const wsUrl =
      import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/stream'

    dispatch({ type: 'SET_STATUS', payload: 'connecting' })

    wsRef.current = createWsClient({
      url: wsUrl,

      onOpen: () => dispatch({ type: 'SET_STATUS', payload: 'connected' }),

      onClose: () => dispatch({ type: 'SET_STATUS', payload: 'disconnected' }),

      onError: () => dispatch({ type: 'SET_STATUS', payload: 'error' }),

      onMessage: (data) => {
        // Ignore error-only payloads (camera unavailable)
        if (data.error) return

        dispatch({ type: 'FRAME_RECEIVED', payload: data })

        // Refresh event history shortly after an alert fires
        if (data.alert) {
          setTimeout(loadEvents, 1_200)
        }
      },
    })

    return () => {
      wsRef.current?.close()
    }
  }, [loadEvents])

  return (
    <SurveillanceContext.Provider value={{ state, loadEvents }}>
      {children}
    </SurveillanceContext.Provider>
  )
}

/** Hook for consuming surveillance state anywhere in the tree. */
export function useSurveillance() {
  const ctx = useContext(SurveillanceContext)
  if (!ctx) {
    throw new Error('useSurveillance must be used within a SurveillanceProvider')
  }
  return ctx
}
