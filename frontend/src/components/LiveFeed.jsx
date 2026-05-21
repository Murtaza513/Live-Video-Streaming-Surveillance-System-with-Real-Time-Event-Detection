import React from 'react'
import { useSurveillance } from '../context/SurveillanceContext'

export default function LiveFeed() {
  const { state } = useSurveillance()
  const {
    latestFrame,
    motionDetected,
    personDetected,
    motionRatio,
    jpegQuality,
    scale,
    connectionStatus,
  } = state

  // Highlight border colour based on current detection state
  const borderClass = personDetected
    ? 'ring-2 ring-alert'
    : motionDetected
    ? 'ring-2 ring-warn'
    : 'ring-1 ring-border'

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-widest">
        Live Feed
      </h2>

      {/* Video frame */}
      <div className={`relative rounded-lg overflow-hidden bg-slate-900 ${borderClass}`}>
        {latestFrame ? (
          <img
            src={`data:image/jpeg;base64,${latestFrame}`}
            alt="Live surveillance feed"
            className="w-full h-auto block"
            draggable={false}
          />
        ) : (
          <div className="flex items-center justify-center h-64 text-slate-500 text-sm select-none">
            {connectionStatus === 'connecting'
              ? 'Connecting to camera…'
              : connectionStatus === 'connected'
              ? 'Waiting for first frame…'
              : 'No signal'}
          </div>
        )}

        {/* Detection badge overlay */}
        {(personDetected || motionDetected) && (
          <div className="absolute top-3 left-3 flex gap-2">
            {personDetected && (
              <span className="px-2 py-0.5 rounded text-xs font-bold bg-alert text-white shadow">
                PERSON
              </span>
            )}
            {motionDetected && !personDetected && (
              <span className="px-2 py-0.5 rounded text-xs font-bold bg-warn text-black shadow">
                MOTION
              </span>
            )}
          </div>
        )}
      </div>

      {/* Compression and detection metadata */}
      <div className="grid grid-cols-3 gap-3 text-center text-xs text-slate-400">
        <div className="bg-surface rounded-lg p-3 border border-border">
          <div className="text-white font-mono text-sm font-bold">{jpegQuality}</div>
          <div className="mt-0.5">JPEG Quality</div>
        </div>
        <div className="bg-surface rounded-lg p-3 border border-border">
          <div className="text-white font-mono text-sm font-bold">
            {(scale * 100).toFixed(0)}%
          </div>
          <div className="mt-0.5">Resolution</div>
        </div>
        <div className="bg-surface rounded-lg p-3 border border-border">
          <div
            className={`font-mono text-sm font-bold ${
              motionDetected ? 'text-warn' : 'text-white'
            }`}
          >
            {(motionRatio * 100).toFixed(1)}%
          </div>
          <div className="mt-0.5">Motion Δ</div>
        </div>
      </div>
    </div>
  )
}
