'use client';

import React from 'react';
import { motion } from 'motion/react';
import { cn } from '@/lib/utils';

interface AnimatedProgressRingProps {
    progress: number;
    size?: number;
    strokeWidth?: number;
    className?: string;
    variant?: 'default' | 'success' | 'error';
}

export function AnimatedProgressRing({
    progress,
    size = 40,
    strokeWidth = 3,
    className = '',
    variant = 'default'
}: AnimatedProgressRingProps) {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const strokeDashoffset = circumference - (progress / 100) * circumference;

    const colors = {
        default: 'stroke-foreground/60',
        success: 'stroke-green-500',
        error: 'stroke-red-500'
    };

    return (
        <div className={cn('relative inline-flex', className)}>
            <svg
                width={size}
                height={size}
                className="transform -rotate-90"
            >
                {/* Background circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    fill="none"
                    className="text-border/30"
                />
                {/* Progress circle */}
                <motion.circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    fill="none"
                    className={colors[variant]}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    strokeLinecap="round"
                />
            </svg>
            {progress > 0 && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                    className="absolute inset-0 flex items-center justify-center"
                >
                    <span className="text-xs font-medium">
                        {Math.round(progress)}%
                    </span>
                </motion.div>
            )}
        </div>
    );
}
