/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Monochrome System - RaptorFlow Editorial
        black: '#000000',
        white: '#FFFFFF',
        ink: '#0c0c0c',
        cream: {
          DEFAULT: '#fdfcf9',
          50: '#fdfcf9',
        },

        // Oxblood Accent - 5% usage only
        oxblood: {
          DEFAULT: '#6b2b2d',
          light: '#8f3739',
          dark: '#4a1d1e',
        },

        // Grayscale Hierarchy
        gray: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['GFS Didot', 'Didot', 'Bodoni Moda', 'Georgia', 'serif'],
        display: ['GFS Didot', 'Didot', 'serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1.5' }],      // 12px
        'sm': ['0.875rem', { lineHeight: '1.5' }],     // 14px
        'base': ['1rem', { lineHeight: '1.5' }],       // 16px
        'lg': ['1.125rem', { lineHeight: '1.5' }],     // 18px
        'xl': ['1.25rem', { lineHeight: '1.4' }],      // 20px
        '2xl': ['1.5rem', { lineHeight: '1.3' }],      // 24px
        '3xl': ['1.875rem', { lineHeight: '1.2' }],    // 30px
        '4xl': ['2.25rem', { lineHeight: '1.1' }],     // 36px
        '5xl': ['3rem', { lineHeight: '1' }],          // 48px
        '6xl': ['3.75rem', { lineHeight: '1' }],       // 60px
        '7xl': ['4rem', { lineHeight: '0.95' }],       // 64px
      },
      spacing: {
        // 8px grid system (4px base)
        '0.5': '2px',
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '7': '28px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px',
        '20': '80px',
        '24': '96px',
      },
      borderRadius: {
        'none': '0',
        'sm': '2px',
        DEFAULT: '4px',
        'md': '4px',
        'lg': '6px',
        'full': '9999px',
      },
      transitionDuration: {
        '100': '100ms',
        '150': '150ms',
        '180': '180ms',
        '200': '200ms',
        '300': '300ms',
        '400': '400ms',
      },
      transitionTimingFunction: {
        'luxury': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'editorial': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      animation: {
        'fade-in': 'fadeIn 300ms ease-out',
        'fade-in-up': 'fadeInUp 300ms ease-out',
        'slide-in-right': 'slideInRight 300ms ease-out',
        'scale-in': 'scaleIn 180ms ease-out',
        'shimmer': 'shimmer 2s infinite',
        'spin': 'spin 1s linear infinite',
        'press': 'press 100ms ease-out',
        'blob': 'blob 7s infinite',
      },
      animationDelay: {
        '0': '0s',
        '2000': '2s',
        '4000': '4s',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(-12px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.96)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        press: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(0.98)' },
          '100%': { transform: 'scale(1)' },
        },
        blob: {
          '0%, 100%': { transform: 'translate(0px, 0px) scale(1)' },
          '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
        },
      },
    },
  },
  plugins: [
    function ({ matchUtilities, theme }) {
      matchUtilities(
        {
          'animation-delay': (value) => {
            return {
              'animation-delay': value,
            }
          },
        },
        {
          values: theme('animationDelay'),
        }
      )
    },
  ],
}
