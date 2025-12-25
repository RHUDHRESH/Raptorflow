'use client';

import React, { useEffect, useState, useRef } from 'react';
import { cn } from '@/lib/utils';
import { Check, Loader2, AlertCircle, ArrowRight } from 'lucide-react';
import { GenerationJob, getAssetConfig } from './types';
import Image from 'next/image';
import { motion } from 'motion/react';
import { gsap } from 'gsap';
import { AnimatedGradientBorder } from '@/components/ui/animated-gradient-border';
import { AnimatedProgressRing } from '@/components/ui/animated-progress-ring';

interface GenerationCardProps {
    job: GenerationJob;
    onClick?: () => void;
    className?: string;
}

const PHASE_MESSAGES = [
    'Understanding your request...',
    'Gathering brand context...',
    'Crafting the perfect asset...',
    'Adding finishing touches...',
    'Almost there...',
];

export function GenerationCard({ job, onClick, className }: GenerationCardProps) {
    const [phaseIndex, setPhaseIndex] = useState(0);
    const config = getAssetConfig(job.assetType);
    const cardRef = useRef<HTMLDivElement>(null);

    // Cycle through phase messages during generation
    useEffect(() => {
        if (job.status !== 'generating') return;

        const interval = setInterval(() => {
            setPhaseIndex(prev => (prev + 1) % PHASE_MESSAGES.length);
        }, 3000);

        return () => clearInterval(interval);
    }, [job.status]);

    // GSAP hover effects
    useEffect(() => {
        if (!cardRef.current) return;

        const card = cardRef.current;

        const handleMouseEnter = () => {
            gsap.to(card, {
                y: -2,
                duration: 0.3,
                ease: 'power2.out'
            });
        };

        const handleMouseLeave = () => {
            gsap.to(card, {
                y: 0,
                duration: 0.3,
                ease: 'power2.out'
            });
        };

        card.addEventListener('mouseenter', handleMouseEnter);
        card.addEventListener('mouseleave', handleMouseLeave);

        return () => {
            card.removeEventListener('mouseenter', handleMouseEnter);
            card.removeEventListener('mouseleave', handleMouseLeave);
        };
    }, []);

    const isComplete = job.status === 'complete';
    const isFailed = job.status === 'failed';
    const isGenerating = job.status === 'generating' || job.status === 'queued';

    return (
        <AnimatedGradientBorder
            active={isGenerating}
            variant={isFailed ? 'error' : isComplete ? 'success' : 'default'}
            className="w-full"
        >
            <motion.div
                ref={cardRef}
                onClick={isComplete ? onClick : undefined}
                className={cn(
                    'relative overflow-hidden rounded-xl border bg-card transition-all duration-300',
                    isComplete && 'cursor-pointer hover:shadow-lg hover:border-foreground/20',
                    isFailed && 'border-red-500/20',
                    className
                )}
                whileHover={{ scale: isComplete ? 1.02 : 1 }}
                whileTap={{ scale: isComplete ? 0.98 : 1 }}
            >
            {/* Enhanced Shimmer animation during generation */}
            {isGenerating && (
                <div className="absolute inset-0 overflow-hidden">
                    <motion.div
                        className="absolute inset-0 h-full w-full bg-gradient-to-r from-transparent via-foreground/5 to-transparent"
                        animate={{ x: ['-100%', '100%'] }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: 'linear'
                        }}
                    />
                </div>
            )}

            <div className="relative p-6 space-y-4">
                {/* Header with animated status icon */}
                <div className="flex items-start justify-between">
                    <div className="space-y-1">
                        <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
                            {config?.label || 'Asset'}
                        </p>
                        <p className="text-sm text-foreground/80 line-clamp-2">
                            {job.prompt}
                        </p>
                    </div>

                    {/* Enhanced Status icon */}
                    <motion.div
                        className={cn(
                            'flex items-center justify-center h-10 w-10 rounded-full',
                            isComplete && 'bg-foreground text-background',
                            isFailed && 'bg-red-500/10 text-red-500',
                            isGenerating && 'bg-muted'
                        )}
                        animate={{
                            rotate: isGenerating ? 360 : 0,
                            scale: isComplete ? [1, 1.1, 1] : 1
                        }}
                        transition={{
                            rotate: { duration: 2, repeat: isGenerating ? Infinity : 0, ease: 'linear' },
                            scale: { duration: 0.3, delay: isComplete ? 0.5 : 0 }
                        }}
                    >
                        {isComplete && <Check className="h-5 w-5" />}
                        {isFailed && <AlertCircle className="h-5 w-5" />}
                        {isGenerating && <Loader2 className="h-5 w-5 text-muted-foreground" />}
                    </motion.div>
                </div>

                {/* Enhanced Progress / Status */}
                <div className="space-y-2">
                    {isGenerating && (
                        <>
                            {/* Animated progress ring instead of linear bar */}
                            <div className="flex items-center justify-center py-2">
                                <AnimatedProgressRing
                                    progress={job.progress}
                                    size={32}
                                    strokeWidth={3}
                                    variant="default"
                                />
                            </div>
                            <motion.p
                                className="text-xs text-muted-foreground"
                                key={phaseIndex}
                                initial={{ opacity: 0, y: 5 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -5 }}
                            >
                                {PHASE_MESSAGES[phaseIndex]}
                            </motion.p>
                        </>
                    )}

                    {isComplete && (
                        <motion.div
                            className="flex items-center justify-between pt-2 border-t border-border/40"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.2 }}
                        >
                            <span className="text-xs text-muted-foreground">
                                Ready to edit
                            </span>
                            <motion.div
                                className="flex items-center gap-1 text-xs font-medium text-foreground"
                                whileHover={{ gap: 2 }}
                            >
                                Open <ArrowRight className="h-3 w-3" />
                            </motion.div>
                        </motion.div>
                    )}

                    {isFailed && (
                        <motion.p
                            className="text-xs text-red-500"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.3 }}
                        >
                            Generation failed. Click to retry.
                        </motion.p>
                    )}
                </div>
            </div>
        </motion.div>
        </AnimatedGradientBorder>
    );
}

// Compact version for queue display with animations
export function GenerationCardMini({ job, onClick }: GenerationCardProps) {
    const config = getAssetConfig(job.assetType);
    const isComplete = job.status === 'complete';
    const isGenerating = job.status === 'generating' || job.status === 'queued';
    const miniRef = useRef<HTMLDivElement>(null);

    return (
        <motion.div
            ref={miniRef}
            onClick={isComplete ? onClick : undefined}
            className={cn(
                'relative flex items-center gap-3 p-3 rounded-lg border bg-card transition-all duration-200',
                isComplete && 'cursor-pointer'
            )}
            whileHover={{ scale: isComplete ? 1.02 : 1, backgroundColor: isComplete ? 'rgba(0,0,0,0.02)' : 'transparent' }}
            whileTap={{ scale: isComplete ? 0.98 : 1 }}
        >
            {/* Enhanced Status indicator */}
            <motion.div
                className={cn(
                    'h-2 w-2 rounded-full shrink-0',
                    isComplete && 'bg-foreground',
                    isGenerating && 'bg-amber-500',
                    job.status === 'failed' && 'bg-red-500'
                )}
                animate={{
                    scale: isGenerating ? [1, 1.5, 1] : 1,
                    opacity: isGenerating ? [1, 0.6, 1] : 1
                }}
                transition={{
                    duration: 1,
                    repeat: isGenerating ? Infinity : 0
                }}
            />

            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{config?.label}</p>
                <p className="text-xs text-muted-foreground truncate">{job.prompt}</p>
            </div>

            {isGenerating && (
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                    <Loader2 className="h-4 w-4 text-muted-foreground shrink-0" />
                </motion.div>
            )}
            {isComplete && (
                <motion.div
                    initial={{ x: -10, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.1 }}
                >
                    <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
                </motion.div>
            )}
        </motion.div>
    );
}
