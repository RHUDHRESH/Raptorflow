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
import { Check, ChevronRight, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

interface NewMoveWizardProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onComplete: (move: Move) => void;
}

type Step = 'context' | 'goal' | 'channel' | 'details' | 'validation';

export function NewMoveWizard({ open, onOpenChange, onComplete }: NewMoveWizardProps) {
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);

    // Form State
    const [selectedCampaignId, setSelectedCampaignId] = useState<string | 'standalone' | null>(null);
    const [goal, setGoal] = useState<MoveGoal | null>(null);
    const [channel, setChannel] = useState<ChannelType | null>(null);
    const [duration, setDuration] = useState<MoveDuration>(7);
    const [dailyEffort, setDailyEffort] = useState<15 | 30 | 60>(30);

    // Logic State
    const [activeStep, setActiveStep] = useState<Step>('context');
    const [validationWarning, setValidationWarning] = useState<string | null>(null);
    const [overrideReason, setOverrideReason] = useState<OverrideReason | null>(null);

    useEffect(() => {
        if (open) {
            setCampaigns(getCampaigns().filter(c => c.status === 'active' || c.status === 'planned'));
            setSelectedCampaignId(null);
            setGoal(null);
            setChannel(null);
            setDuration(7);
            setDailyEffort(30);
            setActiveStep('context');
            setValidationWarning(null);
            setOverrideReason(null);
        }
    }, [open]);

    const handleCreate = () => {
        if (!goal || !channel) return;

        const moveId = generateMoveId();
        const now = new Date().toISOString();
        const campaign = campaigns.find(c => c.id === selectedCampaignId);

        // Check active move conflict
        const isGlobalActive = !!getActiveMove();

        const newMove: Move = {
            id: moveId,
            name: `${GOAL_LABELS[goal].label} Sprint`,
            goal,
            channel,
            duration,
            dailyEffort,
            status: isGlobalActive ? 'queued' : 'active',
            campaignId: campaign?.id,
            campaignName: campaign?.name,
            createdAt: now,
            startedAt: isGlobalActive ? undefined : now,
            dueDate: isGlobalActive ? undefined : new Date(Date.now() + duration * 24 * 60 * 60 * 1000).toISOString(),
            checklist: generateDefaultChecklist(goal, channel, duration),
            assetIds: [],
        };

        // If validation warning was overridden, log it
        if (validationWarning && overrideReason && campaign) {
            newMove.override = {
                reason: overrideReason,
                originalCampaignObjective: campaign.objective,
                loggedAt: now
            };
            logMoveOverride(newMove, campaign, overrideReason);
        }

        createMove(newMove);
        if (!isGlobalActive) {
            setActiveMove(moveId);
            toast.success('Move created and started');
        } else {
            toast.success('Move created and queued (another move is active)');
        }

        onComplete(newMove);
    };

    const validateAlignment = (selectedGoal: MoveGoal) => {
        if (selectedCampaignId === 'standalone' || !selectedCampaignId) return true;

        const campaign = campaigns.find(c => c.id === selectedCampaignId);
        if (!campaign) return true;

        if (!isGoalAligned(campaign.objective, selectedGoal)) {
            setValidationWarning(`This Move (${GOAL_LABELS[selectedGoal].label}) doesn't align with your campaign objective (${OBJECTIVE_LABELS[campaign.objective].label}).`);
            return false;
        }
        return true;
    };

    const nextStep = (target: Step) => {
        setActiveStep(target);
    };

    // Render Steps
    const renderContextStep = () => (
        <div className="space-y-4">
            <h3 className="text-lg font-medium">Where is this Move coming from?</h3>
            <div className="space-y-3">
                {campaigns.length > 0 && (
                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-zinc-500 uppercase">From Campaign</label>
                        {campaigns.map(c => (
                            <button
                                key={c.id}
                                onClick={() => {
                                    setSelectedCampaignId(c.id);
                                    nextStep('goal');
                                }}
                                className="w-full text-left p-4 rounded-xl border border-zinc-200 hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700 bg-white dark:bg-zinc-900 transition-all"
                            >
                                <div className="font-medium text-zinc-900 dark:text-zinc-100">{c.name}</div>
                                <div className="text-xs text-zinc-500">{OBJECTIVE_LABELS[c.objective].label} • Week 3</div>
                            </button>
                        ))}
                    </div>
                )}

                <button
                    onClick={() => {
                        setSelectedCampaignId('standalone');
                        nextStep('goal');
                    }}
                    className="w-full text-left p-4 rounded-xl border border-dashed border-zinc-300 hover:border-zinc-400 dark:border-zinc-700 dark:hover:border-zinc-600 bg-transparent transition-all group"
                >
                    <div className="font-medium text-zinc-600 dark:text-zinc-400 group-hover:text-zinc-900 dark:group-hover:text-zinc-200">Standalone Move</div>
                    <div className="text-xs text-zinc-500">Quick sprint without a campaign</div>
                </button>
            </div>
        </div>
    );

    const renderGoalStep = () => (
        <div className="space-y-4">
            <h3 className="text-lg font-medium">What are you trying to accomplish?</h3>
            <div className="grid grid-cols-2 gap-3">
                {(Object.entries(GOAL_LABELS) as [MoveGoal, { label: string; description: string }][]).map(([key, info]) => (
                    <button
                        key={key}
                        onClick={() => {
                            setGoal(key);
                            if (validateAlignment(key)) {
                                nextStep('channel');
                            } else {
                                nextStep('validation');
                            }
                        }}
                        className="text-left p-4 rounded-xl border border-zinc-200 hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700 bg-white dark:bg-zinc-900 transition-all"
                    >
                        <div className="font-semibold text-zinc-900 dark:text-zinc-100 mb-1">{info.label}</div>
                        <div className="text-xs text-zinc-500">{info.description}</div>
                    </button>
                ))}
            </div>
        </div>
    );

    const renderValidationStep = () => (
        <div className="space-y-6">
            <div className="bg-amber-50 dark:bg-amber-900/20 p-6 rounded-2xl border border-amber-200 dark:border-amber-800/50 flex flex-col items-center text-center">
                <div className="w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-800/50 flex items-center justify-center text-amber-600 dark:text-amber-400 mb-4">
                    <AlertTriangle className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-amber-900 dark:text-amber-100 mb-2">Strategy Mismatch</h3>
                <p className="text-amber-800 dark:text-amber-300 mb-6 max-w-sm">
                    {validationWarning}
                    <br /> Running this may dilute your results.
                </p>

                <div className="w-full space-y-3">
                    <div className="text-left w-full space-y-2">
                        <label className="text-xs font-semibold text-amber-800 dark:text-amber-300 uppercase">Reason for override</label>
                        <div className="grid grid-cols-1 gap-2">
                            {(Object.entries(OVERRIDE_LABELS) as [OverrideReason, string][]).map(([reason, label]) => (
                                <button
                                    key={reason}
                                    onClick={() => setOverrideReason(reason)}
                                    className={`p-3 rounded-lg border text-sm text-left transition-colors ${overrideReason === reason
                                        ? 'bg-amber-100 border-amber-300 text-amber-900 dark:bg-amber-800 dark:border-amber-600 dark:text-amber-100'
                                        : 'bg-white border-zinc-200 text-zinc-600 dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-400'
                                        }`}
                                >
                                    {label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <Button
                        onClick={() => nextStep('channel')}
                        disabled={!overrideReason}
                        className="w-full bg-amber-600 hover:bg-amber-700 text-white"
                    >
                        Run Anyway
                    </Button>
                    <Button
                        variant="ghost"
                        onClick={() => {
                            setGoal(null);
                            setValidationWarning(null);
                            setOverrideReason(null);
                            nextStep('goal');
                        }}
                        className="w-full text-zinc-500"
                    >
                        Go Back
                    </Button>
                </div>
            </div>
        </div>
    );

    const renderChannelStep = () => (
        <div className="space-y-4">
            <h3 className="text-lg font-medium">Where will you execute?</h3>
            <div className="grid grid-cols-2 gap-3">
                {(Object.entries(CHANNEL_LABELS) as [ChannelType, string][]).map(([key, label]) => (
                    <button
                        key={key}
                        onClick={() => {
                            setChannel(key);
                            nextStep('details');
                        }}
                        className="p-4 rounded-xl border border-zinc-200 hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700 bg-white dark:bg-zinc-900 transition-all text-left"
                    >
                        <div className="font-medium text-zinc-900 dark:text-zinc-100">{label}</div>
                    </button>
                ))}
            </div>
        </div>
    );

    const renderDetailsStep = () => (
        <div className="space-y-6">
            <h3 className="text-lg font-medium">Finalize Move</h3>

            <div className="space-y-4">
                <div className="space-y-2">
                    <label className="text-sm font-medium">Duration</label>
                    <div className="flex gap-2">
                        {[7, 14, 28].map(d => (
                            <button
                                key={d}
                                onClick={() => setDuration(d as MoveDuration)}
                                className={`flex-1 py-2 rounded-lg border text-sm ${duration === d
                                    ? 'bg-zinc-900 text-white border-zinc-900 dark:bg-white dark:text-zinc-900'
                                    : 'bg-white text-zinc-600 border-zinc-200 dark:bg-zinc-900 dark:text-zinc-400 dark:border-zinc-800'
                                    }`}
                            >
                                {d} days
                            </button>
                        ))}
                    </div>
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-medium">Daily Effort</label>
                    <div className="flex gap-2">
                        {[15, 30, 60].map(e => (
                            <button
                                key={e}
                                onClick={() => setDailyEffort(e as any)}
                                className={`flex-1 py-2 rounded-lg border text-sm ${dailyEffort === e
                                    ? 'bg-zinc-900 text-white border-zinc-900 dark:bg-white dark:text-zinc-900'
                                    : 'bg-white text-zinc-600 border-zinc-200 dark:bg-zinc-900 dark:text-zinc-400 dark:border-zinc-800'
                                    }`}
                            >
                                {e} min
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            <div className="bg-zinc-50 dark:bg-zinc-900/50 p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-widest text-zinc-400">Preview</h4>
                <div className="font-medium text-zinc-900 dark:text-zinc-100">
                    {goal && GOAL_LABELS[goal].label} Sprint
                </div>
                <div className="text-xs text-zinc-500">
                    {channel && CHANNEL_LABELS[channel]} • {duration} days
                    {selectedCampaignId !== 'standalone' && selectedCampaignId && ` • Linked to Campaign`}
                </div>
            </div>

            <Button onClick={handleCreate} className="w-full bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 h-10">
                Create Move & Start Day 1
            </Button>
        </div>
    );

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-md p-0 gap-0 bg-zinc-50 dark:bg-zinc-950 overflow-hidden">
                <div className="p-6 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
                    <h2 className="font-display text-2xl font-semibold mb-1">New Move</h2>
                    <p className="text-sm text-zinc-500">Create a tactical execution packet.</p>
                </div>

                <div className="p-6">
                    {activeStep === 'context' && renderContextStep()}
                    {activeStep === 'goal' && renderGoalStep()}
                    {activeStep === 'validation' && renderValidationStep()}
                    {activeStep === 'channel' && renderChannelStep()}
                    {activeStep === 'details' && renderDetailsStep()}
                </div>
            </DialogContent>
        </Dialog>
    );
}
