/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // PropulseIQ 情緒色彩系統
        sentiment: {
          'very-positive': '#22c55e',
          'positive': '#86efac',
          'neutral': '#94a3b8',
          'negative': '#fb923c',
          'very-negative': '#ef4444',
        },
      },
    },
  },
  plugins: [],
}
