import React from 'react'
import { useSurveillance } from '../context/SurveillanceContext'

/** Maps connection status values to display config. */
const STATUS_CONFIG = {
  connected:    { label: 'Connected',    dot: 'bg-success',               text: 'text-success' },
  connecting:   { label: 'Connecting…',  dot: 'bg-warn animate-pulse',    text: 'text-warn' },
  disconnected: { label: 'Disconnected', dot: 'bg-slate-500',             text: 'text-slate-400' },
  error:        { label: 'Error',        dot: 'bg-alert',                 text: 'text-alert' },
}

export default function ConnectionStatus() {
  const { state } = useSurveillance()
  const cfg = STATUS_CONFIG[state.connectionStatus] ?? STATUS_CONFIG.disconnected

  return (
    <div className="flex items-center gap-2" role="status" aria-label={`Connection: ${cfg.label}`}>
      <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${cfg.dot}`} />
      <span className={`text-sm font-medium ${cfg.text}`}>{cfg.label}</span>
    </div>
  )
}
