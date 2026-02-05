/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'bu-scarlet': '#CC0000',
        'rating-excellent': '#22c55e',
        'rating-good': '#84cc16',
        'rating-average': '#eab308',
        'rating-poor': '#ef4444',
      },
    },
  },
  plugins: [],
}
