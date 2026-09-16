/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Outfit', 'Inter', 'sans-serif'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['Fira Code', 'Cascadia Code', 'JetBrains Mono', 'monospace'],
      },
      colors: {
        surface: {
          DEFAULT: '#0a0e1a',
          50: '#0d1220',
          100: '#111827',
          200: '#161d2e',
          300: '#1e2740',
          400: '#283450',
          500: '#334155',
        },
        brand: {
          50: '#eef4ff',
          100: '#d9e5ff',
          200: '#bccfff',
          300: '#8eb0ff',
          400: '#5985ff',
          500: '#3b63fb',
          600: '#2546f0',
          700: '#1d35dd',
          800: '#1e2db3',
          900: '#1e2b8d',
        },
        accent: {
          purple: '#8b5cf6',
          pink: '#ec4899',
          emerald: '#10b981',
          amber: '#f59e0b',
          cyan: '#06b6d4',
        },
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in': 'slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in-left': 'slideInLeft 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        'glow-pulse': 'glowPulse 2.5s infinite',
        'shimmer': 'shimmer 2s infinite linear',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'scale(0.95) translateY(8px)' },
          '100%': { opacity: '1', transform: 'scale(1) translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-12px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(59, 99, 251, 0.5)' },
          '50%': { boxShadow: '0 0 20px 4px rgba(59, 99, 251, 0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      boxShadow: {
        'glow-sm': '0 0 12px -2px rgba(59, 99, 251, 0.25)',
        'glow-md': '0 0 24px -4px rgba(59, 99, 251, 0.35)',
        'glow-lg': '0 0 40px -6px rgba(59, 99, 251, 0.4)',
        'dark-elevation': '0 2px 8px rgba(0,0,0,0.3), 0 8px 32px rgba(0,0,0,0.4)',
        'dark-elevation-lg': '0 4px 16px rgba(0,0,0,0.4), 0 16px 48px rgba(0,0,0,0.5)',
      },
    },
  },
  plugins: [],
}
