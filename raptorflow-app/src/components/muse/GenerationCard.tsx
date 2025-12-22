'use client';

import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { Check, Loader2, AlertCircle, ArrowRight } from 'lucide-react';
import { GenerationJob, getAssetConfig } from './types';
import Image from 'next/image';

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

    // Cycle through phase messages during generation
    useEffect(() => {
        if (job.status !== 'generating') return;

        const interval = setInterval(() => {
            setPhaseIndex(prev => (prev + 1) % PHASE_MESSAGES.length);
        }, 3000);

        return () => clearInterval(interval);
    }, [job.status]);

    const isComplete = job.status === 'complete';
    const isFailed = job.status === 'failed';
    const isGenerating = job.status === 'generating' || job.status === 'queued';

    return (
        <div
            onClick={isComplete ? onClick : undefined}
            className={cn(
                'relative overflow-hidden rounded-xl border bg-card transition-all duration-300',
                isComplete && 'cursor-pointer hover:shadow-lg hover:border-foreground/20 hover:-translate-y-0.5',
                isFailed && 'border-red-500/20',
                className
            )}
        >
            {/* Shimmer animation during generation */}
            {isGenerating && (
                <div className="absolute inset-0 overflow-hidden">
                    <div
                        className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-foreground/5 to-transparent"
                        style={{ animationDuration: '2s', animationIterationCount: 'infinite' }}
                    />
                </div>
            )}

            <div className="relative p-6 space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between">
                    <div className="space-y-1">
                        <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
                            {config?.label || 'Asset'}
                        </p>
                        <p className="text-sm text-foreground/80 line-clamp-2">
                            {job.prompt}
                        </p>
                    </div>

                    {/* Status icon */}
                    <div className={cn(
                        'flex items-center justify-center h-10 w-10 rounded-full',
                        isComplete && 'bg-foreground text-background',
                        isFailed && 'bg-red-500/10 text-red-500',
                        isGenerating && 'bg-muted'
                    )}>
                        {isComplete && <Check className="h-5 w-5" />}
                        {isFailed && <AlertCircle className="h-5 w-5" />}
                        {isGenerating && <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />}
                    </div>
                </div>

                {/* Progress / Status */}
                <div className="space-y-2">
                    {isGenerating && (
                        <>
                            {/* Abstract progress bar */}
                            <div className="h-1 w-full bg-border/30 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-foreground/60 rounded-full transition-all duration-1000 ease-out"
                                    style={{ width: `${job.progress}%` }}
                                />
                            </div>
                            <p className="text-xs text-muted-foreground animate-pulse">
                                {PHASE_MESSAGES[phaseIndex]}
                            </p>
                        </>
                    )}

                    {isComplete && (
                        <div className="flex items-center justify-between pt-2 border-t border-border/40">
                            <span className="text-xs text-muted-foreground">
                                Ready to edit
                            </span>
                            <div className="flex items-center gap-1 text-xs font-medium text-foreground group-hover:gap-2 transition-all">
                                Open <ArrowRight className="h-3 w-3" />
                            </div>
                        </div>
                    )}

                    {isFailed && (
                        <p className="text-xs text-red-500">
                            Generation failed. Click to retry.
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}

// Compact version for queue display
export function GenerationCardMini({ job, onClick }: GenerationCardProps) {
    const config = getAssetConfig(job.assetType);
    const isComplete = job.status === 'complete';
    const isGenerating = job.status === 'generating' || job.status === 'queued';

    return (
        <div
            onClick={isComplete ? onClick : undefined}
            className={cn(
                'relative flex items-center gap-3 p-3 rounded-lg border bg-card transition-all duration-200',
                isComplete && 'cursor-pointer hover:bg-muted/30'
            )}
        >
            {/* Status indicator */}
            <div className={cn(
                'h-2 w-2 rounded-full shrink-0',
                isComplete && 'bg-foreground',
                isGenerating && 'bg-amber-500 animate-pulse',
                job.status === 'failed' && 'bg-red-500'
            )} />

            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{config?.label}</p>
                <p className="text-xs text-muted-foreground truncate">{job.prompt}</p>
            </div>

            {isGenerating && (
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground shrink-0" />
            )}
            {isComplete && (
                <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
            )}
        </div>
    );
}
