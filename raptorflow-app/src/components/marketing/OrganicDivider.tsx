'use client';

import { cn } from '@/lib/utils';

interface OrganicDividerProps {
    variant?: 'wave' | 'drip' | 'curve' | 'peak';
    fromColor?: string;
    toColor?: string;
    className?: string;
    flip?: boolean;
}

export function OrganicDivider({
    variant = 'wave',
    fromColor = 'var(--color-canvas)',
    toColor = 'var(--color-surface)',
    className,
    flip = false,
}: OrganicDividerProps) {
    const paths = {
        wave: 'M0,50 C200,100 400,0 600,50 C800,100 1000,0 1200,50 L1200,100 L0,100 Z',
        drip: 'M0,0 L0,40 Q150,100 300,40 Q450,0 600,40 Q750,100 900,40 Q1050,0 1200,40 L1200,0 Z',
        curve: 'M0,100 Q300,0 600,50 Q900,100 1200,0 L1200,100 L0,100 Z',
        peak: 'M0,100 L400,100 L600,20 L800,100 L1200,100 L1200,100 L0,100 Z',
    };

    return (
        <div
            className={cn(
                'relative w-full overflow-hidden pointer-events-none',
                flip && 'rotate-180',
                className
            )}
            style={{ marginTop: '-1px', marginBottom: '-1px' }}
        >
            <svg
                viewBox="0 0 1200 100"
                preserveAspectRatio="none"
                className="w-full h-16 md:h-24 lg:h-32"
                style={{ display: 'block' }}
            >
                <defs>
                    <linearGradient id={`divider-gradient-${variant}`} x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor={fromColor} />
                        <stop offset="100%" stopColor={toColor} />
                    </linearGradient>
                </defs>
                <path
                    d={paths[variant]}
                    fill={toColor}
                    className="transition-colors duration-500"
                />
            </svg>
        </div>
    );
}

// Animated version with SVG morphing
export function AnimatedOrganicDivider({
    className,
    color = 'currentColor',
}: {
    className?: string;
    color?: string;
}) {
    return (
        <div className={cn('relative w-full overflow-hidden', className)}>
            <svg
                viewBox="0 0 1200 120"
                preserveAspectRatio="none"
                className="w-full h-20 md:h-28"
            >
                <path
                    fill={color}
                    d="M0,0 V46.29 C150,80 300,90 450,80 C600,70 750,50 900,60 C1050,70 1150,90 1200,100 L1200,0 Z"
                    className="animate-pulse"
                    style={{ animationDuration: '4s' }}
                />
            </svg>
        </div>
    );
}

// Multiple wave layers for depth
export function LayeredWaveDivider({
    className,
    baseColor = 'hsl(var(--muted))',
}: {
    className?: string;
    baseColor?: string;
}) {
    return (
        <div className={cn('relative w-full h-24 md:h-32 overflow-hidden', className)}>
            {/* Back layer */}
            <svg
                viewBox="0 0 1200 120"
                preserveAspectRatio="none"
                className="absolute bottom-0 w-full h-full opacity-30"
            >
                <path
                    fill={baseColor}
                    d="M0,60 C300,120 600,0 900,60 C1050,90 1150,80 1200,60 L1200,120 L0,120 Z"
                />
            </svg>
            {/* Middle layer */}
            <svg
                viewBox="0 0 1200 120"
                preserveAspectRatio="none"
                className="absolute bottom-0 w-full h-full opacity-60"
                style={{ transform: 'translateX(-10%)' }}
            >
                <path
                    fill={baseColor}
                    d="M0,80 C200,40 400,100 600,60 C800,20 1000,80 1200,40 L1200,120 L0,120 Z"
                />
            </svg>
            {/* Front layer */}
            <svg
                viewBox="0 0 1200 120"
                preserveAspectRatio="none"
                className="absolute bottom-0 w-full h-full"
            >
                <path
                    fill={baseColor}
                    d="M0,40 C200,100 400,20 600,60 C800,100 1000,40 1200,80 L1200,120 L0,120 Z"
                />
            </svg>
        </div>
    );
}
