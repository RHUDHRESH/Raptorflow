'use client';

import React from 'react';
import { Phase4Data } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Lock, Download, Check, Star, Target, Layers, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LockVersionProps {
    data: Phase4Data;
    onLock: () => void;
    onDownload?: () => void;
}

function formatCurrency(value: number): string {
    if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(0)}M`;
    if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
    return `$${value}`;
}

function SummaryCard({ icon: Icon, title, children, color }: {
    icon: React.ElementType;
    title: string;
    children: React.ReactNode;
    color: string;
}) {
    return (
        <div className="bg-card border rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
                <div className={cn("p-2 rounded-lg", color)}>
                    <Icon className="h-4 w-4" />
                </div>
                <h3 className="font-semibold">{title}</h3>
            </div>
            {children}
        </div>
    );
}

export function LockVersion({ data, onLock, onDownload }: LockVersionProps) {
    const primarySegment = data.targetSegments.find(s => s.isPrimary);
    const dominantValue = data.differentiatedValue.find(v => v.isDominant);

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Positioning Pack v{data.version}
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Your positioning is complete. Lock it to make it the source of truth.
                </p>
            </div>

            {/* Positioning Statement */}
            <div className="max-w-2xl mx-auto bg-gradient-to-br from-primary/5 to-primary/10 border-2 border-primary/20 rounded-2xl p-6">
                <div className="text-center">
                    <div className="text-xs text-muted-foreground uppercase tracking-wider mb-2">
                        Positioning Statement
                    </div>
                    <p className="text-lg font-serif">{data.positioningStatement}</p>
                </div>
            </div>

            {/* Summary Grid */}
            <div className="grid md:grid-cols-2 gap-4 max-w-3xl mx-auto">
                {/* Category */}
                <SummaryCard icon={Layers} title="Category" color="bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                    <p className="text-lg font-semibold">{data.marketCategory.primary}</p>
                    {data.marketCategory.altLabels.length > 0 && (
                        <p className="text-sm text-muted-foreground">
                            Alt: {data.marketCategory.altLabels[0]}
                        </p>
                    )}
                </SummaryCard>

                {/* Primary Segment */}
                <SummaryCard icon={Target} title="Primary Segment" color="bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
                    <p className="text-lg font-semibold">{primarySegment?.name || 'Not selected'}</p>
                    <p className="text-sm text-muted-foreground">{primarySegment?.jtbd}</p>
                </SummaryCard>

                {/* Dominant Value */}
                <SummaryCard icon={Star} title="Dominant Value" color="bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
                    <p className="font-medium">{dominantValue?.value || 'Not selected'}</p>
                    <p className="text-sm text-muted-foreground">For: {dominantValue?.forWhom}</p>
                </SummaryCard>

                {/* TAM/SAM/SOM */}
                <SummaryCard icon={TrendingUp} title="Market Size" color="bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                    <div className="grid grid-cols-3 gap-2 text-center">
                        <div>
                            <div className="text-xs text-muted-foreground">TAM</div>
                            <div className="font-bold">{formatCurrency(data.tamSamSom.tam.value)}</div>
                        </div>
                        <div>
                            <div className="text-xs text-muted-foreground">SAM</div>
                            <div className="font-bold">{formatCurrency(data.tamSamSom.sam.value)}</div>
                        </div>
                        <div>
                            <div className="text-xs text-muted-foreground">SOM</div>
                            <div className="font-bold">{formatCurrency(data.tamSamSom.som.value)}</div>
                        </div>
                    </div>
                </SummaryCard>
            </div>

            {/* Alternatives Count */}
            <div className="max-w-3xl mx-auto grid grid-cols-3 gap-4 text-center">
                <div className="bg-card border rounded-xl p-4">
                    <div className="text-2xl font-bold">{data.competitiveAlternatives.statusQuo.length}</div>
                    <div className="text-xs text-muted-foreground">Status Quo</div>
                </div>
                <div className="bg-card border rounded-xl p-4">
                    <div className="text-2xl font-bold">{data.competitiveAlternatives.direct.length}</div>
                    <div className="text-xs text-muted-foreground">Direct</div>
                </div>
                <div className="bg-card border rounded-xl p-4">
                    <div className="text-2xl font-bold">{data.competitiveAlternatives.indirect.length}</div>
                    <div className="text-xs text-muted-foreground">Indirect</div>
                </div>
            </div>

            {/* Proof Status */}
            <div className="max-w-md mx-auto text-center">
                <p className="text-sm text-muted-foreground">
                    {data.proofStack.filter(p => p.proof.length > 0).length} of {data.proofStack.length} claims have proof attached
                </p>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
                {onDownload && (
                    <Button variant="outline" size="lg" onClick={onDownload} className="px-6">
                        <Download className="h-4 w-4 mr-2" /> Download PDF
                    </Button>
                )}
                <Button size="lg" onClick={onLock} className="px-8 py-6 text-lg rounded-xl">
                    <Lock className="h-5 w-5 mr-2" /> Lock as Source of Truth
                </Button>
            </div>
        </div>
    );
}
