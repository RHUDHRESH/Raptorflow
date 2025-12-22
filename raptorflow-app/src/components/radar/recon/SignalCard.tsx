'use client';

import React, { useState } from 'react';
import { Signal } from '../types';
import { cn } from '@/lib/utils';
import { Bookmark, MoreHorizontal, ArrowRight, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

interface SignalCardProps {
    signal: Signal;
}

import { SignalDrawer } from './SignalDrawer';

export function SignalCard({ signal }: SignalCardProps) {
    const router = useRouter();
    const [isHovered, setIsHovered] = useState(false);
    const [detailOpen, setDetailOpen] = useState(false);

    const handleDraft = (angleId?: string) => {
        const angle = angleId ? signal.angles.find(a => a.id === angleId) : signal.angles.filter(Boolean)[0];
        if (angle) {
            // Build a rich, ready-to-use prompt that Muse can act on immediately
            const richPrompt = [
                `Create a ${angle.label} based on this signal:`,
                ``,
                `📡 SIGNAL: "${signal.title}"`,
                `🎯 Why it Matters: ${signal.whyItMatters}`,
                `📰 Source: ${signal.source.name}`,
                ``,
                `Direction: ${angle.prompt}`,
            ].join('\n');

            router.push(`/muse?prompt=${encodeURIComponent(richPrompt)}`);
        }
    };


    const timeAgo = (date: Date) => {
        const hours = Math.floor((new Date().getTime() - date.getTime()) / (1000 * 60 * 60));
        return hours < 24 ? `${hours}h ago` : `${Math.floor(hours / 24)}d ago`;
    };

    return (
        <>
            <div
                className={cn(
                    "group relative bg-card rounded-2xl p-6 border border-border/60 transition-all duration-200",
                    "hover:shadow-sm hover:border-border cursor-pointer"
                )}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                onClick={() => setDetailOpen(true)}
            >
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <span className={cn(
                            "h-2 w-2 rounded-full",
                            signal.confidence === 'high' ? "bg-emerald-500" :
                                signal.confidence === 'medium' ? "bg-amber-500" : "bg-zinc-300"
                        )} />
                        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                            {signal.source.name}
                        </span>
                        <span className="text-xs text-muted-foreground/40">•</span>
                        <span className="text-xs text-muted-foreground/60">{timeAgo(signal.timestamp)}</span>
                    </div>

                    <button className="text-muted-foreground/40 hover:text-foreground transition-colors">
                        <Bookmark className="h-4 w-4" />
                    </button>
                </div>

                {/* Content */}
                <h3 className="font-sans text-lg font-semibold text-foreground mb-2 leading-snug group-hover:text-primary transition-colors">
                    {signal.title}
                </h3>

                <div className="flex items-start gap-2 mb-6">
                    <span className="text-sm font-medium text-muted-foreground shrink-0 mt-0.5">Why it matters:</span>
                    <p className="text-sm text-foreground/80 leading-relaxed">
                        {signal.whyItMatters}
                    </p>
                </div>

                {/* Angles Strip */}
                <div className="flex flex-wrap gap-2 mb-6">
                    {signal.angles.filter(Boolean).map((angle) => (
                        <button
                            key={angle.id}
                            onClick={(e) => { e.stopPropagation(); handleDraft(angle.id); }}
                            className={cn(
                                "px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200",
                                "bg-secondary/40 text-muted-foreground hover:bg-secondary hover:text-foreground",
                                "border border-transparent hover:border-border/60"
                            )}
                        >
                            {angle.label}
                        </button>
                    ))}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                    <Button
                        onClick={(e) => { e.stopPropagation(); handleDraft(); }}
                        className="h-9 px-4 bg-primary text-primary-foreground hover:bg-primary/90 rounded-xl text-sm font-medium shadow-none"
                    >
                        <Zap className="h-3.5 w-3.5 mr-2" />
                        Draft in Muse
                    </Button>

                    <Button
                        onClick={(e) => { e.stopPropagation(); }}
                        variant="ghost"
                        className="h-9 px-3 text-muted-foreground hover:text-foreground rounded-xl text-sm"
                    >
                        Dismiss
                    </Button>
                </div>
            </div>

            <SignalDrawer
                signal={signal}
                open={detailOpen}
                onClose={() => setDetailOpen(false)}
            />
        </>
    );
}
