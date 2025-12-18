import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface NanobanaBackgroundProps {
    className?: string
    intensity?: 'low' | 'medium' | 'high'
    variant?: 'void' | 'nebula' | 'grid'
}

export const NanobanaBackground: React.FC<NanobanaBackgroundProps> = ({
    className,
    intensity = 'medium',
    variant = 'void'
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null)

    useEffect(() => {
        // Optional: Add simple canvas stardust effect here later if needed
        // For now, we rely on CSS layers for maximum performance and consistent design
    }, [])

    return (
        <div className={cn("fixed inset-0 -z-50 overflow-hidden pointer-events-none bg-background", className)}>

            {/* Layer 1: The Grid (Foundation) */}
            <div
                className="absolute inset-0 opacity-[0.03]"
                style={{
                    backgroundImage: `linear-gradient(to right, hsl(var(--foreground) / 0.12) 1px, transparent 1px),
                            linear-gradient(to bottom, hsl(var(--foreground) / 0.12) 1px, transparent 1px)`,
                    backgroundSize: '40px 40px'
                }}
            />

            {/* Layer 2: The Void Breath (Ambient Gradients) */}
            {variant === 'nebula' && (
                <>
                    <motion.div
                        animate={{
                            scale: [1, 1.2, 1],
                            opacity: [0.1, 0.2, 0.1],
                            rotate: [0, 90, 0]
                        }}
                        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                        className="absolute -top-[20%] -left-[10%] w-[50vw] h-[50vw] rounded-full bg-primary/20 blur-[120px]"
                    />
                    <motion.div
                        animate={{
                            scale: [1.2, 1, 1.2],
                            opacity: [0.1, 0.15, 0.1],
                            x: [0, 100, 0]
                        }}
                        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
                        className="absolute top-[40%] -right-[10%] w-[40vw] h-[40vw] rounded-full bg-accent/10 blur-[100px]"
                    />
                </>
            )}

            {variant === 'void' && (
                <div
                    className="absolute inset-0"
                    style={{
                        backgroundImage:
                            'linear-gradient(to bottom, transparent, hsl(var(--background) / 0.55), hsl(var(--background)))',
                    }}
                />
            )}

            {/* Layer 3: Noise (Texture) */}
            <div className="absolute inset-0 opacity-[0.015] bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />

        </div>
    )
}
