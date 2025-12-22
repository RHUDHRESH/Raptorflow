'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Check, Copy, Sparkles, ChevronLeft, ChevronRight, Shuffle } from 'lucide-react';

interface Variant {
    id: string;
    content: string;
    score?: number;
}

interface VariantSelectorProps {
    variants: Variant[];
    selectedId?: string;
    onSelect?: (variant: Variant) => void;
    onRegenerate?: () => void;
    className?: string;
}

export function VariantSelector({
    variants,
    selectedId,
    onSelect,
    onRegenerate,
    className,
}: VariantSelectorProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [copiedId, setCopiedId] = useState<string | null>(null);

    const currentVariant = variants[currentIndex];

    const handlePrev = () => {
        setCurrentIndex(i => i > 0 ? i - 1 : variants.length - 1);
    };

    const handleNext = () => {
        setCurrentIndex(i => i < variants.length - 1 ? i + 1 : 0);
    };

    const handleCopy = async (variant: Variant) => {
        await navigator.clipboard.writeText(variant.content);
        setCopiedId(variant.id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    if (variants.length === 0) {
        return null;
    }

    return (
        <div className={cn('space-y-4', className)}>
            {/* Header with navigation */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">
                        {variants.length} Variant{variants.length > 1 ? 's' : ''}
                    </span>
                </div>

                <div className="flex items-center gap-1">
                    <button
                        onClick={handlePrev}
                        className={cn(
                            'h-7 w-7 rounded-lg flex items-center justify-center',
                            'hover:bg-muted transition-colors',
                            'disabled:opacity-40'
                        )}
                        disabled={variants.length <= 1}
                    >
                        <ChevronLeft className="h-4 w-4" />
                    </button>
                    <span className="text-xs text-muted-foreground px-2">
                        {currentIndex + 1} / {variants.length}
                    </span>
                    <button
                        onClick={handleNext}
                        className={cn(
                            'h-7 w-7 rounded-lg flex items-center justify-center',
                            'hover:bg-muted transition-colors',
                            'disabled:opacity-40'
                        )}
                        disabled={variants.length <= 1}
                    >
                        <ChevronRight className="h-4 w-4" />
                    </button>
                </div>
            </div>

            {/* Variant content */}
            <div className={cn(
                'relative p-4 rounded-xl',
                'border border-border/60 bg-card',
                selectedId === currentVariant.id && 'border-foreground/30 bg-foreground/5'
            )}>
                {/* Score badge */}
                {currentVariant.score !== undefined && (
                    <div className={cn(
                        'absolute -top-2 -right-2',
                        'px-2 py-0.5 rounded-full text-xs font-bold',
                        currentVariant.score >= 70 && 'bg-green-500 text-white',
                        currentVariant.score >= 40 && currentVariant.score < 70 && 'bg-amber-500 text-white',
                        currentVariant.score < 40 && 'bg-red-500 text-white'
                    )}>
                        {currentVariant.score}
                    </div>
                )}

                <p className="text-sm leading-relaxed whitespace-pre-line">
                    {currentVariant.content}
                </p>

                {/* Actions */}
                <div className="flex items-center gap-2 mt-4 pt-3 border-t border-border/40">
                    <button
                        onClick={() => onSelect?.(currentVariant)}
                        className={cn(
                            'flex items-center gap-1.5 h-8 px-3 rounded-lg',
                            'text-xs font-medium transition-all',
                            selectedId === currentVariant.id
                                ? 'bg-green-500 text-white'
                                : 'bg-foreground text-background hover:opacity-90'
                        )}
                    >
                        {selectedId === currentVariant.id ? (
                            <>
                                <Check className="h-3 w-3" />
                                Selected
                            </>
                        ) : (
                            'Use This'
                        )}
                    </button>

                    <button
                        onClick={() => handleCopy(currentVariant)}
                        className={cn(
                            'flex items-center gap-1.5 h-8 px-3 rounded-lg',
                            'border border-border/60 text-xs',
                            'hover:bg-muted/30 transition-colors'
                        )}
                    >
                        {copiedId === currentVariant.id ? (
                            <>
                                <Check className="h-3 w-3 text-green-500" />
                                Copied
                            </>
                        ) : (
                            <>
                                <Copy className="h-3 w-3" />
                                Copy
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Variant dots */}
            <div className="flex items-center justify-center gap-1.5">
                {variants.map((variant, index) => (
                    <button
                        key={variant.id}
                        onClick={() => setCurrentIndex(index)}
                        className={cn(
                            'h-2 rounded-full transition-all',
                            index === currentIndex
                                ? 'w-4 bg-foreground'
                                : 'w-2 bg-muted-foreground/30 hover:bg-muted-foreground/50'
                        )}
                    />
                ))}
            </div>

            {/* Regenerate button */}
            {onRegenerate && (
                <button
                    onClick={onRegenerate}
                    className={cn(
                        'w-full flex items-center justify-center gap-2 h-9 rounded-lg',
                        'border border-border/60 text-sm',
                        'hover:bg-muted/30 transition-colors'
                    )}
                >
                    <Shuffle className="h-3.5 w-3.5" />
                    Generate More Variants
                </button>
            )}
        </div>
    );
}

// Compact variant pills for message display
interface VariantPillsProps {
    count: number;
    selectedIndex?: number;
    onViewVariants?: () => void;
    className?: string;
}

export function VariantPills({ count, selectedIndex, onViewVariants, className }: VariantPillsProps) {
    return (
        <button
            onClick={onViewVariants}
            className={cn(
                'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full',
                'border border-border/60 bg-card',
                'text-xs hover:bg-muted/30 transition-colors',
                className
            )}
        >
            <Sparkles className="h-3 w-3 text-muted-foreground" />
            <span>{count} variants</span>
            {selectedIndex !== undefined && (
                <span className="text-muted-foreground">
                    (#{selectedIndex + 1} selected)
                </span>
            )}
        </button>
    );
}

// Generate mock variants - in production this would come from AI
export function generateMockVariants(prompt: string, count: number = 3, context?: Record<string, string>): Variant[] {
    const baseContent = prompt.length > 50
        ? prompt.substring(0, 50) + '...'
        : prompt;

    const cohortInfo = context?.cohort ? `\n[Targeting: ${context.cohort}]` : '';

    return Array.from({ length: count }, (_, i) => ({
        id: `variant-${Date.now()}-${i}`,
        content: `[Variant ${i + 1}]${cohortInfo}\n\n${baseContent}\n\n[Different approach ${i + 1}: This would be a unique variation of the content with different phrasing, structure, or angle.]`,
        score: Math.round(50 + Math.random() * 40),
    }));
}
