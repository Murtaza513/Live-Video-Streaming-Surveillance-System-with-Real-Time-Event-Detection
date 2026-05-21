import React, { useState } from 'react'
import { useSurveillance } from '../context/SurveillanceContext'

function formatDatetime(iso) {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString([], { month: 'short', day: '2-digit' }) +
      ' ' +
      d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return iso
  }
}

const TYPE_BADGE = {
  person: 'bg-red-500/20 text-red-300 border border-red-700',
  motion: 'bg-yellow-500/20 text-yellow-300 border border-yellow-700',
}

const FILTERS = [
  { value: '',       label: 'All' },
  { value: 'motion', label: 'Motion' },
  { value: 'person', label: 'Person' },
]

export default function EventHistory() {
  const { state, loadEvents } = useSurveillance()
  const { events, eventsTotal } = state
  const [filter, setFilter] = useState('')

  const visible = filter ? events.filter((e) => e.event_type === filter) : events

  return (
    <div className="flex flex-col gap-4">
      {/* Header row */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-widest">
          Event Log
          <span className="ml-2 text-slate-500 font-normal normal-case">
            ({eventsTotal} total)
          </span>
        </h2>

        <div className="flex items-center gap-2">
          {/* Type filter buttons */}
          {FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={`px-2.5 py-1 text-xs rounded border transition-colors ${
                filter === f.value
                  ? 'bg-accent/20 border-accent text-accent'
                  : 'border-border text-slate-400 hover:border-slate-400 hover:text-slate-200'
              }`}
            >
              {f.label}
            </button>
          ))}

          {/* Refresh button */}
          <button
            onClick={loadEvents}
            title="Refresh event log"
            className="px-2.5 py-1 text-xs rounded border border-border text-slate-400 hover:border-slate-400 hover:text-slate-200 transition-colors"
          >
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="text-slate-500 border-b border-border text-xs uppercase tracking-wider">
              <th className="pb-2 pr-4 font-medium">Timestamp</th>
              <th className="pb-2 pr-4 font-medium">Type</th>
              <th className="pb-2 pr-4 font-medium">Confidence</th>
              <th className="pb-2 font-medium">Message</th>
            </tr>
          </thead>
          <tbody>
            {visible.length === 0 ? (
              <tr>
                <td colSpan={4} className="py-8 text-center text-slate-500 text-sm">
                  No events recorded yet.
                </td>
              </tr>
            ) : (
              visible.map((event) => (
                <tr
                  key={event.id}
                  className="border-b border-border/40 hover:bg-white/[0.03] transition-colors"
                >
                  <td className="py-2.5 pr-4 text-slate-300 whitespace-nowrap font-mono text-xs">
                    {formatDatetime(event.timestamp)}
                  </td>
                  <td className="py-2.5 pr-4">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        TYPE_BADGE[event.event_type] ?? 'bg-slate-700 text-slate-300'
                      }`}
                    >
                      {event.event_type}
                    </span>
                  </td>
                  <td className="py-2.5 pr-4 text-slate-300 font-mono text-xs">
                    {(event.confidence * 100).toFixed(0)}%
                  </td>
                  <td className="py-2.5 text-slate-400 text-xs max-w-sm truncate">
                    {event.message}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
