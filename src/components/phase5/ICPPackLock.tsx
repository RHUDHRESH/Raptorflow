'use client';

import React from 'react';
import { Phase5Data, ICP, ICPFitScore } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Lock, Download, Users, Target, Network, Check, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ICPPackLockProps {
    data: Phase5Data;
    onLock: () => void;
    onDownload?: () => void;
}

function ICPSummaryCard({ icp }: { icp: ICP }) {
    const scorePercent = icp.fitScore.total;
    const assumedCount = icp.dataConfidence.assumed.length;
    const provenCount = icp.dataConfidence.proven.length;

    return (
        <div className="bg-card border rounded-xl p-4">
            <div className="flex items-start justify-between gap-4 mb-3">
                <div>
                    <h3 className="font-semibold">{icp.name}</h3>
                    <p className="text-sm text-muted-foreground">
                        Displacing: {icp.displacedAlternative}
                    </p>
                </div>
                <div className={cn(
                    "text-lg font-bold",
                    scorePercent >= 80 ? "text-green-600" :
                        scorePercent >= 60 ? "text-amber-600" : "text-red-600"
                )}>
                    {scorePercent}%
                </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="bg-muted rounded p-2">
                    <div className="font-bold">{icp.personas.length}</div>
                    <div className="text-muted-foreground">Personas</div>
                </div>
                <div className="bg-muted rounded p-2">
                    <div className="font-bold">{icp.habitat.platforms.length}</div>
                    <div className="text-muted-foreground">Channels</div>
                </div>
                <div className="bg-muted rounded p-2">
                    <div className="font-bold">{icp.triggers.length}</div>
                    <div className="text-muted-foreground">Triggers</div>
                </div>
            </div>

            {assumedCount > 0 && (
                <div className="mt-3 flex items-center gap-2 text-amber-600 text-xs">
                    <AlertCircle className="h-3 w-3" />
                    {assumedCount} assumed fields need validation
                </div>
            )}
        </div>
    );
}

export function ICPPackLock({ data, onLock, onDownload }: ICPPackLockProps) {
    const totalICPs = data.icps.length;
    const totalPersonas = data.icps.reduce((acc, icp) => acc + icp.personas.length, 0);
    const wedgeICP = data.icps.find(i => i.id === data.interICPGraph.primaryWedgeICP);

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    ICP Pack v{data.version}
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Your targeting intelligence is complete. Lock it as source of truth.
                </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
                <div className="text-center bg-card border rounded-xl p-4">
                    <Target className="h-6 w-6 mx-auto mb-2 text-primary" />
                    <div className="text-2xl font-bold">{totalICPs}</div>
                    <div className="text-xs text-muted-foreground">ICPs</div>
                </div>
                <div className="text-center bg-card border rounded-xl p-4">
                    <Users className="h-6 w-6 mx-auto mb-2 text-purple-500" />
                    <div className="text-2xl font-bold">{totalPersonas}</div>
                    <div className="text-xs text-muted-foreground">Personas</div>
                </div>
                <div className="text-center bg-card border rounded-xl p-4">
                    <Network className="h-6 w-6 mx-auto mb-2 text-amber-500" />
                    <div className="text-2xl font-bold">{data.interICPGraph.edges.length}</div>
                    <div className="text-xs text-muted-foreground">Relationships</div>
                </div>
            </div>

            {/* Wedge Strategy */}
            {wedgeICP && (
                <div className="max-w-md mx-auto bg-primary/5 border-2 border-primary/20 rounded-xl p-4 text-center">
                    <p className="text-sm text-muted-foreground mb-1">Primary Wedge ICP</p>
                    <p className="text-lg font-semibold text-primary">{wedgeICP.name}</p>
                </div>
            )}

            {/* ICP Cards */}
            <div className="grid md:grid-cols-2 gap-4 max-w-3xl mx-auto">
                {data.icps.map(icp => (
                    <ICPSummaryCard key={icp.id} icp={icp} />
                ))}
            </div>

            {/* What's Included */}
            <div className="max-w-md mx-auto">
                <h3 className="font-semibold mb-3 text-center">Pack Contents</h3>
                <div className="space-y-2">
                    {[
                        'ICP Definitions (firmographics + technographics)',
                        'Persona Stacks (goals, objections, proof needs)',
                        'Buying Group Maps (Gartner model)',
                        'JTBD Forces of Progress',
                        'Habitat & Discovery Maps',
                        'Inter-ICP Relationship Graph'
                    ].map((item, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm">
                            <Check className="h-4 w-4 text-green-500" />
                            {item}
                        </div>
                    ))}
                </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
                {onDownload && (
                    <Button variant="outline" size="lg" onClick={onDownload} className="px-6">
                        <Download className="h-4 w-4 mr-2" /> Export Pack
                    </Button>
                )}
                <Button size="lg" onClick={onLock} className="px-8 py-6 text-lg rounded-xl">
                    <Lock className="h-5 w-5 mr-2" /> Lock as Source of Truth
                </Button>
            </div>
        </div>
    );
}
