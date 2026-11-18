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
        cryo: {
          darkest: '#050811',
          dark: '#0A0F1D',
          surface: '#0F172A',
          card: '#131D35',
          border: '#1E293B',
          borderLight: '#334155',
          cyan: '#38BDF8',
          cyanGlow: '#0EA5E9',
          ice: '#7DD3FC',
          muted: '#94A3B8',
          subtle: '#64748B',
          glacier: '#0284C7',
          grounded: '#2DD4BF',
          warning: '#F59E0B',
          danger: '#EF4444',
          success: '#10B981'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif']
      }
    },
  },
  plugins: [],
}
