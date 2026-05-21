import React from 'react'
import { useSurveillance } from '../context/SurveillanceContext'

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return iso
  }
}

const ALERT_STYLES = {
  person: {
    wrapper: 'bg-red-900/40 border border-red-700',
    icon:    'text-alert',
    symbol:  '▲',
  },
  motion: {
    wrapper: 'bg-yellow-900/30 border border-yellow-700',
    icon:    'text-warn',
    symbol:  '◉',
  },
}

export default function AlertPanel() {
  const { state } = useSurveillance()
  const { alerts } = state

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-widest">
          Active Alerts
        </h2>
        {alerts.length > 0 && (
          <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-alert text-white text-xs font-bold">
            {Math.min(alerts.length, 9)}
          </span>
        )}
      </div>

      <div className="flex flex-col gap-2 max-h-72 overflow-y-auto pr-1">
        {alerts.length === 0 ? (
          <p className="text-slate-500 text-sm py-4 text-center">No alerts yet.</p>
        ) : (
          alerts.map((alert, idx) => {
            const style = ALERT_STYLES[alert.type] ?? ALERT_STYLES.motion
            return (
              <div key={idx} className={`flex items-start gap-3 p-3 rounded-lg ${style.wrapper}`}>
                <span className={`mt-0.5 text-base font-bold leading-none ${style.icon}`}>
                  {style.symbol}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white leading-snug">{alert.message}</p>
                  <p className="text-xs text-slate-400 mt-1">{formatTime(alert.timestamp)}</p>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
