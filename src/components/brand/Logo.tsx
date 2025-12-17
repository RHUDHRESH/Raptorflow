import React from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

// ═══════════════════════════════════════════════════════════════════════════════
// RAPTORFLOW LOGO COMPONENT
// Premium logo with styled R lettermark and claw accent
// ═══════════════════════════════════════════════════════════════════════════════

interface LogoProps {
    size?: 'sm' | 'md' | 'lg' | 'xl'
    showText?: boolean
    animated?: boolean
    className?: string
    linkTo?: string
}

const sizeMap = {
    sm: { icon: 28, text: 'text-sm' },
    md: { icon: 36, text: 'text-base' },
    lg: { icon: 44, text: 'text-xl' },
    xl: { icon: 56, text: 'text-2xl' }
}

export const RaptorFlowLogo = ({
    size = 'md',
    showText = true,
    animated = true,
    className = '',
    linkTo = '/'
}: LogoProps) => {
    const { icon, text } = sizeMap[size]

    const LogoContent = (
        <motion.div
            className={`flex items-center gap-3 ${className}`}
            whileHover={animated ? { scale: 1.02 } : undefined}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
        >
            {/* Icon Mark - Amber square with R and claw marks */}
            <motion.svg
                width={icon}
                height={icon}
                viewBox="0 0 48 48"
                fill="none"
                className="flex-shrink-0"
                whileHover={animated ? { rotate: 3 } : undefined}
                transition={{ type: "spring", stiffness: 300 }}
            >
                {/* Background */}
                <rect width="48" height="48" rx="10" fill="hsl(var(--primary))" />

                {/* Stylized R */}
                <path
                    d="M14 12V36"
                    stroke="hsl(var(--primary-foreground))"
                    strokeWidth="4"
                    strokeLinecap="round"
                />
                <path
                    d="M14 12H26C30.418 12 34 15.134 34 19C34 22.866 30.418 26 26 26H14"
                    stroke="hsl(var(--primary-foreground))"
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    fill="none"
                />
                <path
                    d="M24 26L34 38"
                    stroke="hsl(var(--primary-foreground))"
                    strokeWidth="4"
                    strokeLinecap="round"
                />

                {/* Claw accent marks - top right */}
                <motion.path
                    d="M32 6L42 16"
                    stroke="hsl(var(--primary-foreground))"
                    strokeWidth="2"
                    strokeLinecap="round"
                    opacity="0.6"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ delay: 0.3, duration: 0.4 }}
                />
                <motion.path
                    d="M36 4L44 12"
                    stroke="hsl(var(--primary-foreground))"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    opacity="0.4"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ delay: 0.4, duration: 0.3 }}
                />
            </motion.svg>

            {/* Wordmark */}
            {showText && (
                <div className="leading-none">
                    <span className={`font-serif font-semibold tracking-tight ${text}`}>
                        Raptor<span className="text-primary">Flow</span>
                    </span>
                </div>
            )}
        </motion.div>
    )

    if (linkTo) {
        return (
            <Link to={linkTo} className="inline-block">
                {LogoContent}
            </Link>
        )
    }

    return LogoContent
}

// Simple icon-only version for favicon usage
export const RaptorFlowIcon = ({ size = 32 }: { size?: number }) => (
    <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
    >
        <rect width="48" height="48" rx="10" fill="#F59E0B" />
        <path d="M14 12V36" stroke="#0A0A0A" strokeWidth="4" strokeLinecap="round" />
        <path d="M14 12H26C30.418 12 34 15.134 34 19C34 22.866 30.418 26 26 26H14" stroke="#0A0A0A" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
        <path d="M24 26L34 38" stroke="#0A0A0A" strokeWidth="4" strokeLinecap="round" />
        <path d="M32 6L42 16" stroke="#0A0A0A" strokeWidth="2" strokeLinecap="round" opacity="0.6" />
        <path d="M36 4L44 12" stroke="#0A0A0A" strokeWidth="1.5" strokeLinecap="round" opacity="0.4" />
    </svg>
)

export default RaptorFlowLogo
