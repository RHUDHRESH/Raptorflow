'use client';

import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { X, Copy, Check, ArrowLeftRight, Sparkles, Crown } from 'lucide-react';

interface SplitEditorProps {
    initialContentA?: string;
    initialContentB?: string;
    title?: string;
    onSave?: (content: string) => void;
    onClose?: () => void;
    className?: string;
}

interface ComparisonResult {
    winner: 'A' | 'B' | 'tie';
    scoreA: number;
    scoreB: number;
    reasoning: string;
}

// Mock AI comparison - would call backend in production
function compareVersions(a: string, b: string): ComparisonResult {
    const scoreA = 50 + Math.random() * 40;
    const scoreB = 50 + Math.random() * 40;

    let winner: 'A' | 'B' | 'tie' = 'tie';
    let reasoning = 'Both versions are equally effective.';

    if (Math.abs(scoreA - scoreB) > 10) {
        winner = scoreA > scoreB ? 'A' : 'B';
        reasoning = winner === 'A'
            ? 'Version A has stronger hooks and clearer messaging.'
            : 'Version B is more concise and action-oriented.';
    }

    return {
        winner,
        scoreA: Math.round(scoreA),
        scoreB: Math.round(scoreB),
        reasoning,
    };
}

export function SplitEditor({
    initialContentA = '',
    initialContentB = '',
    title = 'A/B Comparison',
    onSave,
    onClose,
    className,
}: SplitEditorProps) {
    const [contentA, setContentA] = useState(initialContentA);
    const [contentB, setContentB] = useState(initialContentB);
    const [comparison, setComparison] = useState<ComparisonResult | null>(null);
    const [isComparing, setIsComparing] = useState(false);
    const [selectedVersion, setSelectedVersion] = useState<'A' | 'B' | null>(null);

    const handleCompare = useCallback(async () => {
        setIsComparing(true);
        // Simulate AI call
        await new Promise(r => setTimeout(r, 1500));
        const result = compareVersions(contentA, contentB);
        setComparison(result);
        setIsComparing(false);
    }, [contentA, contentB]);

    const handlePickWinner = useCallback((version: 'A' | 'B') => {
        setSelectedVersion(version);
        const content = version === 'A' ? contentA : contentB;
        onSave?.(content);
    }, [contentA, contentB, onSave]);

    const handleCopyToB = useCallback(() => {
        setContentB(contentA);
    }, [contentA]);

    const handleCopyToA = useCallback(() => {
        setContentA(contentB);
    }, [contentB]);

    const handleSwap = useCallback(() => {
        const temp = contentA;
        setContentA(contentB);
        setContentB(temp);
    }, [contentA, contentB]);

    return (
        <div className={cn('flex flex-col h-full bg-background', className)}>
            {/* Header */}
            <div className="flex items-center justify-between h-14 px-6 border-b border-border/40">
                <div className="flex items-center gap-3">
                    <ArrowLeftRight className="h-5 w-5 text-muted-foreground" />
                    <h2 className="font-medium">{title}</h2>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleSwap}
                        className={cn(
                            'flex items-center gap-2 h-8 px-3 rounded-lg',
                            'border border-border/60 bg-card',
                            'text-sm hover:bg-muted/30 transition-colors'
                        )}
                    >
                        <ArrowLeftRight className="h-3.5 w-3.5" />
                        Swap
                    </button>
                    <button
                        onClick={handleCompare}
                        disabled={isComparing || !contentA.trim() || !contentB.trim()}
                        className={cn(
                            'flex items-center gap-2 h-8 px-4 rounded-lg',
                            'bg-foreground text-background',
                            'text-sm font-medium',
                            'hover:opacity-90 transition-opacity',
                            'disabled:opacity-40 disabled:cursor-not-allowed'
                        )}
                    >
                        {isComparing ? (
                            <>
                                <span className="h-3 w-3 border-2 border-background/30 border-t-background rounded-full animate-spin" />
                                Comparing...
                            </>
                        ) : (
                            <>
                                <Sparkles className="h-3.5 w-3.5" />
                                Compare
                            </>
                        )}
                    </button>
                    {onClose && (
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-muted rounded-lg transition-colors"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    )}
                </div>
            </div>

            {/* Comparison result banner */}
            {comparison && (
                <div className={cn(
                    'flex items-center justify-between px-6 py-3',
                    'bg-muted/30 border-b border-border/40'
                )}>
                    <div className="flex items-center gap-3">
                        <Crown className={cn(
                            'h-5 w-5',
                            comparison.winner === 'A' && 'text-amber-500',
                            comparison.winner === 'B' && 'text-amber-500',
                            comparison.winner === 'tie' && 'text-muted-foreground'
                        )} />
                        <span className="text-sm">
                            {comparison.winner === 'tie'
                                ? 'It\'s a tie!'
                                : `Version ${comparison.winner} wins`}
                            {' — '}
                            <span className="text-muted-foreground">{comparison.reasoning}</span>
                        </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                        <span>A: <strong>{comparison.scoreA}</strong>/100</span>
                        <span>B: <strong>{comparison.scoreB}</strong>/100</span>
                    </div>
                </div>
            )}

            {/* Split editors */}
            <div className="flex-1 flex overflow-hidden">
                {/* Version A */}
                <div className="flex-1 flex flex-col border-r border-border/40">
                    <div className="flex items-center justify-between px-4 py-2 bg-muted/20 border-b border-border/40">
                        <div className="flex items-center gap-2">
                            <span className={cn(
                                'h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold',
                                comparison?.winner === 'A' ? 'bg-amber-500 text-white' : 'bg-muted text-muted-foreground',
                                selectedVersion === 'A' && 'ring-2 ring-green-500'
                            )}>
                                A
                            </span>
                            <span className="text-sm font-medium">Version A</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <button
                                onClick={handleCopyToB}
                                className="p-1.5 hover:bg-muted rounded-md transition-colors"
                                title="Copy to B"
                            >
                                <Copy className="h-3.5 w-3.5" />
                            </button>
                            <button
                                onClick={() => handlePickWinner('A')}
                                className={cn(
                                    'flex items-center gap-1 px-2 py-1 rounded-md text-xs',
                                    'hover:bg-green-500/10 text-green-600 transition-colors'
                                )}
                            >
                                <Check className="h-3 w-3" />
                                Pick A
                            </button>
                        </div>
                    </div>
                    <textarea
                        value={contentA}
                        onChange={(e) => setContentA(e.target.value)}
                        placeholder="Write version A..."
                        className={cn(
                            'flex-1 w-full resize-none p-4',
                            'bg-transparent border-none outline-none',
                            'text-sm leading-relaxed placeholder:text-muted-foreground/40'
                        )}
                    />
                </div>

                {/* Version B */}
                <div className="flex-1 flex flex-col">
                    <div className="flex items-center justify-between px-4 py-2 bg-muted/20 border-b border-border/40">
                        <div className="flex items-center gap-2">
                            <span className={cn(
                                'h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold',
                                comparison?.winner === 'B' ? 'bg-amber-500 text-white' : 'bg-muted text-muted-foreground',
                                selectedVersion === 'B' && 'ring-2 ring-green-500'
                            )}>
                                B
                            </span>
                            <span className="text-sm font-medium">Version B</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <button
                                onClick={handleCopyToA}
                                className="p-1.5 hover:bg-muted rounded-md transition-colors"
                                title="Copy to A"
                            >
                                <Copy className="h-3.5 w-3.5" />
                            </button>
                            <button
                                onClick={() => handlePickWinner('B')}
                                className={cn(
                                    'flex items-center gap-1 px-2 py-1 rounded-md text-xs',
                                    'hover:bg-green-500/10 text-green-600 transition-colors'
                                )}
                            >
                                <Check className="h-3 w-3" />
                                Pick B
                            </button>
                        </div>
                    </div>
                    <textarea
                        value={contentB}
                        onChange={(e) => setContentB(e.target.value)}
                        placeholder="Write version B..."
                        className={cn(
                            'flex-1 w-full resize-none p-4',
                            'bg-transparent border-none outline-none',
                            'text-sm leading-relaxed placeholder:text-muted-foreground/40'
                        )}
                    />
                </div>
            </div>

            {/* Footer hints */}
            <div className="px-6 py-3 border-t border-border/40 bg-muted/10">
                <p className="text-xs text-muted-foreground text-center">
                    Write two versions, click Compare to see which performs better, then Pick your winner.
                </p>
            </div>
        </div>
    );
}
