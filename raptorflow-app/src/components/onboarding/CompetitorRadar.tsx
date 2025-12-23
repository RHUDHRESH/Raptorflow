'use client';

import React, { useState, useEffect } from 'react';
import { FoundationData } from '@/lib/foundation';
import { cn } from '@/lib/utils';
import { Radar, Target } from 'lucide-react';

interface CompetitorRadarProps {
    industry: string;
    onComplete?: () => void;
    className?: string;
}

interface CompetitorArchetype {
    name: string;
    description: string;
    threat: 'low' | 'medium' | 'high';
}

const INDUSTRY_ARCHETYPES: Record<string, CompetitorArchetype[]> = {
    'saas': [
        { name: 'The Incumbent', description: 'Established players with deep pockets', threat: 'high' },
        { name: 'The Disruptor', description: 'Fast-moving startups with fresh angles', threat: 'medium' },
        { name: 'The Feature Creep', description: 'Platforms expanding into your space', threat: 'medium' }
    ],
    'marketing': [
        { name: 'The Agency', description: 'Full-service firms with relationships', threat: 'high' },
        { name: 'The Tool Stack', description: 'Point solutions users already have', threat: 'medium' },
        { name: 'The DIY', description: 'Customers doing it themselves', threat: 'low' }
    ],
    'default': [
        { name: 'The Market Leader', description: 'Dominant player in your category', threat: 'high' },
        { name: 'The Niche Player', description: 'Specialists who own a segment', threat: 'medium' },
        { name: 'The Substitute', description: 'Different solutions to the same problem', threat: 'low' }
    ]
};

function getArchetypes(industry: string): CompetitorArchetype[] {
    const normalized = industry.toLowerCase();
    for (const [key, archetypes] of Object.entries(INDUSTRY_ARCHETYPES)) {
        if (normalized.includes(key)) return archetypes;
    }
    return INDUSTRY_ARCHETYPES.default;
}

export function CompetitorRadar({ industry, onComplete, className }: CompetitorRadarProps) {
    const [phase, setPhase] = useState<'scanning' | 'revealing' | 'complete'>('scanning');
    const [revealedIndex, setRevealedIndex] = useState(-1);

    const archetypes = getArchetypes(industry);

    useEffect(() => {
        if (!industry) return;

        // Scanning phase
        const scanTimer = setTimeout(() => {
            setPhase('revealing');
        }, 1500);

        return () => clearTimeout(scanTimer);
    }, [industry]);

    useEffect(() => {
        if (phase !== 'revealing') return;

        if (revealedIndex < archetypes.length - 1) {
            const timer = setTimeout(() => {
                setRevealedIndex(prev => prev + 1);
            }, 500);
            return () => clearTimeout(timer);
        } else {
            setPhase('complete');
            onComplete?.();
        }
    }, [phase, revealedIndex, archetypes.length, onComplete]);

    if (!industry) return null;

    return (
        <div className={cn(
            "bg-card border border-border rounded-2xl p-6 relative overflow-hidden",
            className
        )}>
            {/* Radar animation background */}
            {phase === 'scanning' && (
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-32 h-32 rounded-full border border-primary/20 animate-ping" />
                    <div className="absolute w-24 h-24 rounded-full border border-primary/30 animate-ping animation-delay-200" />
                    <div className="absolute w-16 h-16 rounded-full border border-primary/40 animate-ping animation-delay-400" />
                </div>
            )}

            <div className="relative">
                <div className="flex items-center gap-2 mb-4">
                    <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                        {phase === 'scanning'
                            ? <Radar className="h-4 w-4 text-primary animate-spin" />
                            : <Target className="h-4 w-4 text-primary" />
                        }
                    </div>
                    <div>
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground block">
                            Competitive Landscape
                        </span>
                        <span className="text-sm font-medium text-foreground">
                            {phase === 'scanning' ? 'Scanning...' : `${archetypes.length} archetypes detected`}
                        </span>
                    </div>
                </div>

                {/* Competitor cards */}
                <div className="space-y-2 mt-4">
                    {archetypes.map((archetype, idx) => (
                        <div
                            key={archetype.name}
                            className={cn(
                                "p-3 rounded-xl border transition-all duration-500",
                                idx <= revealedIndex
                                    ? "opacity-100 translate-x-0 bg-muted/30 border-border"
                                    : "opacity-0 translate-x-4 border-transparent"
                            )}
                        >
                            <div className="flex items-center justify-between">
                                <div>
                                    <span className="text-sm font-medium text-foreground">
                                        {archetype.name}
                                    </span>
                                    <p className="text-xs text-muted-foreground">
                                        {archetype.description}
                                    </p>
                                </div>
                                <span className={cn(
                                    "text-[10px] font-semibold uppercase px-2 py-1 rounded-full",
                                    archetype.threat === 'high' && "bg-red-100 text-red-700",
                                    archetype.threat === 'medium' && "bg-yellow-100 text-yellow-700",
                                    archetype.threat === 'low' && "bg-green-100 text-green-700"
                                )}>
                                    {archetype.threat}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
