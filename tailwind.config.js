/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // RaptorFlow Charcoal / Ivory Design System
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
        },
        
        // Borders
        'border-rf': {
          1: '#E3DED3',
          2: '#D2CCC0',
        },
        
        // Legacy colors for backward compatibility
        background: '#EFEDE6',
        foreground: '#2A2529',
        
        // Accent colors (kept minimal)
        accent: {
          DEFAULT: '#2A2529',
          50: '#F7F5EF',
          100: '#EFEDE6',
          200: '#E3DED3',
          300: '#D2CCC0',
          400: '#847C82',
          500: '#5C565B',
          600: '#2A2529',
          700: '#1a1819',
          800: '#0f0e0f',
          900: '#000000',
        },
        
        // Legacy aliases
        canvas: '#EFEDE6',
        charcoal: '#2A2529',
        aubergine: '#2A2529',
        gold: '#2A2529',
        champagne: '#5C565B',
        noir: '#2A2529',
        ivory: '#F3F0E7',
        line: '#E3DED3',
      },
      
      fontFamily: {
        sans: ['DM Sans', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        display: ['DM Sans', 'system-ui', 'sans-serif'],
      },
      
      fontSize: {
        // RaptorFlow type scale
        'h1': ['40px', { lineHeight: '48px', fontWeight: '700', letterSpacing: '-0.02em' }],
        'h2': ['32px', { lineHeight: '40px', fontWeight: '700', letterSpacing: '-0.01em' }],
        'h3': ['24px', { lineHeight: '32px', fontWeight: '700' }],
        'h4': ['20px', { lineHeight: '28px', fontWeight: '600' }],
        'body': ['16px', { lineHeight: '26px', fontWeight: '400' }],
        'body-sm': ['14px', { lineHeight: '22px', fontWeight: '400' }],
        'label': ['12px', { lineHeight: '16px', fontWeight: '600', letterSpacing: '0.08em' }],
        'mono-sm': ['12px', { lineHeight: '18px', fontWeight: '500' }],
        
        // Display sizes
        'display-2xl': ['clamp(3rem, 8vw, 6rem)', { lineHeight: '0.95', letterSpacing: '-0.02em' }],
        'display-xl': ['clamp(2.5rem, 6vw, 4.5rem)', { lineHeight: '1', letterSpacing: '-0.02em' }],
        'display-lg': ['clamp(2rem, 5vw, 3.5rem)', { lineHeight: '1.1', letterSpacing: '-0.01em' }],
        'display-md': ['clamp(1.5rem, 4vw, 2.5rem)', { lineHeight: '1.2' }],
        'display-sm': ['clamp(1.25rem, 3vw, 1.75rem)', { lineHeight: '1.3' }],
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
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'grain': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E\")",
      },
      
      animation: {
        'spin-slow': 'spin 20s linear infinite',
        'pulse-slow': 'pulse 4s ease-in-out infinite',
        'float': 'float 4s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards',
      },
      
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      
      boxShadow: {
        'soft': '0 2px 8px rgba(42, 37, 41, 0.06)',
        'medium': '0 4px 16px rgba(42, 37, 41, 0.08)',
        'large': '0 8px 32px rgba(42, 37, 41, 0.12)',
        'glow': '0 0 60px rgba(42, 37, 41, 0.08)',
      },
      
      transitionTimingFunction: {
        'rf': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
}
