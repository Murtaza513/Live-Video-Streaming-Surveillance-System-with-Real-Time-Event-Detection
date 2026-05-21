import React from 'react'
import { SurveillanceProvider } from './context/SurveillanceContext'
import AlertPanel from './components/AlertPanel'
import ConnectionStatus from './components/ConnectionStatus'
import EventHistory from './components/EventHistory'
import LiveFeed from './components/LiveFeed'

export default function App() {
  return (
    <SurveillanceProvider>
      <div className="min-h-screen bg-surface text-white font-sans flex flex-col">

        {/* ── Header ─────────────────────────────────────────────────────── */}
        <header className="bg-panel border-b border-border px-4 md:px-8 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            {/* Brand mark */}
            <div className="w-8 h-8 rounded-md bg-accent/20 border border-accent/40 flex items-center justify-center">
              <span className="text-accent text-sm font-bold">S</span>
            </div>
            <div>
              <h1 className="text-base font-bold leading-tight tracking-tight">SurveillanceOS</h1>
              <p className="text-xs text-slate-500 leading-tight">Real-Time Intelligence Platform</p>
            </div>
          </div>
          <ConnectionStatus />
        </header>

        {/* ── Main content grid ──────────────────────────────────────────── */}
        <main className="flex-1 p-4 md:p-6 grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 auto-rows-min">

          {/* Live feed — spans 2 columns on large screens */}
          <section className="lg:col-span-2 bg-panel border border-border rounded-xl p-4 md:p-6">
            <LiveFeed />
          </section>

          {/* Alert panel — right sidebar */}
          <section className="bg-panel border border-border rounded-xl p-4 md:p-6">
            <AlertPanel />
          </section>

          {/* Event history — full width */}
          <section className="lg:col-span-3 bg-panel border border-border rounded-xl p-4 md:p-6">
            <EventHistory />
          </section>

        </main>

        {/* ── Footer ─────────────────────────────────────────────────────── */}
        <footer className="border-t border-border px-4 md:px-8 py-3 text-xs text-slate-600 text-center flex-shrink-0">
          SurveillanceOS v1.0 — Real-Time Video Surveillance Platform
        </footer>

      </div>
    </SurveillanceProvider>
  )
}
