import { useSurveillance } from '../context/SurveillanceContext'

export function AlertPanel() {
  const { alerts } = useSurveillance()

  return (
    <section className="rounded-2xl bg-panel p-4 shadow-lg">
      <h2 className="mb-4 text-lg font-semibold">Real-Time Alerts</h2>
      <div className="space-y-3">
        {alerts.length === 0 && <p className="text-sm text-slate-400">No alerts yet</p>}
        {alerts.map((alert) => (
          <div key={alert.id} className="rounded-lg border border-danger/40 bg-danger/10 p-3">
            <p className="text-sm font-medium text-danger">{alert.event_type.toUpperCase()}</p>
            <p className="text-xs text-slate-300">{alert.message}</p>
            <p className="text-xs text-slate-400">{new Date(alert.created_at).toLocaleTimeString()}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
