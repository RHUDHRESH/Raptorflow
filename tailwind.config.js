/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // RaptorFlow Design System v1.0 — "Charcoal / Ivory"
        'rf': {
          'charcoal': '#2A2529',
          'ivory': '#F3F0E7',
        },

        // Surfaces
        'canvas': '#EFEDE6',
        'surface': '#F7F5EF',
        'raised': '#FFFFFF',

        // Ink (Text)
        'ink': {
          1: '#2A2529',
          2: '#5C565B',
          3: '#847C82',
          inverse: '#F3F0E7',
        },

        // Borders
        'border-rf': {
          1: '#E3DED3',
          2: '#D2CCC0',
        },

        // Focus ring
        'focus': {
          outer: '#D2CCC0',
          inner: '#2A2529',
        },

        // Legacy compat (map to new tokens where possible to prevent breaking)
        background: '#EFEDE6',
        foreground: '#2A2529',
        accent: {
          DEFAULT: '#2A2529',
        }
      },

      fontFamily: {
        sans: ['DM Sans', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        display: ['DM Sans', 'system-ui', 'sans-serif'],
      },

      spacing: {
        'rf-1': '4px',
        'rf-2': '8px',
        'rf-3': '12px',
        'rf-4': '16px',
        'rf-5': '20px',
        'rf-6': '24px',
        'rf-8': '32px',
        'rf-10': '40px',
        'rf-12': '48px',
        'rf-16': '64px',
      },

      borderRadius: {
        'rf-sm': '10px',
        'rf-md': '14px',
        'rf-lg': '18px',
      },

      boxShadow: {
        // "Modals: one soft shadow allowed (subtle)"
        'modal': '0 12px 32px -4px rgba(42, 37, 41, 0.08), 0 4px 16px -4px rgba(42, 37, 41, 0.04)',
        // "Cards: border-only" (override defaults)
        'sm': 'none',
        'DEFAULT': 'none',
        'md': 'none',
        'lg': 'none',
        'xl': 'none',
        '2xl': 'none',
      },

      transitionTimingFunction: {
        'rf': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
}
