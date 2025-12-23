'use client';

import React, { useState } from 'react';
import { Icp } from '@/types/icp-types';
import { cn } from '@/lib/utils';
import {
    Target,
    Sparkles,
    ChevronRight,
    Users,
    AlertTriangle,
    Zap,
    MessageSquare,
    Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ICPRevealCardProps {
    icp: Partial<Icp>;
    confidence: number;
    reasoning: string;
    onRefine?: () => void;
    onActivate?: () => void;
    isActive?: boolean;
    index: number;
}

/**
 * Premium reveal card for auto-generated ICPs
 */
export function ICPRevealCard({
    icp,
    confidence,
    reasoning,
    onRefine,
    onActivate,
    isActive,
    index
}: ICPRevealCardProps) {
    const [isRevealed, setIsRevealed] = useState(false);

    const confidencePercent = Math.round(confidence * 100);
    const confidenceColor = confidence >= 0.7 ? 'text-green-500' : confidence >= 0.5 ? 'text-yellow-500' : 'text-orange-500';

    const pains = icp.painMap?.primaryPains || [];
    const traits = icp.psycholinguistics?.mindsetTraits || [];
    const tone = icp.psycholinguistics?.tonePreference || [];

    return (
        <div
            className={cn(
                "bg-card border rounded-2xl overflow-hidden transition-all duration-500",
                isActive ? "border-primary shadow-lg shadow-primary/10" : "border-border",
                !isRevealed && "cursor-pointer hover:border-primary/50"
            )}
            style={{ animationDelay: `${index * 200}ms` }}
        >
            {/* Header */}
            <div
                className="p-6 relative"
                onClick={() => !isRevealed && setIsRevealed(true)}
            >
                {/* Priority badge */}
                {icp.priority === 'primary' && (
                    <div className="absolute top-4 right-4 px-2 py-1 bg-primary/10 text-primary text-[10px] font-semibold uppercase tracking-wider rounded-full flex items-center gap-1">
                        <Sparkles className="h-3 w-3" /> Primary
                    </div>
                )}

                <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center flex-shrink-0">
                        <Target className="h-6 w-6 text-primary" />
                    </div>

                    <div className="flex-1 min-w-0">
                        <h3 className="font-serif text-xl font-medium text-foreground mb-1 truncate">
                            {icp.name || 'Generated ICP'}
                        </h3>

                        {/* Confidence */}
                        <div className="flex items-center gap-2">
                            <div className="h-1.5 w-20 bg-muted rounded-full overflow-hidden">
                                <div
                                    className={cn("h-full rounded-full transition-all duration-500",
                                        confidence >= 0.7 ? "bg-green-500" :
                                            confidence >= 0.5 ? "bg-yellow-500" : "bg-orange-500"
                                    )}
                                    style={{ width: `${confidencePercent}%` }}
                                />
                            </div>
                            <span className={cn("text-xs font-medium", confidenceColor)}>
                                {confidencePercent}% match
                            </span>
                        </div>
                    </div>
                </div>

                {/* Reasoning */}
                <p className="text-sm text-muted-foreground mt-4 leading-relaxed">
                    {reasoning}
                </p>

                {!isRevealed && (
                    <div className="mt-4 text-xs text-primary flex items-center gap-1 font-medium">
                        Click to reveal details <ChevronRight className="h-3 w-3" />
                    </div>
                )}
            </div>

            {/* Expanded details */}
            {isRevealed && (
                <div className="border-t border-border animate-in slide-in-from-top-4 fade-in duration-300">
                    <div className="p-6 space-y-4">
                        {/* Pain Points */}
                        {pains.length > 0 && (
                            <div>
                                <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                                    <AlertTriangle className="h-3 w-3" /> Pain Points
                                </div>
                                <ul className="space-y-1">
                                    {pains.map((pain, i) => (
                                        <li key={i} className="text-sm text-foreground flex items-start gap-2">
                                            <span className="text-primary mt-1">•</span>
                                            {pain}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Mindset */}
                        {traits.length > 0 && (
                            <div>
                                <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                                    <Users className="h-3 w-3" /> Mindset
                                </div>
                                <div className="flex flex-wrap gap-1.5">
                                    {traits.map((trait, i) => (
                                        <span key={i} className="px-2 py-0.5 bg-muted text-muted-foreground text-xs rounded-full capitalize">
                                            {trait}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Tone */}
                        {tone.length > 0 && (
                            <div>
                                <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                                    <MessageSquare className="h-3 w-3" /> Preferred Tone
                                </div>
                                <div className="flex flex-wrap gap-1.5">
                                    {tone.map((t, i) => (
                                        <span key={i} className="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full capitalize">
                                            {t}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Actions */}
                    <div className="px-6 pb-6 flex gap-3">
                        {onRefine && (
                            <Button variant="outline" size="sm" onClick={onRefine} className="flex-1">
                                Refine
                            </Button>
                        )}
                        {onActivate && (
                            <Button
                                size="sm"
                                onClick={onActivate}
                                className={cn("flex-1", isActive && "bg-green-600 hover:bg-green-700")}
                            >
                                {isActive ? (
                                    <><Check className="h-4 w-4 mr-1" /> Active</>
                                ) : (
                                    <><Zap className="h-4 w-4 mr-1" /> Set Active</>
                                )}
                            </Button>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
