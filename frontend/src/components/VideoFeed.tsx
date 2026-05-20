import { useSurveillance } from '../context/SurveillanceContext'

export function VideoFeed() {
  const { frameSrc, latestMotion } = useSurveillance()

  return (
    <section className="rounded-2xl bg-panel p-4 shadow-lg">
      <h2 className="mb-4 text-lg font-semibold">Live Feed</h2>
      <div className="aspect-video w-full overflow-hidden rounded-xl bg-slate-800">
        {frameSrc ? (
          <img src={frameSrc} alt="Live surveillance" className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full items-center justify-center text-slate-400">Waiting for stream...</div>
        )}
      </div>
      <p className="mt-3 text-sm text-slate-300">Motion intensity: {latestMotion.toFixed(2)}%</p>
    </section>
  )
}
