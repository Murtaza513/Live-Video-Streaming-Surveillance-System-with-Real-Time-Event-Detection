/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#0f172a',   // page background
        panel:   '#1e293b',   // card / section background
        border:  '#334155',   // subtle borders
        accent:  '#22d3ee',   // cyan highlight
        alert:   '#ef4444',   // red danger
        success: '#22c55e',   // green success
        warn:    '#facc15',   // yellow warning
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
