/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Editorial Color System
        canvas: '#F7F4EF',
        charcoal: '#1F1F1F',
        aubergine: '#3B2339',
        gold: '#C8A56A',
        line: '#DCD6C8',

        // Keep white/black for compatibility
        white: '#FFFFFF',
        black: '#000000',

        // Grayscale Palette (keep for backward compatibility)
        neutral: {
          50: '#FAFAFA',
          100: '#F4F4F5',
          200: '#E4E4E7',
          300: '#D4D4D8',
          400: '#A1A1AA',
          500: '#71717A',
          600: '#52525B',
          700: '#3F3F46',
          800: '#27272A',
          900: '#18181B',
          950: '#09090B',
        },
        gray: {
          50: '#FAFAFA',
          100: '#F4F4F5',
          200: '#E4E4E7',
          300: '#D4D4D8',
          400: '#A1A1AA',
          500: '#71717A',
          600: '#52525B',
          700: '#3F3F46',
          800: '#27272A',
          900: '#18181B',
          950: '#09090B',
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'], // Editorial sans for body
        serif: ['"Playfair Display"', 'Georgia', 'serif'], // Editorial serif for headings
        mono: ['"JetBrains Mono"', 'monospace'], // Mono for UI details
        display: ['"Playfair Display"', 'Georgia', 'serif'], // Alias display to serif
        body: ['"DM Sans"', 'system-ui', 'sans-serif'], // Alias body to DM Sans
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      letterSpacing: {
        'tightest': '-0.075em',
        'widest': '0.25em',
      },
      lineHeight: {
        'tight': '0.95',
      },
      fontSize: {
        '10xl': '10rem',
        '11xl': '12rem',
        '12xl': '14rem',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
      },
      animation: {
        'blob': 'blob 7s infinite',
      },
      keyframes: {
        blob: {
          '0%': {
            transform: 'translate(0px, 0px) scale(1)',
          },
          '33%': {
            transform: 'translate(30px, -50px) scale(1.1)',
          },
          '66%': {
            transform: 'translate(-20px, 20px) scale(0.9)',
          },
          '100%': {
            transform: 'translate(0px, 0px) scale(1)',
          },
        },
      },
    },
  },
  plugins: [],
}
