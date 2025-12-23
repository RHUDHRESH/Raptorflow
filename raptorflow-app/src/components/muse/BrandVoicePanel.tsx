'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDownIcon, MicIcon, MessageIcon, TargetIcon, SparklesIcon } from '@/components/ui/icons';

interface BrandVoice {
    tone: string;
    style: string;
    personality: string[];
    keyPhrases: string[];
    avoidPhrases: string[];
}

interface BrandVoicePanelProps {
    brandVoice?: BrandVoice;
    isCollapsed?: boolean;
    onApply?: () => void;
    className?: string;
}

// Mock brand voice data - would come from Foundation
const DEFAULT_BRAND_VOICE: BrandVoice = {
    tone: 'Confident, calm, precise',
    style: 'Direct and surgical. No fluff.',
    personality: ['Founder-friendly', 'Operator mindset', 'No hype'],
    keyPhrases: [
        'Marketing. Finally under control.',
        'From chaos to clarity.',
        'No more guessing.',
    ],
    avoidPhrases: [
        'Game-changing',
        'Synergy',
        'Best-in-class',
        'Revolutionary',
    ],
};

export function BrandVoicePanel({
    brandVoice = DEFAULT_BRAND_VOICE,
    isCollapsed: initialCollapsed = false,
    onApply,
    className
}: BrandVoicePanelProps) {
    const [isCollapsed, setIsCollapsed] = useState(initialCollapsed);

    return (
        <div className={cn(
            'border border-border/60 rounded-xl bg-card overflow-hidden',
            'transition-all duration-300',
            className
        )}>
            {/* Header */}
            <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className={cn(
                    'w-full flex items-center justify-between p-4',
                    'hover:bg-muted/30 transition-colors'
                )}
            >
                <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-foreground/5 flex items-center justify-center">
                        <MicIcon size={16} className="text-foreground/60" />
                    </div>
                    <div className="text-left">
                        <p className="text-sm font-medium">Brand Voice</p>
                        <p className="text-xs text-muted-foreground">
                            {brandVoice.tone}
                        </p>
                    </div>
                </div>
                {isCollapsed ? (
                    <ChevronDownIcon size={16} className="text-muted-foreground" />
                ) : (
                    <ChevronDownIcon size={16} className="text-muted-foreground rotate-180" />
                )}
            </button>

            {/* Content */}
            <div className={cn(
                'overflow-hidden transition-all duration-300',
                isCollapsed ? 'max-h-0 opacity-0' : 'max-h-[500px] opacity-100'
            )}>
                <div className="p-4 pt-0 space-y-4">
                    {/* Style */}
                    <div className="space-y-2">
                        <div className="flex items-center gap-2">
                            <MessageIcon size={14} className="text-muted-foreground" />
                            <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                Style
                            </span>
                        </div>
                        <p className="text-sm">{brandVoice.style}</p>
                    </div>

                    {/* Personality */}
                    <div className="space-y-2">
                        <div className="flex items-center gap-2">
                            <TargetIcon size={14} className="text-muted-foreground" />
                            <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                Personality
                            </span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                            {brandVoice.personality.map((trait, i) => (
                                <span
                                    key={i}
                                    className="px-2 py-1 rounded-md bg-muted text-xs"
                                >
                                    {trait}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Key Phrases */}
                    <div className="space-y-2">
                        <div className="flex items-center gap-2">
                            <SparklesIcon size={14} className="text-muted-foreground" />
                            <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                Key Phrases
                            </span>
                        </div>
                        <ul className="space-y-1">
                            {brandVoice.keyPhrases.map((phrase, i) => (
                                <li key={i} className="flex items-start gap-2 text-sm">
                                    <span className="text-green-500 mt-1">+</span>
                                    <span className="text-muted-foreground">{phrase}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Avoid Phrases */}
                    <div className="space-y-2">
                        <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                            Avoid
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                            {brandVoice.avoidPhrases.map((phrase, i) => (
                                <span
                                    key={i}
                                    className="px-2 py-1 rounded-md bg-red-500/10 text-red-500 text-xs line-through"
                                >
                                    {phrase}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Apply button */}
                    {onApply && (
                        <button
                            onClick={onApply}
                            className={cn(
                                'w-full h-9 rounded-lg',
                                'bg-foreground text-background',
                                'text-sm font-medium',
                                'hover:opacity-90 transition-opacity'
                            )}
                        >
                            Apply Brand Voice
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}

// Compact badge for toolbar
export function BrandVoiceBadge({
    tone = 'Confident',
    onClick,
    className
}: {
    tone?: string;
    onClick?: () => void;
    className?: string;
}) {
    return (
        <button
            onClick={onClick}
            className={cn(
                'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg',
                'border border-border/60 bg-card',
                'text-xs hover:bg-muted/30 transition-colors',
                className
            )}
        >
            <MicIcon size={12} className="text-muted-foreground" />
            <span className="text-muted-foreground">{tone}</span>
        </button>
    );
}
