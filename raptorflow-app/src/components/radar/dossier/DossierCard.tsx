'use client';

import React from 'react';
import { Dossier } from '../types';
import { cn } from '@/lib/utils';
import { ArrowRight, FileText, Target } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DossierCardProps {
    dossier: Dossier;
}

import { DossierDetail } from './DossierDetail';
import { useState } from 'react';

export function DossierCard({ dossier }: DossierCardProps) {
    const [detailOpen, setDetailOpen] = useState(false);

    return (
        <>
            <div
                className={cn(
                    "group flex flex-col h-full bg-card rounded-2xl border border-border/60 overflow-hidden transition-all duration-300",
                    "hover:border-border hover:shadow-md hover:-translate-y-0.5 cursor-pointer"
                )}
                onClick={() => setDetailOpen(true)}
            >

                {/* Decorative Top Strip */}
                <div className="h-1.5 w-full bg-gradient-to-r from-zinc-200 to-zinc-100 dark:from-zinc-800 dark:to-zinc-900" />

                <div className="p-7 flex flex-col h-full">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                            <FileText className="h-3.5 w-3.5" />
                            Strategic Brief
                        </div>
                        <span className="text-xs text-muted-foreground/60">
                            {dossier.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </span>
                    </div>

                    {/* Title */}
                    <h3 className="font-display text-2xl font-medium text-foreground mb-4 leading-tight group-hover:text-primary transition-colors">
                        {dossier.title}
                    </h3>

                    {/* What Changed */}
                    <div className="mb-6">
                        <p className="text-sm leading-relaxed text-muted-foreground line-clamp-3">
                            <span className="text-foreground font-medium">Market Shift: </span>
                            {dossier.whatChanged}
                        </p>
                    </div>

                    {/* Key Points */}
                    <div className="space-y-2 mb-8 flex-1">
                        {dossier.summary.map((point, i) => (
                            <div key={i} className="flex items-start gap-2.5">
                                <span className="h-1.5 w-1.5 rounded-full bg-border mt-2 shrink-0 group-hover:bg-primary/40 transition-colors" />
                                <p className="text-sm text-foreground/80">{point}</p>
                            </div>
                        ))}
                    </div>

                    {/* Recommended Move (Highlight) */}
                    <div className="mt-auto mb-6 p-4 rounded-xl bg-secondary/30 border border-secondary/50">
                        <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-primary/80 uppercase tracking-wide">
                            <Target className="h-3.5 w-3.5" />
                            Recommended Move
                        </div>
                        <p className="text-sm font-medium text-foreground">
                            {dossier.recommendedMove.name}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
                            {dossier.recommendedMove.target}
                        </p>
                    </div>

                    {/* Action */}
                    <Button
                        className="w-full justify-between group-hover:bg-primary group-hover:text-primary-foreground transition-all"
                        variant="outline"
                        onClick={(e) => { e.stopPropagation(); setDetailOpen(true); }}
                    >
                        View Dossier
                        <ArrowRight className="h-4 w-4 opacity-50 group-hover:translate-x-1 transition-transform" />
                    </Button>
                </div>
            </div>

            <DossierDetail
                dossier={dossier}
                open={detailOpen}
                onClose={() => setDetailOpen(false)}
            />
        </>
    );
}
