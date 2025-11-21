/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fdfaf6',
          100: '#f8f5f0',
          200: '#f1ece4',
          300: '#e7e2d8',
          400: '#d8d2c7',
          500: '#bcb5af',
          600: '#8f8983',
          700: '#5f5b56',
          800: '#3c3935',
          900: '#211f1d',
        },
        accent: {
          50: '#fefbf8',
          100: '#f9f3ea',
          200: '#f1e4d1',
          300: '#e8d2b6',
          400: '#d2b38c',
          500: '#b48f63',
          600: '#8c6c47',
          700: '#624a2f',
          800: '#3e2e1d',
          900: '#1d140c',
        },
        neutral: {
          50: '#fdfcf9',
          100: '#f7f5f0',
          200: '#efede5',
          300: '#dedbd1',
          400: '#c7c3ba',
          500: '#a7a399',
          600: '#7d7a72',
          700: '#56534b',
          800: '#36332c',
          900: '#1d1b17',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Playfair Display', 'Georgia', 'serif'],
        display: ['Playfair Display', 'serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out',
        'fade-in-up': 'fadeInUp 0.6s ease-out',
        'slide-in-right': 'slideInRight 0.5s ease-out',
        'scale-in': 'scaleIn 0.4s ease-out',
        'shimmer': 'shimmer 2s infinite',
        'spin': 'spin 1s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
    },
  },
}
