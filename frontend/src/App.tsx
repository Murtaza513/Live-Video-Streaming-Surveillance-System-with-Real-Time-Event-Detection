import { AlertPanel } from './components/AlertPanel'
import { ConnectionStatus } from './components/ConnectionStatus'
import { EventHistory } from './components/EventHistory'
import { VideoFeed } from './components/VideoFeed'
import { SurveillanceProvider } from './context/SurveillanceContext'

function App() {
  return (
    <SurveillanceProvider>
      <main className="min-h-screen bg-slate-900 px-4 py-6 text-slate-100 md:px-10">
        <div className="mx-auto max-w-7xl space-y-6">
          <header className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-bold">Real-Time Surveillance Dashboard</h1>
              <p className="text-sm text-slate-400">Intelligent monitoring with motion and person detection</p>
            </div>
            <ConnectionStatus />
          </header>

          <section className="grid gap-6 lg:grid-cols-3">
            <div className="space-y-6 lg:col-span-2">
              <VideoFeed />
              <EventHistory />
            </div>
            <AlertPanel />
          </section>
        </div>
      </main>
    </SurveillanceProvider>
  )
}

export default App
