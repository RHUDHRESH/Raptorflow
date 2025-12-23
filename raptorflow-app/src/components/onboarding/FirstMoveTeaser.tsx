'use client';

import React, { useMemo } from 'react';
import { FoundationData } from '@/lib/foundation';
import { cn } from '@/lib/utils';
import { Lightbulb, ArrowRight, Sparkles } from 'lucide-react';

interface FirstMoveTeaserProps {
    data: FoundationData;
    className?: string;
}

interface MoveRecommendation {
    title: string;
    description: string;
    channel: string;
}

/**
 * Predicts the first marketing move based on cohort and business data
 */
export function FirstMoveTeaser({ data, className }: FirstMoveTeaserProps) {
    const recommendation = useMemo((): MoveRecommendation | null => {
        const { customerType, buyerRole, decisionStyle } = data.cohorts || {};
        const { stage } = data.business || {};

        // Simple rule-based recommendations
        if (customerType === 'b2b' || (Array.isArray(customerType) && customerType.includes('b2b'))) {
            if (buyerRole?.toLowerCase().includes('ceo') || buyerRole?.toLowerCase().includes('founder')) {
                return {
                    title: 'Executive Thought Leadership Series',
                    description: 'Build authority with a LinkedIn content strategy targeting founders and C-suite.',
                    channel: 'LinkedIn'
                };
            }
            if (buyerRole?.toLowerCase().includes('cfo') || buyerRole?.toLowerCase().includes('finance')) {
                return {
                    title: 'ROI-Focused Case Study',
                    description: 'Create a data-driven case study showing financial impact for CFOs.',
                    channel: 'Email + LinkedIn'
                };
            }
            return {
                title: 'B2B Cold Outreach Campaign',
                description: 'Targeted outreach sequence to decision-makers with value-first messaging.',
                channel: 'Email'
            };
        }

        if (customerType === 'b2c' || (Array.isArray(customerType) && customerType.includes('b2c'))) {
            if (stage === 'early' || stage === 'idea') {
                return {
                    title: 'Community Launch Strategy',
                    description: 'Build initial audience via Twitter/X threads and community engagement.',
                    channel: 'Twitter + Discord'
                };
            }
            return {
                title: 'Viral Content Hook Series',
                description: 'Create short-form video content optimized for organic reach.',
                channel: 'TikTok + Instagram'
            };
        }

        // Default
        return {
            title: 'Positioning Content Sprint',
            description: 'Establish your unique position with a 7-day content series.',
            channel: 'Multi-channel'
        };
    }, [data]);

    if (!recommendation) return null;

    return (
        <div className={cn(
            "bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/20 rounded-2xl p-6 relative overflow-hidden",
            className
        )}>
            {/* Sparkle decoration */}
            <div className="absolute -top-4 -right-4 text-primary/10">
                <Sparkles className="h-24 w-24" />
            </div>

            <div className="relative">
                <div className="flex items-center gap-2 mb-3">
                    <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Lightbulb className="h-4 w-4 text-primary" />
                    </div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-primary">
                        Your First Move
                    </span>
                </div>

                <h3 className="font-serif text-xl font-medium text-foreground mb-2">
                    {recommendation.title}
                </h3>

                <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                    {recommendation.description}
                </p>

                <div className="flex items-center justify-between">
                    <span className="text-xs bg-background/50 px-2 py-1 rounded-full text-muted-foreground">
                        Channel: {recommendation.channel}
                    </span>
                    <button className="text-xs font-medium text-primary flex items-center gap-1 hover:underline">
                        Learn more <ArrowRight className="h-3 w-3" />
                    </button>
                </div>
            </div>
        </div>
    );
}
