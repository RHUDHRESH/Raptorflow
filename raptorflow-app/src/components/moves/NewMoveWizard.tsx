'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import {
    Move,
    MoveGoal,
    MoveDuration,
    ChannelType,
    Campaign,
    OFFER_LABELS,
    OBJECTIVE_LABELS,
    GOAL_LABELS,
    CHANNEL_LABELS,
    isGoalAligned,
    OverrideReason,
    OVERRIDE_LABELS
} from '@/lib/campaigns-types';
import {
    createMove,
    getCampaigns,
    getActiveMove,
    setActiveMove,
    logMoveOverride,
    generateMoveId,
    generateDefaultChecklist
} from '@/lib/campaigns';
import { Check, ChevronRight, AlertTriangle, Plus, Trash2, X, Target, Zap, Clock, ArrowLeft, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface NewMoveWizardProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onComplete: (moves: Move[]) => void;
}

type Step = 'select-goals' | 'configure' | 'review';

interface PendingMove {
    tempId: string;
    goal: MoveGoal;
    channel: ChannelType | null;
    duration: MoveDuration;
    dailyEffort: 15 | 30 | 60;
    campaignId: string | 'standalone' | null;
    overrideReason?: OverrideReason;
}

export function NewMoveWizard({ open, onOpenChange, onComplete }: NewMoveWizardProps) {
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [activeStep, setActiveStep] = useState<Step>('select-goals');

    // Multi-move state
    const [selectedCampaignId, setSelectedCampaignId] = useState<string | 'standalone' | null>(null);
    const [pendingMoves, setPendingMoves] = useState<PendingMove[]>([]);

    // Pagination state for configuration step
    const [activeConfigIndex, setActiveConfigIndex] = useState(0);

    useEffect(() => {
        if (open) {
            setCampaigns(getCampaigns().filter(c => c.status === 'active' || c.status === 'planned'));
            // Reset to clean state
            setActiveStep('select-goals');
            setSelectedCampaignId(null);
            setPendingMoves([]);
            setActiveConfigIndex(0);
        }
    }, [open]);

    const handleToggleGoal = (goal: MoveGoal) => {
        const existingIndex = pendingMoves.findIndex(p => p.goal === goal);
        if (existingIndex >= 0) {
            // Remove
            setPendingMoves(prev => prev.filter((_, i) => i !== existingIndex));
        } else {
            // Add new pending move with defaults
            const newMove: PendingMove = {
                tempId: Math.random().toString(36).substr(2, 9),
                goal,
                channel: null, // User must select
                duration: 7,
                dailyEffort: 30,
                campaignId: selectedCampaignId,
            };
            setPendingMoves(prev => [...prev, newMove]);
        }
    };

    const updateMove = (tempId: string, updates: Partial<PendingMove>) => {
        setPendingMoves(prev => prev.map(m => m.tempId === tempId ? { ...m, ...updates } : m));
    };

    const handleNext = () => {
        if (activeStep === 'select-goals') {
            setActiveStep('configure');
            setActiveConfigIndex(0);
        } else if (activeStep === 'configure') {
            if (activeConfigIndex < pendingMoves.length - 1) {
                // Next move config
                setActiveConfigIndex(prev => prev + 1);
            } else {
                // Done configuring all
                setActiveStep('review');
            }
        } else if (activeStep === 'review') {
            handleCreateAll();
        }
    };

    const handleBack = () => {
        if (activeStep === 'select-goals') {
            onOpenChange(false);
        } else if (activeStep === 'configure') {
            if (activeConfigIndex > 0) {
                setActiveConfigIndex(prev => prev - 1);
            } else {
                setActiveStep('select-goals');
            }
        } else if (activeStep === 'review') {
            setActiveStep('configure');
            setActiveConfigIndex(pendingMoves.length - 1); // Go to last config
        }
    };

    const handleCreateAll = () => {
        // Validation
        const incomplete = pendingMoves.filter(m => !m.channel);
        if (incomplete.length > 0) {
            toast.error('Please select a channel for all moves');
            return;
        }

        const createdMoves: Move[] = [];
        const isGlobalActive = !!getActiveMove();
        let queuedCount = 0;

        pendingMoves.forEach((pm, index) => {
            const moveId = generateMoveId();
            const now = new Date().toISOString();
            const campaign = campaigns.find(c => c.id === pm.campaignId);

            // First move starts now if nothing active, others queued
            const shouldStart = !isGlobalActive && index === 0;

            const newMove: Move = {
                id: moveId,
                name: `${GOAL_LABELS[pm.goal].label} Sprint`,
                goal: pm.goal,
                channel: pm.channel!,
                duration: pm.duration,
                dailyEffort: pm.dailyEffort,
                status: shouldStart ? 'active' : 'queued',
                campaignId: campaign?.id,
                campaignName: campaign?.name,
                createdAt: now,
                startedAt: shouldStart ? now : undefined,
                dueDate: shouldStart ? new Date(Date.now() + pm.duration * 24 * 60 * 60 * 1000).toISOString() : undefined,
                checklist: generateDefaultChecklist(pm.goal, pm.channel!, pm.duration),
                assetIds: [],
            };

            if (pm.overrideReason && campaign) {
                newMove.override = {
                    reason: pm.overrideReason,
                    originalCampaignObjective: campaign.objective,
                    loggedAt: now
                };
                logMoveOverride(newMove, campaign, pm.overrideReason);
            }

            createMove(newMove);
            createdMoves.push(newMove);

            if (shouldStart) {
                setActiveMove(moveId);
            } else {
                queuedCount++;
            }
        });

        toast.success(`Created ${createdMoves.length} moves (${queuedCount} queued)`);
        onComplete(createdMoves);
    };

    // --- Renderers ---

    const renderHeader = () => (
        <div className="px-8 py-6 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 sticky top-0 z-10 flex justify-between items-start">
            <div>
                <h2 className="font-display text-3xl font-medium text-zinc-900 dark:text-zinc-100">
                    {activeStep === 'select-goals' && "Select Your Targets"}
                    {activeStep === 'configure' && `Configure: ${GOAL_LABELS[pendingMoves[activeConfigIndex]?.goal]?.label || 'Strategy'}`}
                    {activeStep === 'review' && "Confirm Battle Plan"}
                </h2>
                <div className="flex items-center gap-2 mt-1">
                    <p className="text-zinc-500 text-lg">
                        {activeStep === 'select-goals' && "Choose one or more objectives to attack simultaneously."}
                        {activeStep === 'configure' && `Step ${activeConfigIndex + 1} of ${pendingMoves.length}. Define tactics for this objective.`}
                        {activeStep === 'review' && "Review and launch your moves."}
                    </p>
                </div>

            </div>
            <div className="flex items-center gap-2">
                <div className="flex gap-1 mr-4">
                    {['select-goals', 'configure', 'review'].map((s, i) => (
                        <div key={s} className={cn(
                            "h-2 w-8 rounded-full transition-all",
                            activeStep === s ? "bg-zinc-900 dark:bg-zinc-100" :
                                (['select-goals', 'configure', 'review'].indexOf(activeStep) > i) ? "bg-zinc-400 dark:bg-zinc-600" : "bg-zinc-200 dark:bg-zinc-800"
                        )} />
                    ))}
                </div>
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onOpenChange(false)}
                    className="rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800"
                >
                    <X className="w-5 h-5" />
                </Button>
            </div>
        </div>
    );

    const renderFooter = () => {
        // Validation for buttons
        let canProceed = true;
        let nextLabel = "Next";

        if (activeStep === 'select-goals') {
            canProceed = pendingMoves.length > 0;
            nextLabel = "Configure Strategy";
        } else if (activeStep === 'configure') {
            const currentMove = pendingMoves[activeConfigIndex];
            canProceed = !!currentMove?.channel;
            nextLabel = activeConfigIndex < pendingMoves.length - 1 ? "Next Move" : "Review Plan";
        } else if (activeStep === 'review') {
            nextLabel = `Launch ${pendingMoves.length} Moves`;
        }

        return (
            <div className="px-8 py-6 border-t border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 flex justify-between items-center mt-auto">
                <Button
                    variant="ghost"
                    onClick={handleBack}
                    className="text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 flex items-center gap-2 pl-2 pr-4 h-12 rounded-xl"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back
                </Button>

                <div className="flex items-center gap-4">
                    <div className="text-sm text-zinc-500 font-medium">
                        {activeStep === 'select-goals' && `${pendingMoves.length} selected`}
                        {activeStep === 'configure' && `${activeConfigIndex + 1} / ${pendingMoves.length}`}
                    </div>

                    <Button
                        onClick={handleNext}
                        disabled={!canProceed}
                        className={cn(
                            "px-8 h-12 text-base rounded-xl flex items-center gap-2",
                            activeStep === 'review'
                                ? "bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900"
                                : "bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900"
                        )}
                    >
                        {nextLabel}
                        {activeStep !== 'review' && <ArrowRight className="w-4 h-4" />}
                    </Button>
                </div>
            </div>
        );
    };

    const renderConfigureStep = () => {
        const pm = pendingMoves[activeConfigIndex];
        if (!pm) return null;

        return (
            <div className="max-w-3xl mx-auto space-y-8 animate-in slide-in-from-right-8 duration-300 fade-in">
                {/* Pagination Indicator within Content */}
                {pendingMoves.length > 1 && (
                    <div className="flex justify-center gap-2 mb-8">
                        {pendingMoves.map((_, idx) => (
                            <button
                                key={idx}
                                onClick={() => setActiveConfigIndex(idx)}
                                className={cn(
                                    "w-3 h-3 rounded-full transition-all",
                                    idx === activeConfigIndex
                                        ? "bg-zinc-900 scale-125 dark:bg-zinc-100"
                                        : idx < activeConfigIndex
                                            ? "bg-zinc-400 dark:bg-zinc-600"
                                            : "bg-zinc-200 dark:bg-zinc-800"
                                )}
                            />
                        ))}
                    </div>
                )}

                <div className="bg-white dark:bg-zinc-900 rounded-3xl border border-zinc-200 dark:border-zinc-800 overflow-hidden shadow-lg shadow-zinc-200/50 dark:shadow-none">
                    <div className="px-8 py-6 border-b border-zinc-100 dark:border-zinc-800 flex justify-between items-center bg-zinc-50/50 dark:bg-zinc-900/50">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-2xl bg-zinc-900 text-white dark:bg-white dark:text-zinc-900 flex items-center justify-center text-xl font-bold shadow-lg">
                                {activeConfigIndex + 1}
                            </div>
                            <div>
                                <h3 className="font-display font-medium text-2xl text-zinc-900 dark:text-zinc-100">{GOAL_LABELS[pm.goal].label}</h3>
                                <p className="text-sm text-zinc-500">{GOAL_LABELS[pm.goal].description}</p>
                            </div>

                        </div>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => updateMove(pm.tempId, { duration: 7, dailyEffort: 30, channel: null })}
                            className="text-zinc-400 hover:text-red-500"
                        >
                            Reset Defaults
                        </Button>
                    </div>

                    <div className="p-8 space-y-8">
                        {/* Channel Selection */}
                        <div className="space-y-4">
                            <label className="text-sm font-bold uppercase tracking-widest text-zinc-400 block">Select Channel</label>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                {(Object.entries(CHANNEL_LABELS) as [ChannelType, string][]).map(([key, label]) => (
                                    <button
                                        key={key}
                                        onClick={() => updateMove(pm.tempId, { channel: key })}
                                        className={cn(
                                            "w-full text-left px-4 py-4 rounded-xl border transition-all relative overflow-hidden group",
                                            pm.channel === key
                                                ? "bg-zinc-50 border-zinc-900 text-zinc-900 ring-1 ring-zinc-900 dark:bg-zinc-800 dark:border-zinc-100 dark:text-zinc-100 shadow-md scale-[1.02]"
                                                : "bg-white text-zinc-600 border-zinc-200 hover:border-zinc-300 dark:bg-zinc-900 dark:text-zinc-400 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-800"
                                        )}
                                    >
                                        <div className="font-medium relative z-10">{label}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="h-px bg-zinc-100 dark:bg-zinc-800" />

                        {/* Parameters */}
                        <div className="grid grid-cols-2 gap-8">
                            <div className="space-y-4">
                                <label className="text-sm font-bold uppercase tracking-widest text-zinc-400 block">Sprint Duration</label>
                                <div className="flex gap-2">
                                    {[7, 14, 28].map(d => (
                                        <button
                                            key={d}
                                            onClick={() => updateMove(pm.tempId, { duration: d as MoveDuration })}
                                            className={cn(
                                                "flex-1 py-3 rounded-xl border text-sm transition-all font-medium",
                                                pm.duration === d
                                                    ? "bg-zinc-50 border-zinc-900 text-zinc-900 ring-1 ring-zinc-900 dark:bg-zinc-800 dark:border-zinc-100 dark:text-zinc-100 dark:ring-zinc-100 shadow-md"
                                                    : "bg-zinc-50 border-zinc-200 text-zinc-500 hover:bg-white dark:bg-zinc-900 dark:border-zinc-800"
                                            )}
                                        >
                                            {d} days
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <label className="text-sm font-bold uppercase tracking-widest text-zinc-400 block">Daily Effort</label>
                                <div className="flex gap-2">
                                    {[15, 30, 60].map(e => (
                                        <button
                                            key={e}
                                            onClick={() => updateMove(pm.tempId, { dailyEffort: e as any })}
                                            className={cn(
                                                "flex-1 py-3 rounded-xl border text-sm transition-all font-medium",
                                                pm.dailyEffort === e
                                                    ? "bg-zinc-50 border-zinc-900 text-zinc-900 ring-1 ring-zinc-900 dark:bg-zinc-800 dark:border-zinc-100 dark:text-zinc-100 dark:ring-zinc-100 shadow-md"
                                                    : "bg-zinc-50 border-zinc-200 text-zinc-500 hover:bg-white dark:bg-zinc-900 dark:border-zinc-800"
                                            )}
                                        >
                                            {e} min
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-6xl w-[95vw] h-[90vh] p-0 overflow-hidden flex flex-col bg-zinc-50 dark:bg-zinc-950 border-none sm:rounded-3xl shadow-2xl transition-all">
                {renderHeader()}

                <div className="flex-1 overflow-y-auto p-8 relative">
                    {activeStep === 'select-goals' && (
                        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
                            {/* Campaign Context Selector */}
                            {campaigns.length > 0 && (
                                <div className="space-y-4">
                                    <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-400">Context</h3>
                                    <div className="flex gap-4 overflow-x-auto pb-2">
                                        <button
                                            onClick={() => setSelectedCampaignId('standalone')}
                                            className={cn(
                                                "flex items-center gap-3 px-6 py-4 rounded-xl border transition-all min-w-[200px]",
                                                selectedCampaignId === 'standalone' || !selectedCampaignId
                                                    ? "bg-white border-zinc-900 ring-1 ring-zinc-900 shadow-md dark:bg-zinc-900 dark:border-zinc-100 dark:ring-zinc-100"
                                                    : "bg-white/50 border-zinc-200 hover:border-zinc-400 dark:bg-zinc-900/50 dark:border-zinc-800"
                                            )}
                                        >
                                            <div className="w-10 h-10 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center">
                                                <Zap className="w-5 h-5 text-zinc-500" />
                                            </div>
                                            <div className="text-left">
                                                <div className="font-semibold text-zinc-900 dark:text-zinc-100">Standalone</div>
                                                <div className="text-xs text-zinc-500">Quick Sprint</div>
                                            </div>
                                        </button>

                                        {campaigns.map(c => (
                                            <button
                                                key={c.id}
                                                onClick={() => setSelectedCampaignId(c.id)}
                                                className={cn(
                                                    "flex items-center gap-3 px-6 py-4 rounded-xl border transition-all min-w-[240px]",
                                                    selectedCampaignId === c.id
                                                        ? "bg-white border-zinc-900 ring-1 ring-zinc-900 shadow-md dark:bg-zinc-900 dark:border-zinc-100 dark:ring-zinc-100"
                                                        : "bg-white/50 border-zinc-200 hover:border-zinc-400 dark:bg-zinc-900/50 dark:border-zinc-800"
                                                )}
                                            >
                                                <div className="w-10 h-10 rounded-full bg-indigo-50 dark:bg-indigo-900/20 flex items-center justify-center">
                                                    <Target className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                                                </div>
                                                <div className="text-left">
                                                    <div className="font-semibold text-zinc-900 dark:text-zinc-100 truncate max-w-[140px]">{c.name}</div>
                                                    <div className="text-xs text-zinc-500">{OBJECTIVE_LABELS[c.objective].label}</div>
                                                </div>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div className="space-y-4">
                                <h3 className="text-sm font-semibold uppercase tracking-widest text-zinc-400">Available Goals</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {(Object.entries(GOAL_LABELS) as [MoveGoal, { label: string; description: string }][]).map(([key, info]) => {
                                        const isSelected = pendingMoves.some(p => p.goal === key);
                                        return (
                                            <div
                                                key={key}
                                                onClick={() => handleToggleGoal(key)}
                                                className={cn(
                                                    "cursor-pointer group relative p-6 rounded-2xl border transition-all duration-200",
                                                    isSelected
                                                        ? "bg-zinc-50 border-zinc-900 ring-1 ring-zinc-900 shadow-xl scale-[1.02] dark:bg-zinc-900 dark:border-white dark:ring-white"
                                                        : "bg-white border-zinc-200 hover:border-zinc-400 hover:shadow-md dark:bg-zinc-900 dark:border-zinc-800 dark:hover:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-800/50"
                                                )}
                                            >
                                                <div className="flex justify-between items-start mb-4">
                                                    <h4 className={cn("font-display text-xl font-medium transition-colors", isSelected ? "text-zinc-900 dark:text-zinc-100" : "text-zinc-900 dark:text-zinc-100")}>{info.label}</h4>
                                                    {isSelected && (
                                                        <div className="w-6 h-6 rounded-full bg-zinc-900 text-white dark:bg-white dark:text-zinc-900 flex items-center justify-center shadow-sm">
                                                            <Check className="w-4 h-4" />
                                                        </div>
                                                    )}
                                                </div>
                                                <p className={cn(
                                                    "text-sm leading-relaxed transition-colors",
                                                    isSelected ? "text-zinc-600 dark:text-zinc-400 font-medium" : "text-zinc-500"
                                                )}>
                                                    {info.description}
                                                </p>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>
                    )}

                    {activeStep === 'configure' && renderConfigureStep()}

                    {activeStep === 'review' && (
                        <div className="max-w-2xl mx-auto space-y-8 text-center pt-8 animate-in fade-in zoom-in-95 duration-300">
                            <div className="space-y-2">
                                <h3 className="font-display text-4xl font-medium text-zinc-900 dark:text-zinc-100">Ready to Execute?</h3>
                                <p className="text-zinc-500 text-lg">You are about to launch {pendingMoves.length} strategic moves.</p>
                            </div>

                            <div className="bg-white dark:bg-zinc-900 rounded-3xl border border-zinc-200 dark:border-zinc-800 divide-y divide-zinc-100 dark:divide-zinc-800 shadow-xl text-left overflow-hidden">
                                {pendingMoves.map((pm, i) => (
                                    <div key={pm.tempId} className="p-6 flex items-center justify-between group hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors">
                                        <div className="flex items-center gap-5">
                                            <div className="w-12 h-12 rounded-2xl bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-lg font-bold text-zinc-900 dark:text-zinc-100">
                                                {i + 1}
                                            </div>
                                            <div>
                                                <h4 className="font-semibold text-lg text-zinc-900 dark:text-zinc-100">
                                                    {GOAL_LABELS[pm.goal].label}
                                                </h4>
                                                <div className="text-zinc-500 mt-1 flex items-center gap-2 text-sm">
                                                    <span className="font-medium text-zinc-700 dark:text-zinc-300">{CHANNEL_LABELS[pm.channel!]}</span>
                                                    <span className="text-zinc-300 dark:text-zinc-700">•</span>
                                                    <Clock className="w-3.5 h-3.5" />
                                                    <span>{pm.duration} days</span>
                                                </div>
                                            </div>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => {
                                                setActiveStep('configure');
                                                setActiveConfigIndex(i);
                                            }}
                                            className="text-zinc-400 group-hover:text-zinc-900 dark:group-hover:text-zinc-100"
                                        >
                                            Edit
                                        </Button>
                                    </div>
                                ))}
                            </div>

                            <div className="bg-amber-50 dark:bg-amber-900/10 p-6 rounded-2xl border border-amber-200 dark:border-amber-800/30 text-amber-800 dark:text-amber-200 text-sm flex items-start gap-3 text-left">
                                <Zap className="w-5 h-5 shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-bold mb-1">Execution Protocol</p>
                                    <p>The first move ({GOAL_LABELS[pendingMoves[0].goal].label}) will start immediately on Day 1. The remaining {pendingMoves.length - 1} moves will be queued for deployment upon completion or manual activation.</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {renderFooter()}
            </DialogContent>
        </Dialog>
    );
}
