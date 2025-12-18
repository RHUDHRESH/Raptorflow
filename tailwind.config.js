/** @type {import('tailwindcss').Config} */
export default {
	darkMode: ["class"],
	content: [
		"./index.html",
		"./src/**/*.{js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			colors: {
				/* SYSTEM: NANOBANA / BIO-DIGITAL */
				/* Base: Deep Void & Crisp Starlight */
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',

				/* The Void Scale (Deep Blue-Blacks) */
				obsidian: {
					DEFAULT: '#05050A', /* Deepest Void */
					'50': '#1A1A1E',
					'100': '#141418',
					'200': '#101014',
					'300': '#0A0A0E',
					'400': '#05050A',
					'500': '#000000',
				},

				/* The Starlight Scale (Crisp Cool Whites) */
				starlight: {
					DEFAULT: '#FFFFFF',
					'50': '#FFFFFF',
					'100': '#F5F8FA',
					'200': '#E8EFF5',
					'300': '#D1DBE5',
					'400': '#B0C0D0',
				},

				/* Active Elements */
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				primary: {
					DEFAULT: 'hsl(var(--primary))',
					foreground: 'hsl(var(--primary-foreground))',
					glow: 'hsl(var(--primary) / 0.5)'
				},
				secondary: {
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))'
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))'
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))'
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))'
				},

				/* Nanobana Accents (Neon/Bio) */
				neon: {
					orange: '#FF8800',
					lime: '#CCFF00',
					plasma: '#FF0055',
					violet: '#BC13FE',
					amber: '#FFD600'
				},

				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				sidebar: {
					DEFAULT: '#05050A', // Obsidian tint
					foreground: '#FFFFFF',
					primary: '#FF8800', // Neon Orange
					'primary-foreground': '#000000',
					accent: 'rgba(255, 255, 255, 0.05)', // Glass hover
					'accent-foreground': '#FFFFFF',
					border: 'rgba(255, 255, 255, 0.05)',
					ring: '#FF8800',
				},
			},
			fontFamily: {
				/* Tech-First Typography */
				sans: ['Inter', 'SF Pro Display', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
				mono: ['JetBrains Mono', 'SF Mono', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
				display: ['Space Grotesk', 'Inter', 'sans-serif'], // Optional for headers if we add Space Grotesk later
			},
			fontSize: {
				'2xs': ['0.625rem', { lineHeight: '1rem' }],
				xs: ['0.75rem', { lineHeight: '1.25rem' }],
				sm: ['0.875rem', { lineHeight: '1.5rem' }],
				base: ['1rem', { lineHeight: '1.75rem' }],
				lg: ['1.125rem', { lineHeight: '1.75rem' }],
				xl: ['1.25rem', { lineHeight: '1.75rem' }],
				'2xl': ['1.5rem', { lineHeight: '2rem' }],
				'3xl': ['1.875rem', { lineHeight: '2.25rem' }],
				'4xl': ['2.25rem', { lineHeight: '2.5rem' }],
				'5xl': ['3rem', { lineHeight: '1.1' }],
				'6xl': ['3.75rem', { lineHeight: '1.1' }],
				'7xl': ['4.5rem', { lineHeight: '1.1' }],
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)',
				'pill': '9999px',
			},
			boxShadow: {
				'glow-sm': '0 0 10px -2px var(--shadow-color, rgba(255, 136, 0, 0.2))',
				'glow-md': '0 0 20px -5px var(--shadow-color, rgba(255, 136, 0, 0.3))',
				'glow-lg': '0 0 40px -10px var(--shadow-color, rgba(255, 136, 0, 0.4))',
				'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.36)',
				'glass-inset': 'inset 0 0 0 1px rgba(255, 255, 255, 0.05)',
			},
			backgroundImage: {
				'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
				'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
				'void-gradient': 'linear-gradient(to bottom right, #05050A, #101014)',
				'glass-gradient': 'linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)',
			},
			keyframes: {
				'accordion-down': {
					from: { height: '0' },
					to: { height: 'var(--radix-accordion-content-height)' },
				},
				'accordion-up': {
					from: { height: 'var(--radix-accordion-content-height)' },
					to: { height: '0' },
				},
				'pulse-glow': {
					'0%, 100%': { opacity: '1', boxShadow: '0 0 10px var(--shadow-color)' },
					'50%': { opacity: '0.8', boxShadow: '0 0 20px var(--shadow-color)' },
				},
				'float': {
					'0%, 100%': { transform: 'translateY(0)' },
					'50%': { transform: 'translateY(-10px)' },
				},
				'liquid': {
					'0%': { transform: 'translate(0, 0)' },
					'33%': { transform: 'translate(5px, -5px)' },
					'66%': { transform: 'translate(-5px, 5px)' },
					'100%': { transform: 'translate(0, 0)' },
				}
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
				'float': 'float 6s ease-in-out infinite',
				'liquid': 'liquid 8s ease-in-out infinite',
			},
		},
	},
	plugins: [],
}
