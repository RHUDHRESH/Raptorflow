'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
    Campaign,
    CampaignObjective,
    OfferType,
    ChannelType,
    OBJECTIVE_LABELS,
    OFFER_LABELS,
    CHANNEL_LABELS,
    OBJECTIVE_GOAL_ALIGNMENT,
    Move,
    MoveGoal,
    MoveDuration
} from '@/lib/campaigns-types';
import {
    createCampaign,
    createMove,
    generateCampaignId,
    generateMoveId,
    generateDefaultChecklist
} from '@/lib/campaigns';
import { Check, ChevronDown, ChevronRight, X, ArrowRight, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

// Mock cohorts for now
const MOCK_COHORTS = [
    { id: 'c1', name: 'SaaS Founders (Seed)' },
    { id: 'c2', name: 'Marketing Agencies' },
    { id: 'c3', name: 'E-commerce Owners' },
    { id: 'c4', name: 'Enterprise CTOs' },
];

interface NewCampaignWizardProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onComplete: (campaign: Campaign) => void;
}

type Step = 'objective' | 'audience' | 'offer' | 'channels' | 'pace' | 'preview';

export function NewCampaignWizard({ open, onOpenChange, onComplete }: NewCampaignWizardProps) {
    // Form State
    const [objective, setObjective] = useState<CampaignObjective | null>(null);
    const [cohortId, setCohortId] = useState<string | null>(null);
    const [cohortName, setCohortName] = useState<string>('');
    const [offer, setOffer] = useState<OfferType | null>(null);
    const [channels, setChannels] = useState<ChannelType[]>([]);
    const [duration, setDuration] = useState<MoveDuration>(14); // Default Move Length
    const [campaignDuration, setCampaignDuration] = useState<90 | 28 | 14>(90);
    const [dailyEffort, setDailyEffort] = useState<15 | 30 | 60>(30);

    // Flow State
    const [activeStep, setActiveStep] = useState<Step>('objective');
    const [previewMoves, setPreviewMoves] = useState<Move[]>([]);

    // Reset on open
    useEffect(() => {
        if (open) {
            setObjective(null);
            setCohortId(null);
            setCohortName('');
            setOffer(null);
            setChannels([]);
            setDuration(14);
            setCampaignDuration(90);
            setActiveStep('objective');
            setPreviewMoves([]);
        }
    }, [open]);

    // Generate preview when all required fields are set
    useEffect(() => {
        if (objective && cohortId && offer && channels.length > 0) {
            generatePreview();
        }
    }, [objective, cohortId, offer, channels, duration]);

    const generatePreview = () => {
        if (!objective || !offer || channels.length === 0) return;

        // Smart generation of moves based on objective
        const moves: Move[] = [];
        const goals = OBJECTIVE_GOAL_ALIGNMENT[objective];

        // Move 1: Setup & Initial Push
        moves.push({
            id: 'preview-1',
            name: 'Foundation & Launch Sprint',
            goal: goals[0] || 'distribution',
            channel: channels[0],
            duration: 7, // Shorter start
            dailyEffort,
            status: 'draft',
            createdAt: new Date().toISOString(),
            checklist: [],
            assetIds: [],
        });

        // Move 2: Core Execution
        moves.push({
            id: 'preview-2',
            name: `Core ${OBJECTIVE_LABELS[objective].label} Cycle`,
            goal: goals[1] || goals[0] || 'leads',
            channel: channels[0],
            duration: duration,
            dailyEffort,
            status: 'draft',
            createdAt: new Date().toISOString(),
            checklist: [],
            assetIds: [],
        });

        // Move 3: Optimization / Expand
        moves.push({
            id: 'preview-3',
            name: channels.length > 1 ? `Expand to ${CHANNEL_LABELS[channels[1]]}` : 'Optimization Sprint',
            goal: goals[2] || goals[0] || 'sales',
            channel: channels[1] || channels[0],
            duration: duration,
            dailyEffort,
            status: 'draft',
            createdAt: new Date().toISOString(),
            checklist: [],
            assetIds: [],
        });

        setPreviewMoves(moves);
    };

    const handleCreate = () => {
        if (!objective || !cohortId || !offer) return;

        const campaignId = generateCampaignId();
        const now = new Date().toISOString();

        // Create Campaign
        const newCampaign: Campaign = {
            id: campaignId,
            name: `${OBJECTIVE_LABELS[objective].label} ${cohortName}`, // e.g. "Acquire SaaS Founders"
            objective,
            cohortId,
            cohortName,
            offer,
            channels,
            duration: campaignDuration,
            moveLength: duration as 7 | 14,
            dailyEffort,
            status: 'active',
            createdAt: now,
            startedAt: now,
        };

        createCampaign(newCampaign);

        // Create Real Moves from Preview
        previewMoves.forEach((pm, index) => {
            const moveId = generateMoveId();
            const realMove: Move = {
                ...pm,
                id: moveId,
                campaignId,
                campaignName: newCampaign.name,
                status: index === 0 ? 'active' : 'queued', // Start Move 1 immediately
                createdAt: now,
                startedAt: index === 0 ? now : undefined,
                dueDate: index === 0 ? new Date(Date.now() + pm.duration * 24 * 60 * 60 * 1000).toISOString() : undefined,
                checklist: generateDefaultChecklist(pm.goal, pm.channel, pm.duration as MoveDuration),
            };
            createMove(realMove);
        });

        toast.success('Campaign created and Move 1 started');
        onComplete(newCampaign);
    };

    // Render Steps
    const renderObjectiveStep = () => (
        <div className="space-y-4">
            <h3 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                1. What is the single outcome you want?
            </h3>
            <div className="grid grid-cols-2 gap-3">
                {(Object.entries(OBJECTIVE_LABELS) as [CampaignObjective, { label: string; description: string }][]).map(([key, info]) => (
                    <button
                        key={key}
                        onClick={() => {
                            setObjective(key);
                            setActiveStep('audience');
                        }}
                        className={`text-left p-4 rounded-xl border transition-all ${objective === key
                            ? 'bg-zinc-900 border-zinc-900 text-white dark:bg-zinc-100 dark:border-zinc-100 dark:text-zinc-900'
                            : 'bg-white border-zinc-200 text-zinc-600 hover:border-zinc-300 dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-400 dark:hover:border-zinc-700'
                            }`}
                    >
                        <div className="font-semibold mb-1">{info.label}</div>
                        <div className={`text-xs ${objective === key ? 'text-zinc-300 dark:text-zinc-500' : 'text-zinc-500'}`}>
                            {info.description}
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );

    const renderAudienceStep = () => (
        <div className="space-y-4">
            <h3 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                2. Who is this for?
            </h3>
            <div className="space-y-2">
                {MOCK_COHORTS.map(cohort => (
                    <button
                        key={cohort.id}
                        onClick={() => {
                            setCohortId(cohort.id);
                            setCohortName(cohort.name);
                            setActiveStep('offer');
                        }}
                        className={`w-full text-left p-3 rounded-lg border flex items-center justify-between ${cohortId === cohort.id
                            ? 'bg-zinc-50 border-zinc-900 text-zinc-900 dark:bg-zinc-800 dark:border-zinc-100 dark:text-zinc-100'
                            : 'bg-white border-zinc-200 text-zinc-600 hover:border-zinc-300 dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-400'
                            }`}
                    >
                        <span>{cohort.name}</span>
                        {cohortId === cohort.id && <Check className="w-4 h-4" />}
                    </button>
                ))}
                <button
                    className="w-full text-left p-3 rounded-lg border border-dashed border-zinc-300 text-zinc-500 hover:text-zinc-800 hover:border-zinc-400 dark:border-zinc-700 dark:text-zinc-500 dark:hover:text-zinc-300"
                    onClick={() => toast('Quick cohort creation coming soon')}
                >
                    + Create new cohort
                </button>
            </div>
        </div>
    );

    const renderOfferStep = () => (
        <div className="space-y-4">
            <h3 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                3. What are you asking them to do?
            </h3>
            <div className="flex flex-wrap gap-2">
                {(Object.entries(OFFER_LABELS) as [OfferType, string][]).map(([key, label]) => (
                    <button
                        key={key}
                        onClick={() => {
                            setOffer(key);
                            setActiveStep('channels');
                        }}
                        className={`px-4 py-2 rounded-full border text-sm transition-colors ${offer === key
                            ? 'bg-zinc-900 border-zinc-900 text-white dark:bg-zinc-100 dark:border-zinc-100 dark:text-zinc-900'
                            : 'bg-white border-zinc-200 text-zinc-600 hover:border-zinc-300 dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-400'
                            }`}
                    >
                        {label}
                    </button>
                ))}
            </div>
        </div>
    );

    const renderChannelsStep = () => (
        <div className="space-y-4">
            <h3 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                4. Where will you run this? (Max 2)
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {(Object.entries(CHANNEL_LABELS) as [ChannelType, string][]).map(([key, label]) => {
                    const isSelected = channels.includes(key);
                    return (
                        <button
                            key={key}
                            onClick={() => {
                                let newChannels = [...channels];
                                if (isSelected) {
                                    newChannels = newChannels.filter(c => c !== key);
                                } else {
                                    if (newChannels.length >= 2) return; // Max 2
                                    newChannels.push(key);
                                }
                                setChannels(newChannels);
                            }}
                            disabled={!isSelected && channels.length >= 2}
                            className={`p-3 rounded-lg border text-sm text-left transition-colors ${isSelected
                                ? 'bg-zinc-900 border-zinc-900 text-white dark:bg-zinc-100 dark:border-zinc-100 dark:text-zinc-900'
                                : channels.length >= 2
                                    ? 'opacity-50 cursor-not-allowed border-zinc-100 text-zinc-300 dark:border-zinc-800 dark:text-zinc-600'
                                    : 'bg-white border-zinc-200 text-zinc-600 hover:border-zinc-300 dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-400'
                                }`}
                        >
                            {label}
                        </button>
                    );
                })}
            </div>
            {channels.length > 0 && (
                <div className="flex justify-end">
                    <Button onClick={() => setActiveStep('pace')} variant="outline" size="sm">
                        Confirm Channels <ArrowRight className="w-3 h-3 ml-2" />
                    </Button>
                </div>
            )}
        </div>
    );

    const renderPaceStep = () => (
        <div className="space-y-6">
            <h3 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                5. How do you want to run it?
            </h3>

            {/* Campaign Duration */}
            <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">Campaign Duration</label>
                <div className="flex gap-2">
                    {[14, 28, 90].map(days => (
                        <button
                            key={days}
                            onClick={() => setCampaignDuration(days as any)}
                            className={`flex-1 py-2 rounded-lg border text-sm ${campaignDuration === days
                                ? 'bg-zinc-100 border-zinc-300 text-zinc-900 font-medium dark:bg-zinc-800 dark:border-zinc-600 dark:text-zinc-100'
                                : 'border-zinc-200 text-zinc-500 hover:bg-zinc-50 dark:border-zinc-800 dark:text-zinc-500'
                                }`}
                        >
                            {days} days
                        </button>
                    ))}
                </div>
            </div>

            {/* Move Length */}
            <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">Move Length</label>
                <div className="flex gap-2">
                    {[7, 14].map(days => (
                        <button
                            key={days}
                            onClick={() => setDuration(days as MoveDuration)}
                            className={`flex-1 py-2 rounded-lg border text-sm ${duration === days
                                ? 'bg-zinc-100 border-zinc-300 text-zinc-900 font-medium dark:bg-zinc-800 dark:border-zinc-600 dark:text-zinc-100'
                                : 'border-zinc-200 text-zinc-500 hover:bg-zinc-50 dark:border-zinc-800 dark:text-zinc-500'
                                }`}
                        >
                            {days} days
                        </button>
                    ))}
                </div>
            </div>

            {/* Daily Effort */}
            <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">Daily Effort</label>
                <div className="flex gap-2">
                    {[15, 30, 60].map(mins => (
                        <button
                            key={mins}
                            onClick={() => setDailyEffort(mins as any)}
                            className={`flex-1 py-2 rounded-lg border text-sm ${dailyEffort === mins
                                ? 'bg-zinc-100 border-zinc-300 text-zinc-900 font-medium dark:bg-zinc-800 dark:border-zinc-600 dark:text-zinc-100'
                                : 'border-zinc-200 text-zinc-500 hover:bg-zinc-50 dark:border-zinc-800 dark:text-zinc-500'
                                }`}
                        >
                            {mins}m / day
                        </button>
                    ))}
                </div>
            </div>

            <Button onClick={() => setActiveStep('preview')} className="w-full">
                Review Plan
            </Button>
        </div>
    );

    const renderPreview = () => (
        <div className="space-y-6">
            <div className="bg-zinc-50 dark:bg-zinc-900/50 p-4 rounded-xl space-y-2 border border-zinc-100 dark:border-zinc-800">
                <h3 className="font-display font-semibold text-xl text-zinc-900 dark:text-zinc-100">
                    {objective && OBJECTIVE_LABELS[objective].label} Campaign
                </h3>
                <div className="flex flex-wrap gap-2 text-xs text-zinc-500">
                    <span className="bg-white dark:bg-zinc-800 px-2 py-1 rounded border border-zinc-200 dark:border-zinc-700">{cohortName}</span>
                    <span className="bg-white dark:bg-zinc-800 px-2 py-1 rounded border border-zinc-200 dark:border-zinc-700">{channels.map(c => CHANNEL_LABELS[c]).join(' + ')}</span>
                    <span className="bg-white dark:bg-zinc-800 px-2 py-1 rounded border border-zinc-200 dark:border-zinc-700">{campaignDuration} days</span>
                </div>
            </div>

            <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-widest text-zinc-400">Your First 3 Moves</h4>
                {previewMoves.map((move, i) => (
                    <div key={i} className="flex gap-4 p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl relative overflow-hidden">
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-zinc-200 dark:bg-zinc-800" />
                        <div className="flex-1">
                            <h5 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-1">
                                {i === 0 && <span className="text-emerald-600 mr-2">● Active Now</span>}
                                {move.name}
                            </h5>
                            <p className="text-xs text-zinc-500">
                                {move.duration} days • {move.dailyEffort}m/day • {move.checklist?.length || 0} tasks
                            </p>
                        </div>
                        {i === 0 && (
                            <div className="flex items-center text-emerald-600 text-xs font-medium">
                                <Sparkles className="w-3 h-3 mr-1" /> Ready
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );

    // Collapsed Card Component
    const CollapsedCard = ({ step, label, value, onClick }: { step: Step, label: string, value: string, onClick: () => void }) => (
        <button
            onClick={onClick}
            className="w-full flex items-center justify-between p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl hover:border-zinc-300 dark:hover:border-zinc-700 transition-colors"
        >
            <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-500 text-xs">
                    <Check className="w-3 h-3" />
                </div>
                <div className="text-sm font-medium text-zinc-600 dark:text-zinc-400">{label}</div>
            </div>
            <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">{value}</span>
                <ChevronDown className="w-4 h-4 text-zinc-400" />
            </div>
        </button>
    );

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-xl p-0 gap-0 bg-zinc-50 dark:bg-zinc-950 max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="p-6 border-b border-zinc-200 dark:border-zinc-800 sticky top-0 bg-zinc-50/80 dark:bg-zinc-950/80 backdrop-blur-md z-10">
                    <h2 className="font-display text-2xl font-semibold mb-1">Create Campaign</h2>
                    <p className="text-sm text-zinc-500">A campaign is a 90-day initiative executed through weekly Moves.</p>
                </div>

                <div className="p-6 space-y-4">
                    {/* Step 1: Objective */}
                    {activeStep === 'objective' ? (
                        <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl shadow-sm border border-zinc-200 dark:border-zinc-800">
                            {renderObjectiveStep()}
                        </div>
                    ) : objective && (
                        <CollapsedCard
                            step="objective"
                            label="Objective"
                            value={OBJECTIVE_LABELS[objective].label}
                            onClick={() => setActiveStep('objective')}
                        />
                    )}

                    {/* Step 2: Audience */}
                    {objective && (
                        activeStep === 'audience' ? (
                            <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl shadow-sm border border-zinc-200 dark:border-zinc-800 animate-in fade-in slide-in-from-bottom-2">
                                {renderAudienceStep()}
                            </div>
                        ) : cohortId && (
                            <CollapsedCard
                                step="audience"
                                label="Audience"
                                value={cohortName}
                                onClick={() => setActiveStep('audience')}
                            />
                        )
                    )}

                    {/* Step 3: Offer */}
                    {cohortId && (
                        activeStep === 'offer' ? (
                            <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl shadow-sm border border-zinc-200 dark:border-zinc-800 animate-in fade-in slide-in-from-bottom-2">
                                {renderOfferStep()}
                            </div>
                        ) : offer && (
                            <CollapsedCard
                                step="offer"
                                label="Offer"
                                value={OFFER_LABELS[offer]}
                                onClick={() => setActiveStep('offer')}
                            />
                        )
                    )}

                    {/* Step 4: Channels */}
                    {offer && (
                        activeStep === 'channels' ? (
                            <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl shadow-sm border border-zinc-200 dark:border-zinc-800 animate-in fade-in slide-in-from-bottom-2">
                                {renderChannelsStep()}
                            </div>
                        ) : channels.length > 0 && (
                            <CollapsedCard
                                step="channels"
                                label="Channels"
                                value={channels.map(c => CHANNEL_LABELS[c]).join(', ')}
                                onClick={() => setActiveStep('channels')}
                            />
                        )
                    )}

                    {/* Step 5: Pace */}
                    {channels.length > 0 && (
                        activeStep === 'pace' ? (
                            <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl shadow-sm border border-zinc-200 dark:border-zinc-800 animate-in fade-in slide-in-from-bottom-2">
                                {renderPaceStep()}
                            </div>
                        ) : (activeStep === 'preview' || previewMoves.length > 0) && (
                            <CollapsedCard
                                step="pace"
                                label="Pace"
                                value={`${campaignDuration}d / ${duration}d moves`}
                                onClick={() => setActiveStep('pace')}
                            />
                        )
                    )}

                    {/* Preview Step */}
                    {activeStep === 'preview' && (
                        <div className="animate-in fade-in slide-in-from-bottom-4">
                            {renderPreview()}
                        </div>
                    )}
                </div>

                {/* Footer Actions */}
                <div className="p-6 border-t border-zinc-200 dark:border-zinc-800 sticky bottom-0 bg-zinc-50 dark:bg-zinc-950 flex justify-between items-center z-10">
                    <button
                        onClick={() => onOpenChange(false)}
                        className="text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-300"
                    >
                        Cancel
                    </button>

                    {activeStep === 'preview' && (
                        <Button
                            onClick={handleCreate}
                            className="bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900"
                        >
                            Create Campaign & Start Move 1
                        </Button>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
