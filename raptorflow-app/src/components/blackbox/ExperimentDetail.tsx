'use client';

import React, { useEffect, useState } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Experiment } from '@/lib/blackbox-types';
import { Clock, BarChart2, Sparkles, Rocket, CheckCircle2, Copy, X, Target, BrainCircuit } from 'lucide-react';
import { cn } from '@/lib/utils';
import { EvidenceLog, EvidenceTrace } from './EvidenceLog';
import { ResultsStrip } from './ResultsStrip';
import { getOutcomesByMove, getTelemetryByMove } from '@/lib/blackbox';

interface ExperimentDetailProps {
    experiment: Experiment | null;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onLaunch?: (id: string) => void;
    onCheckin?: (id: string) => void;
}

export function ExperimentDetail({
    experiment,
    open,
    onOpenChange,
    onLaunch,
    onCheckin
}: ExperimentDetailProps) {
    const [traces, setTraces] = useState<EvidenceTrace[]>([]);
    const [outcomes, setOutcomes] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (experiment && open) {
            const fetchData = async () => {
                setIsLoading(true);
                try {
                    const [telemetryData, outcomesData] = await Promise.all([
                        getTelemetryByMove(experiment.id),
                        getOutcomesByMove(experiment.id)
                    ]);
                    setTraces(telemetryData);
                    setOutcomes(outcomesData);
                } catch (err) {
                    console.error('Failed to fetch experiment data:', err);
                } finally {
                    setIsLoading(false);
                }
            };
            fetchData();
        }
    }, [experiment, open]);

    if (!experiment) return null;

    const isDraft = experiment.status === 'draft';
    const isLaunched = experiment.status === 'launched';
    const isCheckedIn = experiment.status === 'checked_in';

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl p-0 gap-0 bg-white dark:bg-zinc-950 border-0 shadow-xl rounded-2xl overflow-hidden max-h-[90vh] flex flex-col">
                {/* Header */}
                <div className="flex items-start justify-between p-5 border-b border-zinc-100 dark:border-zinc-900 shrink-0">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-[9px] font-bold uppercase tracking-widest text-zinc-400">
                                {experiment.principle.replace('_', ' ')}
                            </span>
                            <div className={cn(
                                "h-1.5 w-1.5 rounded-full animate-pulse",
                                isLaunched ? "bg-green-500" : "bg-zinc-300"
                            )} />
                            <span className="text-[9px] font-bold uppercase tracking-widest text-zinc-300">
                                {experiment.status}
                            </span>
                        </div>
                        <h2 className="text-xl font-semibold tracking-tight">{experiment.title}</h2>
                    </div>
                    <button
                        onClick={() => onOpenChange(false)}
                        className="w-8 h-8 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-900 flex items-center justify-center transition-colors"
                    >
                        <X className="w-4 h-4 text-zinc-400" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6 overflow-y-auto">
                    {/* Bet & Why */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 bg-zinc-50 dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-2">The Bet</p>
                            <p className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed font-sans">{experiment.bet}</p>
                        </div>
                        <div className="p-4 bg-zinc-50/50 dark:bg-zinc-900/50 rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-2">The Reasoning</p>
                            <p className="text-xs text-zinc-500 italic font-sans">{experiment.why}</p>
                        </div>
                    </div>

                    {/* Meta Grid */}
                    <div className="grid grid-cols-4 gap-3">
                        {[
                            { icon: Clock, label: 'Effort', value: experiment.effort },
                            { icon: BarChart2, label: 'Signal', value: experiment.time_to_signal },
                            { icon: Target, label: 'Goal', value: experiment.goal },
                            { icon: Sparkles, label: 'Channel', value: experiment.channel },
                        ].map((item) => {
                            const Icon = item.icon;
                            return (
                                <div key={item.label} className="text-center p-3 bg-zinc-50 dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
                                    <Icon className="w-4 h-4 mx-auto text-zinc-400 mb-1" />
                                    <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 capitalize font-sans">{item.value}</p>
                                    <p className="text-[9px] text-zinc-400 uppercase font-sans font-bold">{item.label}</p>
                                </div>
                            );
                        })}
                    </div>

                    {/* Surgical Learning / Results Strip */}
                    {isCheckedIn && (
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 px-1">
                                <BrainCircuit className="w-4 h-4 text-accent" />
                                <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500 font-sans">Surgical Learning</h3>
                            </div>
                            <ResultsStrip
                                winner={experiment}
                                learnings={experiment.learning ? [experiment.learning] : []}
                            />
                        </div>
                    )}

                    {/* Outcomes */}
                    {outcomes.length > 0 && (
                        <div className="space-y-3">
                            <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500 px-1 font-sans">Business Outcomes</h3>
                            <div className="grid grid-cols-1 gap-2">
                                {outcomes.map((outcome) => (
                                    <div key={outcome.id} className="flex items-center justify-between p-4 bg-zinc-900 text-white rounded-xl">
                                        <div>
                                            <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">Source: {outcome.source}</p>
                                            <p className="text-xs font-medium text-zinc-300">Confidence: {(outcome.confidence * 100).toFixed(0)}%</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-2xl font-bold font-mono tracking-tight">{outcome.value}</p>
                                            <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-widest">{experiment.goal}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Evidence Log (Telemetry) */}
                    <div className="space-y-3 pb-4">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500 px-1 font-sans">Evidence Log</h3>
                        <EvidenceLog traces={traces} isLoading={isLoading} />
                    </div>
                </div>

                {/* Footer */}
                <div className="p-5 border-t border-zinc-100 dark:border-zinc-900 flex items-center justify-between bg-zinc-50/50 dark:bg-zinc-900/50 shrink-0">
                    <Button variant="ghost" size="sm" className="rounded-lg text-zinc-500 font-sans hover:bg-zinc-100">
                        <Copy className="w-3.5 h-3.5 mr-2" /> Duplicate
                    </Button>

                    <div className="flex items-center gap-3">
                        {isDraft && (
                            <Button
                                onClick={() => { onLaunch?.(experiment.id); onOpenChange(false); }}
                                className="rounded-xl bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 px-6 shadow-lg shadow-zinc-200 dark:shadow-none transition-all hover:scale-[1.02]"
                            >
                                <Rocket className="w-3.5 h-3.5 mr-2" /> Launch Experiment
                            </Button>
                        )}

                        {isLaunched && (
                            <Button
                                onClick={() => { onCheckin?.(experiment.id); onOpenChange(false); }}
                                variant="outline"
                                className="rounded-xl border-zinc-900 dark:border-zinc-100 px-6 hover:bg-zinc-900 hover:text-white dark:hover:bg-zinc-100 dark:hover:text-zinc-900 transition-all"
                            >
                                <CheckCircle2 className="w-3.5 h-3.5 mr-2" /> Manual Check-in
                            </Button>
                        )}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
