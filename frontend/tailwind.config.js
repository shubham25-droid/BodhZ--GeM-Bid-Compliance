/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          navy: '#061C3D',
          navyLight: '#0A2540',
          saffron: '#E65100',
          saffronLight: '#FFF3E0',
          emerald: '#1B5E20',
          emeraldLight: '#E8F5E9',
          crimson: '#B71C1C',
          crimsonLight: '#FFEBEE',
          gold: '#D4AF37',
          bg: '#F8FAFC',
          card: '#FFFFFF',
          border: '#E2E8F0',
          textDark: '#0F172A',
          textMuted: '#475569',
        }
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
