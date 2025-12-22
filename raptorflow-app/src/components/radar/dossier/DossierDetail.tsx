'use client';

import React from 'react';
import { Dossier } from '../types';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download, Share2, Target, CheckCircle2 } from 'lucide-react';

interface DossierDetailProps {
    dossier: Dossier | null;
    open: boolean;
    onClose: () => void;
}

export function DossierDetail({ dossier, open, onClose }: DossierDetailProps) {
    if (!dossier) return null;

    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="max-w-4xl h-[90vh] p-0 overflow-hidden flex flex-col bg-background/95 backdrop-blur-sm">
                <div className="flex items-center justify-between px-6 py-4 border-b border-border/40">
                    <Button variant="ghost" size="sm" onClick={onClose} className="gap-2 -ml-2 text-muted-foreground hover:text-foreground">
                        <ArrowLeft className="h-4 w-4" />
                        Back to Radar
                    </Button>
                    <div className="flex gap-2">
                        <Button variant="outline" size="sm" className="gap-2">
                            <Share2 className="h-4 w-4" />
                            Share
                        </Button>
                        <Button variant="outline" size="sm" className="gap-2">
                            <Download className="h-4 w-4" />
                            Export PDF
                        </Button>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto">
                    <div className="max-w-3xl mx-auto px-8 py-12">
                        {/* Header */}
                        <div className="mb-12">
                            <div className="flex items-center gap-2 mb-4">
                                <span className="px-2 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium uppercase tracking-wider">
                                    Strategic Brief
                                </span>
                                <span className="text-sm text-muted-foreground">
                                    {dossier.date.toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' })}
                                </span>
                            </div>
                            <h1 className="font-display text-4xl md:text-5xl font-semibold text-foreground leading-tight mb-6">
                                {dossier.title}
                            </h1>
                            <div className="p-6 rounded-2xl bg-secondary/30 border border-border/50">
                                <h3 className="text-lg font-medium mb-3">Executive Summary</h3>
                                <div className="space-y-2">
                                    {dossier.summary.map((point, i) => (
                                        <div key={i} className="flex gap-3 items-start">
                                            <CheckCircle2 className="h-5 w-5 text-primary/60 shrink-0 mt-0.5" />
                                            <p className="text-foreground/80 leading-relaxed">{point}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Content Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-12">
                            <div>
                                <h3 className="font-display text-2xl font-medium mb-4">The Shift</h3>
                                <p className="text-foreground/80 leading-relaxed text-lg">
                                    {dossier.whatChanged}
                                </p>
                            </div>
                            <div>
                                <h3 className="font-display text-2xl font-medium mb-4">Why It Matters</h3>
                                <ul className="space-y-3">
                                    {dossier.whyItMatters.impacts.map((impact, i) => (
                                        <li key={i} className="flex gap-2">
                                            <span className="text-primary font-bold">•</span>
                                            <span className="text-foreground/80">{impact}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        {/* Market Narrative */}
                        <div className="mb-12 p-8 rounded-2xl border border-border/60 bg-card">
                            <h3 className="font-display text-2xl font-medium mb-6">Market Narrative</h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                                <div>
                                    <span className="text-xs uppercase tracking-wider text-muted-foreground block mb-2">They Believe</span>
                                    <p className="font-medium text-lg leading-snug">{dossier.marketNarrative.believing}</p>
                                </div>
                                <div>
                                    <span className="text-xs uppercase tracking-wider text-amber-500/80 block mb-2">Overhyped</span>
                                    <p className="font-medium text-lg leading-snug">{dossier.marketNarrative.overhyped}</p>
                                </div>
                                <div>
                                    <span className="text-xs uppercase tracking-wider text-emerald-500/80 block mb-2">Underrated</span>
                                    <p className="font-medium text-lg leading-snug">{dossier.marketNarrative.underrated}</p>
                                </div>
                            </div>
                        </div>

                        {/* Recommended Move */}
                        <div className="mb-12">
                            <div className="bg-primary text-primary-foreground rounded-2xl p-8 shadow-xl shadow-primary/5">
                                <div className="flex items-center gap-3 mb-4">
                                    <Target className="h-6 w-6" />
                                    <h3 className="font-display text-2xl font-medium">Recommended Move</h3>
                                </div>

                                <div className="space-y-1 mb-6">
                                    <div className="text-primary-foreground/60 text-sm uppercase tracking-wider">Operation Name</div>
                                    <div className="text-3xl font-bold">{dossier.recommendedMove.name}</div>
                                </div>

                                <div className="flex flex-col md:flex-row gap-8">
                                    <div className="flex-1">
                                        <div className="text-primary-foreground/60 text-sm uppercase tracking-wider mb-2">The Action</div>
                                        <div className="text-lg leading-relaxed font-medium">
                                            {dossier.recommendedMove.action}
                                        </div>
                                    </div>
                                    <div className="md:w-1/3">
                                        <div className="text-primary-foreground/60 text-sm uppercase tracking-wider mb-2">Target Outcome</div>
                                        <div className="text-2xl font-bold">
                                            {dossier.recommendedMove.target}
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-8 pt-8 border-t border-primary-foreground/20 flex gap-4">
                                    <Button variant="secondary" className="flex-1 h-12 text-base font-semibold text-primary">
                                        Activate this Move
                                    </Button>
                                    <Button variant="outline" className="flex-1 h-12 text-base border-primary-foreground/20 hover:bg-primary-foreground/10 text-primary-foreground hover:text-white bg-transparent">
                                        Generate Assets
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
