'use client';

import React from 'react';
import { TargetSegment, SegmentScores } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { ArrowRight, Star, X, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SegmentScoreboardProps {
    segments: TargetSegment[];
    onChange: (segments: TargetSegment[]) => void;
    onContinue: () => void;
}

function ScoreBar({ label, value, color }: { label: string; value: number; color: string }) {
    return (
        <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground w-16">{label}</span>
            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                <div
                    className={cn("h-full rounded-full", color)}
                    style={{ width: `${(value / 5) * 100}%` }}
                />
            </div>
            <span className="text-xs font-medium w-4">{value}</span>
        </div>
    );
}

function SegmentCard({
    segment,
    onSetPrimary,
    onToggleExclude,
}: {
    segment: TargetSegment;
    onSetPrimary: () => void;
    onToggleExclude: () => void;
}) {
    const totalScore = Object.values(segment.scores).reduce((a, b) => a + b, 0);
    const maxScore = 25;
    const scorePercent = Math.round((totalScore / maxScore) * 100);

    return (
        <div className={cn(
            "p-5 rounded-xl border-2 transition-all",
            segment.isExcluded ? "opacity-50 border-dashed border-muted" :
                segment.isPrimary ? "border-primary bg-primary/5" : "border-border bg-card"
        )}>
            <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                    <div className="flex items-center gap-2">
                        {segment.isPrimary && (
                            <Star className="h-4 w-4 text-primary fill-current" />
                        )}
                        <h3 className="font-semibold">{segment.name}</h3>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{segment.jtbd}</p>
                </div>
                <div className={cn(
                    "text-lg font-bold",
                    scorePercent >= 80 ? "text-green-600" :
                        scorePercent >= 60 ? "text-amber-600" : "text-red-600"
                )}>
                    {scorePercent}%
                </div>
            </div>

            {/* Firmographics */}
            <div className="flex flex-wrap gap-2 mb-4">
                {Object.entries(segment.firmographics).map(([k, v]) => (
                    <span key={k} className="text-xs bg-muted px-2 py-1 rounded">
                        {k}: {v}
                    </span>
                ))}
            </div>

            {/* Score Bars */}
            <div className="space-y-2 mb-4">
                <ScoreBar label="Pain" value={segment.scores.pain} color="bg-red-500" />
                <ScoreBar label="Budget" value={segment.scores.budget} color="bg-green-500" />
                <ScoreBar label="Triggers" value={segment.scores.triggers} color="bg-blue-500" />
                <ScoreBar label="Switch" value={segment.scores.switching} color="bg-purple-500" />
                <ScoreBar label="Proof" value={segment.scores.proofFit} color="bg-amber-500" />
            </div>

            {/* Why Best Fit */}
            <div className="space-y-1 mb-4">
                {segment.whyBestFit.map((reason, i) => (
                    <p key={i} className="text-xs text-muted-foreground flex items-center gap-1">
                        <Check className="h-3 w-3 text-green-500" /> {reason}
                    </p>
                ))}
            </div>

            {/* Actions */}
            <div className="flex gap-2">
                {!segment.isExcluded && !segment.isPrimary && (
                    <Button size="sm" variant="outline" onClick={onSetPrimary}>
                        <Star className="h-3 w-3 mr-1" /> Set Primary
                    </Button>
                )}
                <Button
                    size="sm"
                    variant="ghost"
                    onClick={onToggleExclude}
                    className={segment.isExcluded ? "text-green-600" : "text-muted-foreground"}
                >
                    {segment.isExcluded ? (
                        <>Include</>
                    ) : (
                        <><X className="h-3 w-3 mr-1" /> Not our customer</>
                    )}
                </Button>
            </div>
        </div>
    );
}

export function SegmentScoreboard({ segments, onChange, onContinue }: SegmentScoreboardProps) {
    const handleSetPrimary = (segmentId: string) => {
        onChange(segments.map(s => ({
            ...s,
            isPrimary: s.id === segmentId
        })));
    };

    const handleToggleExclude = (segmentId: string) => {
        onChange(segments.map(s =>
            s.id === segmentId
                ? { ...s, isExcluded: !s.isExcluded, isPrimary: false }
                : s
        ));
    };

    const hasPrimary = segments.some(s => s.isPrimary && !s.isExcluded);

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Best-Fit Segments
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    You can't be for everyone. Pick ONE primary segment. This is Dunford Component #4.
                </p>
            </div>

            {/* Segment Cards */}
            <div className="grid gap-4 max-w-3xl mx-auto">
                {segments.map(segment => (
                    <SegmentCard
                        key={segment.id}
                        segment={segment}
                        onSetPrimary={() => handleSetPrimary(segment.id)}
                        onToggleExclude={() => handleToggleExclude(segment.id)}
                    />
                ))}
            </div>

            {/* Continue Button */}
            <div className="flex justify-center pt-4">
                <Button
                    size="lg"
                    onClick={onContinue}
                    disabled={!hasPrimary}
                    className="px-8 py-6 text-lg rounded-xl"
                >
                    {hasPrimary ? 'Continue' : 'Pick a Primary Segment'}
                    <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
            </div>
        </div>
    );
}
