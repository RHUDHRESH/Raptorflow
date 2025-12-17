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
				/* MP072 Core Palette */
				palladian: {
					DEFAULT: '#EEE9DF',
					'50': '#F5F2EB',
					'100': '#EEE9DF',
					'200': '#E5DFD3',
					'300': '#D9D2C4',
					'400': '#CCC4B4',
				},
				oatmeal: {
					DEFAULT: '#C9C1B1',
					light: '#D8D2C5',
					dark: '#B8AFA0',
				},
				blueFantastic: {
					DEFAULT: '#2C3B4D',
					light: '#3D4F65',
					dark: '#1D2833',
					muted: '#6B7A8C',
				},
				burningFlame: {
					DEFAULT: '#FFB162',
					light: '#FFC48A',
					dark: '#E89A4A',
					glow: 'rgba(255, 177, 98, 0.3)',
				},
				/* Legacy mappings */
				/* MP072 Palette - 60-30-10 Rule */
				paper: {
					'50': '#F5F1E8',   /* Lightest cream */
					'100': '#EEE9DF',  /* Palladian - 60% base */
					'200': '#E5DFD3',  /* Slightly darker */
					'300': '#D9D2C4',  /* Borders/dividers */
					'400': '#C9C1B1',  /* Oatmeal - 30% secondary */
					DEFAULT: '#EEE9DF' /* Palladian */
				},
				ink: {
					'50': '#E8ECF0',
					'100': '#D1D8E0',
					'200': '#A3B1C0',
					'300': '#6B7A8C',  /* Muted text */
					'400': '#4A5B6D',  /* Secondary text */
					'500': '#3A4A5C',  /* Darker text */
					'600': '#2C3B4D',  /* Blue Fantastic - 30% dark */
					'700': '#1B2632',  /* Abyssal - dark mode base */
					'800': '#141C24',
					'900': '#0D1318',
					DEFAULT: '#2C3B4D' /* Blue Fantastic */
				},
				/* Burning Flame - 10% accent */
				signal: {
					DEFAULT: 'hsl(var(--signal))',
					muted: 'hsl(var(--signal) / 0.12)',
					raw: '#FFB162' /* Burning Flame */
				},
				/* Muted monochrome status colors */
				success: {
					DEFAULT: '#4A5B6D',  /* Blue-tinted neutral */
					light: '#5A6B7D',
					muted: 'rgba(74, 91, 109, 0.1)'
				},
				warning: {
					DEFAULT: '#A89A7A',  /* Oatmeal-based */
					light: '#B8AA8A',
					muted: 'rgba(168, 154, 122, 0.1)'
				},
				error: {
					DEFAULT: '#A35139',  /* Truffle Trouble */
					light: '#B36149',
					muted: 'rgba(163, 81, 57, 0.1)'
				},
				surface: {
					DEFAULT: 'hsl(var(--surface))',
					elevated: 'hsl(var(--surface-elevated))',
					muted: 'hsl(var(--surface-muted))',
					overlay: 'hsl(var(--surface-overlay))'
				},
				border: {
					DEFAULT: 'hsl(var(--border))',
					light: 'hsl(var(--border-light))',
					dark: 'hsl(var(--border-dark))'
				},
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					DEFAULT: 'hsl(var(--primary))',
					foreground: 'hsl(var(--primary-foreground))'
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
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				sidebar: {
					DEFAULT: 'hsl(var(--sidebar-background))',
					foreground: 'hsl(var(--sidebar-foreground))',
					primary: 'hsl(var(--sidebar-primary))',
					'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
					accent: 'hsl(var(--sidebar-accent))',
					'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
					border: 'hsl(var(--sidebar-border))',
					ring: 'hsl(var(--sidebar-ring))'
				}
			},
			fontFamily: {
				serif: [
					'Playfair Display',
					'Georgia',
					'serif'
				],
				sans: [
					'Inter',
					'SF Pro Display',
					'system-ui',
					'-apple-system',
					'sans-serif'
				],
				mono: [
					'Inter',
					'SF Pro Display',
					'system-ui',
					'-apple-system',
					'sans-serif'
				],
				display: [
					'Playfair Display',
					'Georgia',
					'serif'
				]
			},
			fontSize: {
				'headline-xl': [
					'3.5rem',
					{
						lineHeight: '1.1',
						letterSpacing: '-0.02em',
						fontWeight: '500'
					}
				],
				'headline-lg': [
					'2.5rem',
					{
						lineHeight: '1.15',
						letterSpacing: '-0.015em',
						fontWeight: '500'
					}
				],
				'headline-md': [
					'1.875rem',
					{
						lineHeight: '1.2',
						letterSpacing: '-0.01em',
						fontWeight: '500'
					}
				],
				'headline-sm': [
					'1.5rem',
					{
						lineHeight: '1.25',
						letterSpacing: '-0.005em',
						fontWeight: '500'
					}
				],
				'headline-xs': [
					'1.25rem',
					{
						lineHeight: '1.3',
						fontWeight: '500'
					}
				],
				'body-lg': [
					'1.125rem',
					{
						lineHeight: '1.6'
					}
				],
				'body-md': [
					'1rem',
					{
						lineHeight: '1.6'
					}
				],
				'body-sm': [
					'0.875rem',
					{
						lineHeight: '1.5'
					}
				],
				'body-xs': [
					'0.75rem',
					{
						lineHeight: '1.5'
					}
				],
				caption: [
					'0.6875rem',
					{
						lineHeight: '1.4',
						letterSpacing: '0.04em',
						fontWeight: '500'
					}
				]
			},
			spacing: {
				'18': '4.5rem',
				'22': '5.5rem',
				'26': '6.5rem',
				'30': '7.5rem'
			},
			borderRadius: {
				editorial: '0.5rem',
				card: '0.75rem',
				panel: '1rem'
			},
			boxShadow: {
				'editorial-sm': '0 1px 2px rgba(26, 26, 26, 0.04)',
				editorial: '0 2px 8px rgba(26, 26, 26, 0.06)',
				'editorial-md': '0 4px 16px rgba(26, 26, 26, 0.08)',
				'editorial-lg': '0 8px 32px rgba(26, 26, 26, 0.1)',
				'editorial-xl': '0 16px 48px rgba(26, 26, 26, 0.12)',
				'inner-soft': 'inset 0 1px 2px rgba(26, 26, 26, 0.04)'
			},
			animation: {
				'fade-in': 'fadeIn 0.4s ease-out',
				'fade-up': 'fadeUp 0.5s ease-out',
				'scale-in': 'scaleIn 0.3s ease-out',
				'slide-up': 'slideUp 0.4s ease-out',
				'pulse-soft': 'pulseSoft 2s ease-in-out infinite'
			},
			keyframes: {
				fadeIn: {
					'0%': {
						opacity: '0'
					},
					'100%': {
						opacity: '1'
					}
				},
				fadeUp: {
					'0%': {
						opacity: '0',
						transform: 'translateY(8px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0)'
					}
				},
				scaleIn: {
					'0%': {
						opacity: '0',
						transform: 'scale(0.97)'
					},
					'100%': {
						opacity: '1',
						transform: 'scale(1)'
					}
				},
				slideUp: {
					'0%': {
						transform: 'translateY(100%)'
					},
					'100%': {
						transform: 'translateY(0)'
					}
				},
				pulseSoft: {
					'0%, 100%': {
						opacity: '1'
					},
					'50%': {
						opacity: '0.7'
					}
				}
			},
			transitionDuration: {
				'175': '175ms',
				'225': '225ms'
			},
			transitionTimingFunction: {
				editorial: 'cubic-bezier(0.4, 0, 0.2, 1)',
				smooth: 'cubic-bezier(0.25, 0.1, 0.25, 1)'
			}
		}
	},
	plugins: [],
}
