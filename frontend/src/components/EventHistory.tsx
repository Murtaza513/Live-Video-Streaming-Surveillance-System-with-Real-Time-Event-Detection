import { useSurveillance } from '../context/SurveillanceContext'

export function EventHistory() {
  const { events } = useSurveillance()

  return (
    <section className="rounded-2xl bg-panel p-4 shadow-lg">
      <h2 className="mb-4 text-lg font-semibold">Event History</h2>
      <div className="max-h-[360px] space-y-2 overflow-y-auto">
        {events.map((event) => (
          <div key={`${event.id}-${event.created_at}`} className="rounded-lg border border-slate-700 p-3">
            <p className="text-sm font-medium capitalize text-accent">{event.event_type}</p>
            <p className="text-xs text-slate-300">{event.message}</p>
            <p className="text-xs text-slate-500">{new Date(event.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
