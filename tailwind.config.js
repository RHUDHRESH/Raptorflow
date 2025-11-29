/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // High Fashion Monochrome System
        white: '#FFFFFF',
        black: '#000000',
        
        // Neutral Scale (Warm Greys for "Luxe" feel)
        neutral: {
          50: '#FAFAF9',  // Stone-50
          100: '#F5F5F4', // Stone-100
          200: '#E7E7E5', // Stone-200
          300: '#D6D3D1', // Stone-300
          400: '#A8A29E', // Stone-400
          500: '#78716C', // Stone-500
          600: '#57534E', // Stone-600
          700: '#44403C', // Stone-700
          800: '#292524', // Stone-800
          900: '#1C1917', // Stone-900
          950: '#0C0A09', // Stone-950
        },

        // Semantic Accents (Used Sparingly)
        accent: {
          DEFAULT: '#171717', // Black as primary accent
          secondary: '#57534E',
          success: '#059669', // Emerald-600 (muted)
          warning: '#D97706', // Amber-600 (muted)
          error: '#DC2626',   // Red-600 (muted)
          info: '#2563EB',    // Blue-600 (muted)
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
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
        '7xl': ['4.5rem', { lineHeight: '1' }],        // 72px
      },
      spacing: {
        '0': '0px',
        'px': '1px',
        '0.5': '2px',
        '1': '4px',
        '1.5': '6px',
        '2': '8px',
        '2.5': '10px',
        '3': '12px',
        '3.5': '14px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '7': '28px',
        '8': '32px',
        '9': '36px',
        '10': '40px',
        '11': '44px',
        '12': '48px',
        '14': '56px',
        '16': '64px',
        '20': '80px',
        '24': '96px',
        '28': '112px',
        '32': '128px',
        '36': '144px',
        '40': '160px',
        '44': '176px',
        '48': '192px',
        '52': '208px',
        '56': '224px',
        '60': '240px',
        '64': '256px',
        '72': '288px',
        '80': '320px',
        '96': '384px',
      },
      borderRadius: {
        'none': '0',
        'sm': '2px',
        DEFAULT: '4px',
        'md': '6px',
        'lg': '8px',
        'xl': '12px',
        '2xl': '16px',
        '3xl': '24px',
        'full': '9999px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        'none': 'none',
        'flat': '0 0 0 1px rgba(0,0,0,0.05)',
        'flat-hover': '0 0 0 1px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.05)',
      },
      // Removed heavy animations, keeping only functional ones
      animation: {
        'fade-in': 'fadeIn 200ms ease-out',
        'slide-up': 'slideUp 200ms ease-out',
        'spin': 'spin 1s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
