import React from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

// ═══════════════════════════════════════════════════════════════════════════════
// RAPTORFLOW LOGO COMPONENT
// Ultra-simple iconic logo - passes the "kid draw test"
// Just two angular strokes forming an abstract R/flow symbol
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
            {/* ICONIC MARK - Ultra simple: Two strokes forming abstract R/flow */}
            <motion.svg
                width={icon}
                height={icon}
                viewBox="0 0 48 48"
                fill="none"
                className="flex-shrink-0"
                whileHover={animated ? { rotate: -5 } : undefined}
                transition={{ type: "spring", stiffness: 300 }}
            >
                {/* Background - Pure black square with rounded corners */}
                <rect width="48" height="48" rx="12" fill="#000000" />

                {/* THE MARK - Just two bold strokes
                    Stroke 1: Vertical line on left (the "R" stem)
                    Stroke 2: Angular kick from middle to bottom-right (the "flow")
                    Together: Abstract R with forward momentum
                    A kid can draw: one line down, one diagonal line */}

                {/* Stem - vertical line */}
                <path
                    d="M16 10 L16 38"
                    stroke="#FFFFFF"
                    strokeWidth="6"
                    strokeLinecap="round"
                />

                {/* Flow - angular kick creating momentum */}
                <path
                    d="M16 24 L32 10 M16 24 L36 38"
                    stroke="#FFFFFF"
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                />
            </motion.svg>

            {/* Wordmark - Clean and simple */}
            {showText && (
                <div className="leading-none">
                    <span className={`font-serif font-bold tracking-tight text-foreground ${text}`}>
                        Raptor<span className="font-normal text-zinc-400">Flow</span>
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

// Simple icon-only version - THE iconic mark
export const RaptorFlowIcon = ({ size = 32 }: { size?: number }) => (
    <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
    >
        <rect width="48" height="48" rx="12" fill="#000000" />
        <path d="M16 10 L16 38" stroke="#FFFFFF" strokeWidth="6" strokeLinecap="round" />
        <path d="M16 24 L32 10 M16 24 L36 38" stroke="#FFFFFF" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
)

export default RaptorFlowLogo
