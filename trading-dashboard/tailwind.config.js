/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'trading-dark': '#0f1419',
        'trading-darker': '#0a0e14',
        'trading-light': '#1e2328',
        'trading-green': '#00d4aa',
        'trading-red': '#ff6b6b',
        'trading-blue': '#3b82f6',
        'trading-yellow': '#fbbf24',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/postcss')(),
    require('autoprefixer'),
  ],
} 