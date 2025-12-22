'use client';

import React from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Experiment } from '@/lib/blackbox-types';
import { Clock, BarChart2, Sparkles, Rocket, CheckCircle2, Copy, X, Target } from 'lucide-react';
import { cn } from '@/lib/utils';

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
    if (!experiment) return null;

    const isDraft = experiment.status === 'draft';
    const isLaunched = experiment.status === 'launched';
    const isCheckedIn = experiment.status === 'checked_in';

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-lg p-0 gap-0 bg-white dark:bg-zinc-950 border-0 shadow-xl rounded-2xl overflow-hidden">
                {/* Header */}
                <div className="flex items-start justify-between p-5 border-b border-zinc-100 dark:border-zinc-900">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-[9px] font-bold uppercase tracking-widest text-zinc-400">
                                {experiment.principle.replace('_', ' ')}
                            </span>
                            <span className="text-[9px] font-bold uppercase tracking-widest text-zinc-300">
                                {experiment.status}
                            </span>
                        </div>
                        <h2 className="text-lg font-semibold">{experiment.title}</h2>
                    </div>
                    <button
                        onClick={() => onOpenChange(false)}
                        className="w-7 h-7 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-900 flex items-center justify-center"
                    >
                        <X className="w-4 h-4 text-zinc-400" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-5 space-y-4">
                    {/* Bet */}
                    <div className="p-4 bg-zinc-50 dark:bg-zinc-900 rounded-lg">
                        <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-1">The Bet</p>
                        <p className="text-sm text-zinc-700 dark:text-zinc-300">{experiment.bet}</p>
                    </div>

                    {/* Why */}
                    <div>
                        <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-1">Why it works</p>
                        <p className="text-xs text-zinc-500 italic">{experiment.why}</p>
                    </div>

                    {/* Meta Grid */}
                    <div className="grid grid-cols-4 gap-2">
                        {[
                            { icon: Clock, label: 'Effort', value: experiment.effort },
                            { icon: BarChart2, label: 'Signal', value: experiment.time_to_signal },
                            { icon: Target, label: 'Goal', value: experiment.goal },
                            { icon: Sparkles, label: 'Channel', value: experiment.channel },
                        ].map((item) => {
                            const Icon = item.icon;
                            return (
                                <div key={item.label} className="text-center p-2 bg-zinc-50 dark:bg-zinc-900 rounded-lg">
                                    <Icon className="w-3.5 h-3.5 mx-auto text-zinc-400 mb-0.5" />
                                    <p className="text-xs font-medium text-zinc-900 dark:text-zinc-100 capitalize">{item.value}</p>
                                    <p className="text-[9px] text-zinc-400 uppercase">{item.label}</p>
                                </div>
                            );
                        })}
                    </div>

                    {/* Results */}
                    {isCheckedIn && experiment.self_report && (
                        <div className="p-4 bg-zinc-50 dark:bg-zinc-900 rounded-lg flex items-center justify-between">
                            <div>
                                <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">Result</p>
                                <p className="text-sm font-medium capitalize">{experiment.self_report.outcome}</p>
                            </div>
                            <div className="text-right">
                                <p className="text-2xl font-bold font-mono">{experiment.self_report.metric_value}</p>
                                <p className="text-[10px] text-zinc-400 capitalize">{experiment.self_report.metric_name}</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-5 border-t border-zinc-100 dark:border-zinc-900 flex items-center justify-between">
                    <Button variant="ghost" size="sm" className="rounded-lg text-zinc-500">
                        <Copy className="w-3.5 h-3.5 mr-1.5" /> Duplicate
                    </Button>

                    {isDraft && (
                        <Button
                            onClick={() => { onLaunch?.(experiment.id); onOpenChange(false); }}
                            className="rounded-lg bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 px-5"
                        >
                            <Rocket className="w-3.5 h-3.5 mr-1.5" /> Launch
                        </Button>
                    )}

                    {isLaunched && (
                        <Button
                            onClick={() => { onCheckin?.(experiment.id); onOpenChange(false); }}
                            variant="outline"
                            className="rounded-lg border-zinc-900 dark:border-zinc-100 px-5"
                        >
                            <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" /> Check-in
                        </Button>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
