"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { HEURISTICS_LIBRARY, HeuristicTemplate } from '@/lib/blackbox/heuristics';
import { Sparkles, Library, FileText, Target, Calendar, Users, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Experiment, GoalType, ChannelType, RiskLevel } from '@/lib/blackbox-types';

interface ExperimentBuilderProps {
    goal: GoalType;
    channel: ChannelType;
    risk: RiskLevel;
    onComplete: (experiment: Experiment) => void;
}

export function ExperimentBuilder({ goal, channel, risk, onComplete }: ExperimentBuilderProps) {
    const [selectedHeuristic, setSelectedHeuristic] = useState<HeuristicTemplate | null>(null);
    const [hypothesis, setHypothesis] = useState('');
    const [control, setControl] = useState('');
    const [variant, setVariant] = useState('');
    const [metric, setMetric] = useState('');
    const [sampleSize, setSampleSize] = useState('');
    const [duration, setDuration] = useState(7);

    const applyHeuristic = (h: HeuristicTemplate) => {
        setSelectedHeuristic(h);
        setHypothesis(h.hypothesis_template);
        setMetric(h.success_metric);
        setSampleSize(h.sample_size_recommendation);
        setDuration(h.duration_days);
    };

    const handleBuild = () => {
        const experiment: Experiment = {
            id: `exp-manual-${Date.now()}`,
            goal,
            channel,
            risk_level: risk,
            title: selectedHeuristic?.title || "Custom Experiment",
            bet: hypothesis,
            why: selectedHeuristic?.description || "Manually defined hypothesis.",
            principle: selectedHeuristic?.principle || "pattern_interrupt",
            hypothesis,
            control,
            variant,
            success_metric: metric,
            sample_size: sampleSize,
            duration_days: duration,
            action_steps: [
                `Set up tracking for ${metric}`,
                `Deploy control: ${control}`,
                `Deploy variant: ${variant}`,
                `Run for ${duration} days`
            ],
            effort: "30m",
            time_to_signal: duration <= 2 ? "24h" : duration <= 5 ? "48h" : "7d",
            skill_stack: [],
            asset_ids: [],
            status: "draft",
            created_at: new Date().toISOString()
        };
        onComplete(experiment);
    };

    return (
        <div className="grid lg:grid-cols-12 gap-8 w-full max-w-6xl animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Left: Template Library */}
            <div className="lg:col-span-4 space-y-4">
                <div className="flex items-center space-x-2 mb-2">
                    <Library className="h-4 w-4 text-stone-400" />
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-stone-500">Proven Heuristics</h3>
                </div>
                <div className="space-y-3 overflow-y-auto max-h-[600px] pr-2 custom-scrollbar">
                    {HEURISTICS_LIBRARY.filter(h =>
                        (!h.allowed_channels || h.allowed_channels.includes(channel))
                    ).map((h) => (
                        <Card
                            key={h.id}
                            className={cn(
                                "cursor-pointer transition-all duration-300 border-stone-200 hover:border-stone-400 group",
                                selectedHeuristic?.id === h.id ? "ring-2 ring-stone-800 border-stone-800 bg-stone-50" : "bg-white"
                            )}
                            onClick={() => applyHeuristic(h)}
                        >
                            <CardContent className="p-4 space-y-2">
                                <div className="flex justify-between items-start">
                                    <h4 className="font-bold text-stone-800 group-hover:text-black transition-colors">{h.title}</h4>
                                    <span className="text-[10px] font-mono text-stone-400 bg-stone-100 px-1.5 py-0.5 rounded uppercase">
                                        Impact: {h.impact_score}/10
                                    </span>
                                </div>
                                <p className="text-xs text-stone-500 leading-relaxed">{h.description}</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>

            {/* Right: Form Builder */}
            <div className="lg:col-span-8">
                <Card className="rounded-2xl border-stone-200 bg-white/50 backdrop-blur-sm shadow-md overflow-hidden">
                    <CardHeader className="border-b border-stone-100 bg-stone-50/50 py-6 px-8">
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle className="text-2xl font-serif text-stone-800">Experiment Builder</CardTitle>
                                <CardDescription className="text-stone-500">Construct your growth hypothesis with surgical precision</CardDescription>
                            </div>
                            <Sparkles className="h-6 w-6 text-stone-300" />
                        </div>
                    </CardHeader>
                    <CardContent className="p-8 space-y-8">
                        {/* Hypothesis Section */}
                        <div className="space-y-4">
                            <div className="flex items-center space-x-2">
                                <FileText className="h-4 w-4 text-stone-400" />
                                <Label className="text-sm font-semibold uppercase tracking-tight">Structured Hypothesis</Label>
                            </div>
                            <Textarea
                                placeholder="If we [Action], then [Metric] will [Change] because [Reason]..."
                                className="min-h-[100px] rounded-xl border-stone-200 focus:border-stone-800 focus:ring-stone-800/10 transition-all text-base leading-relaxed"
                                value={hypothesis}
                                onChange={(e) => setHypothesis(e.target.value)}
                            />
                        </div>

                        {/* Variables Grid */}
                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="space-y-3">
                                <Label className="text-xs font-bold text-red-500 uppercase tracking-widest flex items-center">
                                    <div className="w-1.5 h-1.5 rounded-full bg-red-500 mr-2" />
                                    Control (A)
                                </Label>
                                <Input
                                    placeholder={selectedHeuristic?.control_placeholder || "Current behavior..."}
                                    className="rounded-xl border-stone-200"
                                    value={control}
                                    onChange={(e) => setControl(e.target.value)}
                                />
                            </div>
                            <div className="space-y-3">
                                <Label className="text-xs font-bold text-green-600 uppercase tracking-widest flex items-center">
                                    <div className="w-1.5 h-1.5 rounded-full bg-green-600 mr-2" />
                                    Variant (B)
                                </Label>
                                <Input
                                    placeholder={selectedHeuristic?.variant_placeholder || "New behavior..."}
                                    className="rounded-xl border-stone-200"
                                    value={variant}
                                    onChange={(e) => setVariant(e.target.value)}
                                />
                            </div>
                        </div>

                        {/* Stats & Logic */}
                        <div className="grid md:grid-cols-3 gap-6 pt-4 border-t border-stone-100">
                            <div className="space-y-2">
                                <Label className="text-[10px] uppercase font-bold text-stone-400 flex items-center">
                                    <Target className="h-3 w-3 mr-1" /> Success Metric
                                </Label>
                                <Input
                                    placeholder="e.g. Reply Rate"
                                    className="rounded-lg h-9 text-sm"
                                    value={metric}
                                    onChange={(e) => setMetric(e.target.value)}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-[10px] uppercase font-bold text-stone-400 flex items-center">
                                    <Users className="h-3 w-3 mr-1" /> Min. Sample
                                </Label>
                                <Input
                                    placeholder="e.g. 500 visitors"
                                    className="rounded-lg h-9 text-sm"
                                    value={sampleSize}
                                    onChange={(e) => setSampleSize(e.target.value)}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-[10px] uppercase font-bold text-stone-400 flex items-center">
                                    <Calendar className="h-3 w-3 mr-1" /> Duration (Days)
                                </Label>
                                <Input
                                    type="number"
                                    className="rounded-lg h-9 text-sm"
                                    value={duration}
                                    onChange={(e) => setDuration(parseInt(e.target.value))}
                                />
                            </div>
                        </div>

                        <Button
                            className="w-full h-14 rounded-2xl bg-stone-900 hover:bg-black text-white text-lg font-medium transition-all group"
                            onClick={handleBuild}
                            disabled={!hypothesis || !control || !variant}
                        >
                            Finalize Experiment
                            <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
