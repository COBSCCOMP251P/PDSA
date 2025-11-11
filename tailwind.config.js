/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./shared/frontend/**/*.{html,js}",
    "./games/**/*.{html,js}"
  ],
  theme: {
    extend: {
      colors: {
        'game-primary': '#6366f1',
        'game-secondary': '#8b5cf6', 
        'game-accent': '#06b6d4',
        'game-success': '#10b981',
        'game-warning': '#f59e0b',
        'game-error': '#ef4444'
      },
      fontFamily: {
        'game': ['Inter', 'sans-serif']
      },
      animation: {
        'bounce-slow': 'bounce 3s infinite',
        'pulse-slow': 'pulse 4s infinite'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}