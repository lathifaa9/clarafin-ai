/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: '#0f172a',
        glassBg: 'rgba(15, 23, 42, 0.45)',
        glassBorder: 'rgba(255, 255, 255, 0.08)',
        accentTeal: '#0ea5e9',
        accentViolet: '#8b5cf6',
        accentRose: '#f43f5e',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
