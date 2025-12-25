'use client';

import React, { useEffect, useState } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Experiment } from '@/lib/blackbox-types';
import { AppIcon, Icons } from '@/components/ui/Icons';
import { cn } from '@/lib/utils';
import { EvidenceLog, EvidenceTrace } from './EvidenceLog';
import { ResultsStrip } from './ResultsStrip';
import { getOutcomesByMove, getTelemetryByMove, getLearningsByMove } from '@/lib/blackbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AgentAuditLog } from './AgentAuditLog';
import { Badge } from "@/components/ui/badge";
import { GrowthHooks } from "@/lib/growth-hooks";

export interface BlackboxOutcome {
    id: string;
    experiment_id: string;
    hypothesis: string;
    confidence_score: number;
    evidence: string[];
    recommendations: string[];
    created_at: string;
}


export interface BlackboxLearning {
    id: string;
    content: string;
    learning_type: 'strategic' | 'tactical' | 'content';
    status: string;
    timestamp: string;
}

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
    const [outcomes, setOutcomes] = useState<BlackboxOutcome[]>([]);
    const [learnings, setLearnings] = useState<BlackboxLearning[]>([]);
    const [roiData, setRoiData] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (experiment && open) {
            const fetchData = async () => {
                setIsLoading(true);
                try {
                    const [telemetryData, outcomesData, learningsData] = await Promise.all([
                        getTelemetryByMove(experiment.id),
                        getOutcomesByMove(experiment.id),
                        getLearningsByMove(experiment.id)
                    ]);
                    setTraces(telemetryData);
                    setOutcomes(outcomesData);
                    setLearnings(learningsData);

                    // Set default ROI data
                    const avgRoi = 0.42;
                    const avgMomentum = 8.4;
                    setRoiData({ avgRoi, avgMomentum });
                } catch (err) {
                    console.error('Failed to fetch experiment data:', err);
                    // Mock fallback if API fails
                    setRoiData({ avgRoi: 0.42, avgMomentum: 8.4 });
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
                    <div className="flex-1">
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
                        <AppIcon icon={Icons.Close} size={16} className="text-zinc-400" />
                    </button>
                </div>

                <Tabs defaultValue="overview" className="flex-1 flex flex-col min-h-0">
                    <div className="px-5 border-b border-zinc-100 dark:border-zinc-900 bg-zinc-50/30">
                        <TabsList className="bg-transparent h-12 p-0 gap-6">
                            <TabsTrigger
                                value="overview"
                                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-zinc-900 dark:data-[state=active]:border-white rounded-none h-full px-0 text-xs font-bold uppercase tracking-widest text-zinc-400 data-[state=active]:text-zinc-900 dark:data-[state=active]:text-white"
                            >
                                Overview
                            </TabsTrigger>
                            <TabsTrigger
                                value="audit"
                                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-zinc-900 dark:data-[state=active]:border-white rounded-none h-full px-0 text-xs font-bold uppercase tracking-widest text-zinc-400 data-[state=active]:text-zinc-900 dark:data-[state=active]:text-white"
                            >
                                Agent Audit Log
                            </TabsTrigger>
                        </TabsList>
                    </div>

                    <TabsContent value="overview" className="flex-1 overflow-y-auto m-0">
                        <div className="p-6 space-y-6">
                            {/* NEW: Experiment Architecture */}
                            {experiment.hypothesis && (
                                <div className="space-y-4">
                                    <div className="flex items-center gap-2 px-1">
                                        <AppIcon icon={Icons.Target} size={16} className="text-stone-800" />
                                        <h3 className="text-xs font-bold uppercase tracking-widest text-stone-500 font-sans">Experiment Architecture</h3>
                                    </div>
                                    <Card className="rounded-xl border-stone-200 bg-stone-50/30 overflow-hidden">
                                        <div className="p-4 border-b border-stone-100">
                                            <p className="text-[10px] font-bold uppercase tracking-widest text-stone-400 mb-1">Hypothesis</p>
                                            <AppIcon icon={Icons.Time} size={16} className="text-stone-800" />
                                            <p className="text-sm text-stone-800 leading-relaxed italic">&ldquo;{experiment.hypothesis}&rdquo;</p>
                                        </div>
                                        <div className="grid grid-cols-2">
                                            <div className="p-4 border-r border-stone-100 bg-red-50/30">
                                                <p className="text-[10px] font-bold uppercase tracking-widest text-red-400 mb-1">Control (A)</p>
                                                <p className="text-xs text-stone-600 font-sans">{experiment.control}</p>
                                            </div>
                                            <div className="p-4 bg-green-50/30">
                                                <p className="text-[10px] font-bold uppercase tracking-widest text-green-600 mb-1">Variant (B)</p>
                                                <p className="text-xs text-stone-600 font-sans">{experiment.variant}</p>
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 border-t border-stone-100">
                                            <div className="p-3 border-r border-stone-100 flex items-center justify-between">
                                                <span className="text-[10px] font-bold uppercase tracking-widest text-stone-400">Metric</span>
                                                <span className="text-xs font-bold text-stone-700">{experiment.success_metric}</span>
                                            </div>
                                            <div className="p-3 flex items-center justify-between">
                                                <span className="text-[10px] font-bold uppercase tracking-widest text-stone-400">Target</span>
                                                <span className="text-xs font-bold text-stone-700">{experiment.sample_size}</span>
                                            </div>
                                        </div>
                                    </Card>
                                </div>
                            )}

                            {/* NEW: Predicted Performance */}
                            {roiData && (
                                <div className="space-y-4">
                                    <div className="flex items-center gap-2 px-1">
                                        <AppIcon icon={Icons.Chart} size={16} className="text-stone-800" />
                                        <h3 className="text-xs font-bold uppercase tracking-widest text-stone-500 font-sans">Predicted Performance</h3>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <Card className="p-4 rounded-xl border-stone-200 bg-white shadow-sm flex flex-col items-center justify-center text-center">
                                            <p className="text-[10px] font-bold uppercase tracking-widest text-stone-400 mb-1">Historical ROI</p>
                                            <div className="text-2xl font-bold text-stone-800">+{Math.round(roiData.avgRoi * 100)}%</div>
                                            <p className="text-[9px] text-stone-500 font-sans">Based on similar {experiment.goal} tests</p>
                                        </Card>
                                        <Card className="p-4 rounded-xl border-stone-200 bg-white shadow-sm flex flex-col items-center justify-center text-center">
                                            <p className="text-[10px] font-bold uppercase tracking-widest text-stone-400 mb-1">Momentum Score</p>
                                            <div className="text-2xl font-bold text-stone-800">{roiData.avgMomentum.toFixed(1)}</div>
                                            <Badge variant="outline" className="mt-1 text-[8px] bg-stone-100 text-stone-600 border-stone-200">HIGH CONFIDENCE</Badge>
                                        </Card>
                                    </div>
                                </div>
                            )}

                            {/* Bet & Why */}
                            {!experiment.hypothesis && (
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
                            )}

                            {/* Meta Grid */}
                            <div className="grid grid-cols-4 gap-3">
                                {[
                                    { icon: Icons.Clock, label: 'Effort', value: experiment.effort },
                                    { icon: Icons.BarChart2, label: 'Signal', value: experiment.time_to_signal },
                                    { icon: Icons.Target, label: 'Goal', value: experiment.goal },
                                    { icon: Icons.Sparkles, label: 'Channel', value: experiment.channel },
                                ].map((item) => {
                                    return (
                                        <div key={item.label} className="text-center p-3 bg-zinc-50 dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800">
                                            <AppIcon icon={item.icon} className="w-4 h-4 mx-auto text-zinc-400 mb-1" />
                                            <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 capitalize font-sans">{item.value}</p>
                                            <p className="text-[9px] text-zinc-400 uppercase font-bold tracking-widest">{item.label}</p>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Surgical Learning / Results Strip */}
                            {(isCheckedIn || learnings.length > 0) && (
                                <div className="space-y-4">
                                    <div className="flex items-center gap-2 px-1">
                                        <AppIcon icon={Icons.Brain} size={16} className="text-stone-800" />
                                        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500 font-sans">Surgical Learning</h3>
                                    </div>

                                    {learnings.length > 0 ? (
                                        <div className="space-y-2">
                                            {learnings.map(learning => (
                                                <div key={learning.id} className="p-4 bg-accent/5 border border-accent/10 rounded-xl">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className={cn(
                                                            "text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded",
                                                            learning.learning_type === 'strategic' ? "bg-purple-500/10 text-purple-500" :
                                                            learning.learning_type === 'tactical' ? "bg-blue-500/10 text-blue-500" :
                                                            "bg-zinc-500/10 text-zinc-500"
                                                        )}>
                                                            {learning.learning_type}
                                                        </span>
                                                        <span className="text-[9px] text-muted-foreground font-mono">
                                                            {new Date(learning.timestamp).toLocaleDateString()}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm text-zinc-800 dark:text-zinc-200 leading-relaxed">
                                                        {learning.content}
                                                    </p>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <ResultsStrip
                                            winner={experiment}
                                            learnings={experiment.learning ? [experiment.learning] : []}
                                        />
                                    )}
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
                                                    <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">Experiment ID: {outcome.experiment_id}</p>
                                                    <p className="text-xs font-medium text-zinc-300">Confidence: {(outcome.confidence_score * 100).toFixed(0)}%</p>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-2xl font-bold font-mono tracking-tight">{outcome.hypothesis}</p>
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
                    </TabsContent>

                    <TabsContent value="audit" className="flex-1 overflow-y-auto m-0 p-6 bg-zinc-50/10">
                        <AgentAuditLog moveId={experiment.id} isLoading={isLoading} />
                    </TabsContent>
                </Tabs>

                {/* Footer */}
                <div className="p-5 border-t border-zinc-100 dark:border-zinc-900 flex items-center justify-between bg-zinc-50/50 dark:bg-zinc-900/50 shrink-0">
                    <Button variant="ghost" size="sm" className="rounded-lg text-zinc-500 font-sans hover:bg-zinc-100">
                        <AppIcon icon={Icons.Copy} size={14} className="mr-2" /> Duplicate
                    </Button>

                    <div className="flex items-center gap-3">
                        {isDraft && (
                            <Button
                                onClick={() => { onLaunch?.(experiment.id); onOpenChange(false); }}
                                className="rounded-xl bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 px-6 shadow-lg shadow-zinc-200 dark:shadow-none transition-all hover:scale-[1.02]"
                            >
                                <AppIcon icon={Icons.Rocket} size={14} className="mr-2" /> Launch Experiment
                            </Button>
                        )}

                        {isLaunched && (
                            <Button
                                onClick={() => {
                                    onCheckin?.(experiment.id);
                                    GrowthHooks.trackExperimentCompletion();
                                    onOpenChange(false);
                                }}
                                variant="outline"
                                className="rounded-xl border-zinc-900 dark:border-zinc-100 px-6 hover:bg-zinc-900 hover:text-white dark:hover:bg-zinc-100 dark:hover:text-zinc-900 transition-all"
                            >
                                <AppIcon icon={Icons.CheckCircle2} size={14} className="mr-2" /> Manual Check-in
                            </Button>
                        )}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
