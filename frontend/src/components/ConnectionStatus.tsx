import { useSurveillance } from '../context/SurveillanceContext'

const statusClass: Record<string, string> = {
  connected: 'bg-green-500',
  connecting: 'bg-yellow-400',
  disconnected: 'bg-slate-500',
  error: 'bg-red-500',
}

export function ConnectionStatus() {
  const { connectionStatus } = useSurveillance()

  return (
    <div className="inline-flex items-center gap-2 rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-200">
      <span className={`h-2 w-2 rounded-full ${statusClass[connectionStatus]}`} />
      {connectionStatus}
    </div>
  )
}
