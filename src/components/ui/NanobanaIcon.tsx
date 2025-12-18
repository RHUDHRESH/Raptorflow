import React from 'react'
import { cn } from '@/lib/utils'
import { LucideIcon } from 'lucide-react'

interface NanobanaIconProps {
    icon: LucideIcon
    className?: string
    color?: string
    glowColor?: string
    size?: number | string
}

export const NanobanaIcon: React.FC<NanobanaIconProps> = ({
    icon: Icon,
    className,
    color = 'currentColor',
    glowColor,
    size = 24
}) => {
    // If glowColor is not provided, we can infer it or use a default neon
    const glow = glowColor || (color === 'currentColor' ? 'rgba(0, 240, 255, 0.5)' : color)

    return (
        <div className="relative inline-flex items-center justify-center">
            {/* Glow Layer */}
            <Icon
                size={size}
                className={cn("absolute blur-sm opacity-50", className)}
                style={{ color: glow }}
            />
            {/* Main Icon Layer */}
            <Icon
                size={size}
                className={cn("relative z-10", className)}
                style={{ color: color }}
            />
        </div>
    )
}
