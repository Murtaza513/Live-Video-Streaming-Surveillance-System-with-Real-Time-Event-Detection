/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        panel: '#111827',
        accent: '#22c55e',
        danger: '#ef4444',
      },
    },
  },
  plugins: [],
}
