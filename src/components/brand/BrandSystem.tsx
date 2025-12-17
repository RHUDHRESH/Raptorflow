import React from 'react'
import { motion } from 'framer-motion'

// ═══════════════════════════════════════════════════════════════════════════════
// RAPTORFLOW BRAND SYSTEM
// Premium icons, logo, and visual identity
// ═══════════════════════════════════════════════════════════════════════════════

// ───────────────────────────────────────────────────────────────────────────────
// MAIN LOGO
// Bold serif "R" with a raptor claw strike through and lightning accent
// ───────────────────────────────────────────────────────────────────────────────

export const RaptorFlowLogo = ({
    className = '',
    size = 40,
    showText = true,
    variant = 'default' // 'default' | 'light' | 'dark'
}: {
    className?: string
    size?: number
    showText?: boolean
    variant?: 'default' | 'light' | 'dark'
}) => {
    const colors = {
        default: { primary: 'hsl(var(--primary))', secondary: 'hsl(var(--foreground))' },
        light: { primary: '#F59E0B', secondary: '#FFFFFF' },
        dark: { primary: '#F59E0B', secondary: '#0A0A0A' }
    }

    const c = colors[variant]

    return (
        <div className={`flex items-center gap-3 ${className}`}>
            {/* Icon Mark */}
            <svg
                width={size}
                height={size}
                viewBox="0 0 48 48"
                fill="none"
                className="flex-shrink-0"
            >
                {/* Background rounded square */}
                <rect width="48" height="48" rx="12" fill={c.primary} />

                {/* Stylized R with claw marks */}
                <path
                    d="M14 12H26C31.523 12 36 16.477 36 22C36 26.5 33 30.5 28 31L36 40"
                    stroke={variant === 'light' ? '#0A0A0A' : '#FFFFFF'}
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    fill="none"
                />
                <path
                    d="M14 12V40"
                    stroke={variant === 'light' ? '#0A0A0A' : '#FFFFFF'}
                    strokeWidth="4"
                    strokeLinecap="round"
                />

                {/* Claw accent marks - dynamic slash */}
                <path
                    d="M30 8L42 20"
                    stroke={variant === 'light' ? '#0A0A0A' : '#FFFFFF'}
                    strokeWidth="2"
                    strokeLinecap="round"
                    opacity="0.6"
                />
                <path
                    d="M34 6L44 16"
                    stroke={variant === 'light' ? '#0A0A0A' : '#FFFFFF'}
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    opacity="0.4"
                />
            </svg>

            {/* Wordmark */}
            {showText && (
                <span
                    className="font-serif font-semibold tracking-tight"
                    style={{
                        fontSize: size * 0.6,
                        color: c.secondary
                    }}
                >
                    Raptor<span style={{ color: c.primary }}>Flow</span>
                </span>
            )}
        </div>
    )
}

// ───────────────────────────────────────────────────────────────────────────────
// ICON SYSTEM - Premium Luxe SVG Icons
// Hand-crafted icons to replace all emojis
// ───────────────────────────────────────────────────────────────────────────────

interface IconProps {
    size?: number
    className?: string
    animate?: boolean
}

// 🚀 → Launch / Rocket
export const IconLaunch = ({ size = 24, className = '', animate = false }: IconProps) => (
    <motion.svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        className={className}
        animate={animate ? { y: [0, -2, 0] } : undefined}
        transition={animate ? { duration: 2, repeat: Infinity } : undefined}
    >
        <path
            d="M12 2C12 2 14 6 14 10C14 14 12 18 12 18M12 18C12 18 10 14 10 10C10 6 12 2 12 2"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
        />
        <path
            d="M12 2C16 4 18 8 18 12C18 16 16 20 12 22C8 20 6 16 6 12C6 8 8 4 12 2Z"
            stroke="currentColor"
            strokeWidth="1.5"
            fill="currentColor"
            fillOpacity="0.1"
        />
        <circle cx="12" cy="10" r="2" fill="currentColor" />
        <path d="M8 20L4 22M16 20L20 22" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </motion.svg>
)

// 🎯 → Target / Strategy
export const IconTarget = ({ size = 24, className = '', animate = false }: IconProps) => (
    <motion.svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        className={className}
        animate={animate ? { scale: [1, 1.05, 1] } : undefined}
        transition={animate ? { duration: 2, repeat: Infinity } : undefined}
    >
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5" strokeDasharray="4 2" />
        <circle cx="12" cy="12" r="6" stroke="currentColor" strokeWidth="1.5" />
        <circle cx="12" cy="12" r="2" fill="currentColor" />
        <path d="M12 2V6M12 18V22M2 12H6M18 12H22" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </motion.svg>
)

// 📝 → Content / Writing
export const IconContent = ({ size = 24, className = '' }: IconProps) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <rect x="4" y="3" width="16" height="18" rx="2" stroke="currentColor" strokeWidth="1.5" />
        <path d="M8 8H16M8 12H14M8 16H12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M16 14L20 10L22 12L18 16L16 14Z" fill="currentColor" fillOpacity="0.2" stroke="currentColor" strokeWidth="1" />
    </svg>
)

// 🧪 → Testing / Lab
export const IconTesting = ({ size = 24, className = '' }: IconProps) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <path d="M9 3H15V8L19 20H5L9 8V3Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
        <path d="M8 14H16" stroke="currentColor" strokeWidth="1.5" />
        <circle cx="10" cy="17" r="1" fill="currentColor" />
        <circle cx="14" cy="16" r="1.5" fill="currentColor" fillOpacity="0.6" />
        <path d="M9 3H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
)

// ✅ → Tasks / Checklist
export const IconTasks = ({ size = 24, className = '' }: IconProps) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" />
        <path d="M7 9L9 11L13 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M7 15L9 17L13 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" opacity="0.5" />
        <path d="M16 9H19M16 15H18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
)

// 📊 → Results / Analytics
export const IconResults = ({ size = 24, className = '' }: IconProps) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <path d="M3 20L9 14L13 18L21 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="21" cy="10" r="2" fill="currentColor" />
        <path d="M21 10L21 4M21 4L15 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
)

// ⚡ → Speed / Lightning
export const IconSpeed = ({ size = 24, className = '', animate = false }: IconProps) => (
    <motion.svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        className={className}
        animate={animate ? { opacity: [1, 0.7, 1] } : undefined}
        transition={animate ? { duration: 1, repeat: Infinity } : undefined}
    >
        <path d="M13 2L4 14H11L10 22L20 9H12L13 2Z" fill="currentColor" fillOpacity="0.15" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    </motion.svg>
)

// 📋 → Campaign / Cards
export const IconCampaign = ({ size = 24, className = '' }: IconProps) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <rect x="2" y="6" width="14" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" transform="rotate(-5 9 14)" fill="currentColor" fillOpacity="0.05" />
        <rect x="5" y="3" width="14" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" fill="currentColor" fillOpacity="0.1" />
        <path d="M9 8L11 10L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M9 13H15M9 16H13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
)

// 🏢 → Agency / Building
export const IconAgency = ({ size = 24, className = '' }: IconProps) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <path d="M3 21H21" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <rect x="5" y="3" width="14" height="18" rx="1" stroke="currentColor" strokeWidth="1.5" fill="currentColor" fillOpacity="0.05" />
        <rect x="8" y="6" width="3" height="3" rx="0.5" fill="currentColor" fillOpacity="0.3" />
        <rect x="13" y="6" width="3" height="3" rx="0.5" fill="currentColor" fillOpacity="0.3" />
        <rect x="8" y="11" width="3" height="3" rx="0.5" fill="currentColor" fillOpacity="0.3" />
        <rect x="13" y="11" width="3" height="3" rx="0.5" fill="currentColor" fillOpacity="0.3" />
        <rect x="10" y="16" width="4" height="5" fill="currentColor" fillOpacity="0.2" />
    </svg>
)

// 📈 → Growth / Trending Up
export const IconGrowth = ({ size = 24, className = '' }: IconProps) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <path d="M3 17L9 11L13 15L21 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M15 7H21V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M3 17L9 11L13 15L21 7" stroke="currentColor" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" opacity="0.1" />
    </svg>
)

// ✨ → AI / Sparkles / Magic
export const IconMagic = ({ size = 24, className = '', animate = false }: IconProps) => (
    <motion.svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        className={className}
        animate={animate ? { rotate: [0, 10, -10, 0] } : undefined}
        transition={animate ? { duration: 3, repeat: Infinity } : undefined}
    >
        <path d="M12 2L13.5 8L20 8.5L14.5 12L16 19L12 14.5L8 19L9.5 12L4 8.5L10.5 8L12 2Z"
            fill="currentColor" fillOpacity="0.15" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
        <circle cx="19" cy="5" r="2" fill="currentColor" />
        <circle cx="5" cy="18" r="1.5" fill="currentColor" opacity="0.6" />
    </motion.svg>
)

// 🔥 → Hot / Active
export const IconActive = ({ size = 24, className = '' }: IconProps) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <path d="M12 22C16.4183 22 20 18.4183 20 14C20 10 17 7 15 5C15 8 13 10 12 10C11 10 9 8 9 5C7 7 4 10 4 14C4 18.4183 7.58172 22 12 22Z"
            fill="currentColor" fillOpacity="0.15" stroke="currentColor" strokeWidth="1.5" />
        <path d="M12 22C14.2091 22 16 19.5 16 17C16 14.5 14 13 12 12C10 13 8 14.5 8 17C8 19.5 9.79086 22 12 22Z"
            fill="currentColor" fillOpacity="0.3" />
    </svg>
)

// 🏆 → Winner / Trophy
export const IconWinner = ({ size = 24, className = '' }: IconProps) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <path d="M6 4H18V8C18 12.4183 14.4183 16 10 16H14C14 16 12 20 12 22" stroke="currentColor" strokeWidth="1.5" />
        <path d="M6 4C6 4 4 4 4 6C4 8 6 9 6 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M18 4C18 4 20 4 20 6C20 8 18 9 18 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M9 22H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path d="M12 8L12.5 10H14L13 11L13.5 13L12 12L10.5 13L11 11L10 10H11.5L12 8Z" fill="currentColor" />
    </svg>
)

// Export icon map for easy lookup
export const BRAND_ICONS = {
    launch: IconLaunch,
    target: IconTarget,
    content: IconContent,
    testing: IconTesting,
    tasks: IconTasks,
    results: IconResults,
    speed: IconSpeed,
    campaign: IconCampaign,
    agency: IconAgency,
    growth: IconGrowth,
    magic: IconMagic,
    active: IconActive,
    winner: IconWinner,
} as const

export type BrandIconName = keyof typeof BRAND_ICONS

// Helper component to render any brand icon by name
export const BrandIcon = ({
    name,
    size = 24,
    className = '',
    animate = false
}: {
    name: BrandIconName
    size?: number
    className?: string
    animate?: boolean
}) => {
    const Icon = BRAND_ICONS[name]
    return <Icon size={size} className={className} animate={animate} />
}
