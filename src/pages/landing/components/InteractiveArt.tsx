import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface InteractiveArtProps {
    type?: 'orbit' | 'diamond' | 'wave' | 'target' | 'spiral' | 'grid' | 'burst' | 'flow'
    size?: number
    position?: { x: string, y: string }
    delay?: number
    className?: string
}

export const InteractiveArt = ({
    type = 'orbit',
    size = 60,
    position = { x: '10%', y: '20%' },
    delay = 0,
    className
}: InteractiveArtProps) => {
    const [isClicked, setIsClicked] = useState(false)
    const [isHovered, setIsHovered] = useState(false)

    const handleClick = () => {
        setIsClicked(true)
        setTimeout(() => setIsClicked(false), 600)
    }

    const artPaths: Record<string, React.ReactNode> = {
        orbit: (
            <>
                <circle cx="40" cy="40" r="25" strokeDasharray="4 4" />
                <circle cx="40" cy="40" r="15" strokeDasharray="2 3" />
                <circle cx="40" cy="15" r="4" fill="currentColor" fillOpacity="0.3" />
                <circle cx="65" cy="40" r="3" />
            </>
        ),
        diamond: (
            <>
                <path d="M40 10 L70 40 L40 70 L10 40 Z" strokeDasharray="6 3" />
                <path d="M40 20 L60 40 L40 60 L20 40 Z" />
                <circle cx="40" cy="40" r="5" fill="currentColor" fillOpacity="0.2" />
            </>
        ),
        wave: (
            <>
                <path d="M10 40 Q25 20 40 40 Q55 60 70 40" strokeWidth="2" />
                <path d="M10 50 Q25 30 40 50 Q55 70 70 50" strokeDasharray="4 4" />
                <circle cx="40" cy="40" r="3" fill="currentColor" />
            </>
        ),
        target: (
            <>
                <circle cx="40" cy="40" r="30" strokeDasharray="8 4" />
                <circle cx="40" cy="40" r="20" />
                <circle cx="40" cy="40" r="10" strokeDasharray="3 3" />
                <circle cx="40" cy="40" r="3" fill="currentColor" />
            </>
        ),
        spiral: (
            <>
                <path d="M40 40 Q50 30 50 40 Q50 50 40 50 Q30 50 30 40 Q30 30 40 30 Q55 30 55 45 Q55 60 40 60" strokeDasharray="4 2" />
                <circle cx="40" cy="40" r="5" />
            </>
        ),
        grid: (
            <>
                <path d="M20 20 L60 20 M20 40 L60 40 M20 60 L60 60" strokeDasharray="4 4" />
                <path d="M20 20 L20 60 M40 20 L40 60 M60 20 L60 60" strokeDasharray="4 4" />
                <circle cx="40" cy="40" r="4" fill="currentColor" fillOpacity="0.3" />
            </>
        ),
        burst: (
            <>
                <path d="M40 15 L40 25 M40 55 L40 65 M65 40 L55 40 M25 40 L15 40" strokeWidth="2" />
                <path d="M55 25 L50 30 M50 50 L55 55 M30 50 L25 55 M25 25 L30 30" />
                <circle cx="40" cy="40" r="8" fill="currentColor" fillOpacity="0.2" />
            </>
        ),
        flow: (
            <>
                <path d="M15 50 Q30 30 45 50 Q60 70 75 50" strokeWidth="1.5" />
                <path d="M15 40 Q30 20 45 40 Q60 60 75 40" strokeDasharray="5 3" />
                <circle cx="45" cy="45" r="4" fill="currentColor" fillOpacity="0.3" />
            </>
        )
    }

    return (
        <motion.div
            className={cn("absolute pointer-events-auto cursor-pointer select-none z-0", className)}
            style={{ left: position.x, top: position.y }}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay, duration: 0.5, type: "spring" }}
            onClick={handleClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* Particle burst on click */}
            {isClicked && (
                <>
                    {[...Array(6)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="absolute w-2 h-2 rounded-full bg-primary/40"
                            style={{ left: size / 2, top: size / 2 }}
                            initial={{ scale: 0, x: 0, y: 0 }}
                            animate={{
                                scale: [1, 0],
                                x: Math.cos((i * 60) * Math.PI / 180) * 40,
                                y: Math.sin((i * 60) * Math.PI / 180) * 40,
                            }}
                            transition={{ duration: 0.5, ease: "easeOut" }}
                        />
                    ))}
                </>
            )}

            <motion.svg
                width={size}
                height={size}
                viewBox="0 0 80 80"
                fill="none"
                stroke="currentColor"
                strokeWidth="1"
                className="text-muted-foreground/30"
                animate={{
                    rotate: isHovered ? [0, 10, -10, 0] : 0,
                    scale: isClicked ? [1, 1.3, 1] : isHovered ? 1.15 : 1,
                }}
                transition={{
                    type: "spring",
                    stiffness: 300,
                    damping: 15,
                    rotate: { duration: 0.3 }
                }}
                whileTap={{ scale: 0.9 }}
            >
                <motion.g
                    animate={{
                        y: [0, -3, 0],
                        rotate: [0, 2, -2, 0]
                    }}
                    transition={{
                        duration: 4 + delay,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                >
                    {artPaths[type]}
                </motion.g>
            </motion.svg>
        </motion.div>
    )
}

