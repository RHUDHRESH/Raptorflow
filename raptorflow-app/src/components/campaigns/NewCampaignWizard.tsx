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
    generateDefaultChecklist,
    triggerCampaignInference
} from '@/lib/campaigns';
import { getMovesForContext } from '@/lib/move-templates';
import { Check, ChevronDown, ChevronRight, X, ArrowRight, Sparkles, LayoutPanelLeft, ShieldCheck, Edit3, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import { ArcPreview } from './ArcPreview';
import { Badge } from "@/components/ui/badge";
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

type Step = 'objective' | 'audience' | 'offer' | 'channels' | 'pace' | 'approval' | 'preview';

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
    const [isGenerating, setIsGenerating] = useState(false);
    const [generationStatus, setGenerationStatus] = useState<string>('idle');

    // ... (rest of the state)

    const pollStatus = async (campaignId: string) => {
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`/api/v1/campaigns/generate-arc/${campaignId}/status`);
                if (res.ok) {
                    const data = await res.json();
                    setGenerationStatus(data.status);
                    if (data.status === 'completed' || data.status === 'failed') {
                        clearInterval(interval);
                    }
                }
            } catch (err) {
                console.error("Status polling failed:", err);
            }
        }, 2000);
    };

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
            setIsGenerating(false);
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

        // Use move templates for rich, actionable moves
        const templates = getMovesForContext(objective, channels, 3);
        const goals = OBJECTIVE_GOAL_ALIGNMENT[objective];

        const moves: Move[] = templates.map((template, index) => ({
            id: `preview-${index + 1}`,
            name: template.name,
            goal: template.goal || goals[index] || 'leads',
            channel: channels[Math.min(index, channels.length - 1)],
            duration: index === 0 ? 7 : duration, // First move shorter
            dailyEffort,
            status: 'draft',
            createdAt: new Date().toISOString(),
            checklist: [],
            assetIds: [],
            // Rich actionable details from template
            hypothesis: template.hypothesis,
            control: template.control,
            variant: template.variant,
            success_metric: template.success_metric,
            sample_size: template.sample_size,
            action_steps: template.action_steps,
        }));

        setPreviewMoves(moves);
    };

    const handleNext = () => {
        if (activeStep === 'objective' && objective) setActiveStep('audience');
        else if (activeStep === 'audience' && cohortId) setActiveStep('offer');
        else if (activeStep === 'offer' && offer) setActiveStep('channels');
        else if (activeStep === 'channels' && channels.length > 0) setActiveStep('pace');
        else if (activeStep === 'pace') {
            setIsGenerating(true);
            setTimeout(() => {
                setIsGenerating(false);
                setActiveStep('approval');
            }, 1500);
        }
    };

    const handleBack = () => {
        if (activeStep === 'audience') setActiveStep('objective');
        else if (activeStep === 'offer') setActiveStep('audience');
        else if (activeStep === 'channels') setActiveStep('offer');
        else if (activeStep === 'pace') setActiveStep('channels');
        else if (activeStep === 'approval') setActiveStep('pace');
    };

    const handleCreate = async () => {
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

        try {
            await createCampaign(newCampaign);

            // Task 16: Trigger SOTA agentic inference for the 90-day arc
            toast.promise(triggerCampaignInference(campaignId), {
                loading: 'Finalizing 90-day strategic arc...',
                success: 'Strategic arc deployed and moves populated',
                error: 'Failed to generate arc, using basic template'
            });

            // Create Real Moves from Preview
            for (const [index, pm] of previewMoves.entries()) {
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
                await createMove(realMove);
            }

            onComplete(newCampaign);
        } catch (error) {
            toast.error('Failed to create campaign');
            console.error(error);
        }
    };

    // Render Steps
    const renderObjectiveStep = () => (
        <div className="space-y-6">
            <div>
                <h3 className="text-xl font-serif text-stone-800 mb-1">Select Primary Objective</h3>
                <p className="text-xs text-stone-500 font-sans">The single outcome that defines campaign success.</p>
            </div>
            <div className="grid grid-cols-1 gap-3">
                {(Object.entries(OBJECTIVE_LABELS) as [CampaignObjective, { label: string; description: string }][]).map(([key, info]) => (
                    <button
                        key={key}
                        onClick={() => {
                            setObjective(key);
                        }}
                        className={`text-left p-4 rounded-xl border transition-all duration-300 ${objective === key
                            ? 'bg-stone-900 border-stone-900 text-white shadow-md'
                            : 'bg-white border-stone-200 text-stone-600 hover:border-stone-400'
                            }`}
                    >
                        <div className="flex items-center justify-between">
                            <div className="font-bold text-sm tracking-tight">{info.label}</div>
                            {objective === key && <Check className="w-4 h-4 text-stone-100" />}
                        </div>
                        <div className={`text-[11px] mt-1 ${objective === key ? 'text-stone-400' : 'text-stone-500'}`}>
                            {info.description}
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );

    const renderAudienceStep = () => (
        <div className="space-y-6">
            <div>
                <h3 className="text-xl font-serif text-stone-800 mb-1">Target Cohort</h3>
                <p className="text-xs text-stone-500 font-sans">Who are we talking to in this initiative?</p>
            </div>
            <div className="space-y-2">
                {MOCK_COHORTS.map(cohort => (
                    <button
                        key={cohort.id}
                        onClick={() => {
                            setCohortId(cohort.id);
                            setCohortName(cohort.name);
                        }}
                        className={`w-full text-left p-4 rounded-xl border flex items-center justify-between transition-all duration-300 ${cohortId === cohort.id
                            ? 'bg-stone-900 border-stone-900 text-white shadow-md'
                            : 'bg-white border-stone-200 text-stone-600 hover:border-stone-400'
                            }`}
                    >
                        <span className="text-sm font-bold">{cohort.name}</span>
                        {cohortId === cohort.id && <Check className="w-4 h-4 text-stone-100" />}
                    </button>
                ))}
                <button
                    className="w-full text-left p-4 rounded-xl border border-dashed border-stone-300 text-stone-400 hover:text-stone-800 hover:border-stone-400 transition-colors"
                    onClick={() => toast('Quick cohort creation coming soon')}
                >
                    <span className="text-sm">+ Create new cohort</span>
                </button>
            </div>
        </div>
    );

    const renderOfferStep = () => (
        <div className="space-y-6">
            <div>
                <h3 className="text-xl font-serif text-stone-800 mb-1">The Offer</h3>
                <p className="text-xs text-stone-500 font-sans">The specific value exchange or call to action.</p>
            </div>
            <div className="flex flex-wrap gap-2">
                {(Object.entries(OFFER_LABELS) as [OfferType, string][]).map(([key, label]) => (
                    <button
                        key={key}
                        onClick={() => {
                            setOffer(key);
                        }}
                        className={`px-5 py-2.5 rounded-full border text-sm font-medium transition-all duration-300 ${offer === key
                            ? 'bg-stone-900 border-stone-900 text-white shadow-md'
                            : 'bg-white border-stone-200 text-stone-600 hover:border-stone-400'
                            }`}
                    >
                        {label}
                    </button>
                ))}
            </div>
        </div>
    );

    const renderChannelsStep = () => (
        <div className="space-y-6">
            <div>
                <h3 className="text-xl font-serif text-stone-800 mb-1">Distribution Channels</h3>
                <p className="text-xs text-stone-500 font-sans">Pick up to 2 primary channels for this campaign.</p>
            </div>
            <div className="grid grid-cols-2 gap-2">
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
                            className={`p-4 rounded-xl border text-sm text-left transition-all duration-300 ${isSelected
                                ? 'bg-stone-900 border-stone-900 text-white shadow-md'
                                : channels.length >= 2
                                    ? 'opacity-50 cursor-not-allowed border-stone-50 text-stone-300'
                                    : 'bg-white border-stone-200 text-stone-600 hover:border-stone-400'
                                }`}
                        >
                            <div className="font-bold">{label}</div>
                        </button>
                    );
                })}
            </div>
        </div>
    );

    const renderPaceStep = () => (
        <div className="space-y-8">
            <div>
                <h3 className="text-xl font-serif text-stone-800 mb-1">Execution Pacing</h3>
                <p className="text-xs text-stone-500 font-sans">Define your duration and operational capacity.</p>
            </div>

            {/* Campaign Duration */}
            <div className="space-y-3">
                <label className="text-[10px] font-bold uppercase tracking-[0.2em] text-stone-400">Total Campaign Length</label>
                <div className="flex gap-2">
                    {[14, 28, 90].map(days => (
                        <button
                            key={days}
                            onClick={() => setCampaignDuration(days as any)}
                            className={`flex-1 py-3 rounded-xl border text-sm transition-all duration-300 ${campaignDuration === days
                                ? 'bg-stone-900 border-stone-900 text-white shadow-md'
                                : 'bg-white border-stone-200 text-stone-500 hover:border-stone-400'
                                }`}
                        >
                            {days} Days
                        </button>
                    ))}
                </div>
            </div>

            {/* Move Length */}
            <div className="space-y-3">
                <label className="text-[10px] font-bold uppercase tracking-[0.2em] text-stone-400">Iteration (Move) Frequency</label>
                <div className="flex gap-2">
                    {[7, 14].map(days => (
                        <button
                            key={days}
                            onClick={() => setDuration(days as MoveDuration)}
                            className={`flex-1 py-3 rounded-xl border text-sm transition-all duration-300 ${duration === days
                                ? 'bg-stone-900 border-stone-900 text-white shadow-md'
                                : 'bg-white border-stone-200 text-stone-500 hover:border-stone-400'
                                }`}
                        >
                            Every {days} Days
                        </button>
                    ))}
                </div>
            </div>

            {/* Daily Effort */}
            <div className="space-y-3">
                <label className="text-[10px] font-bold uppercase tracking-[0.2em] text-stone-400">Operational Capacity</label>
                <div className="flex gap-2">
                    {[15, 30, 60].map(mins => (
                        <button
                            key={mins}
                            onClick={() => setDailyEffort(mins as any)}
                            className={`flex-1 py-3 rounded-xl border text-sm transition-all duration-300 ${dailyEffort === mins
                                ? 'bg-stone-900 border-stone-900 text-white shadow-md'
                                : 'bg-white border-stone-200 text-stone-500 hover:border-stone-400'
                                }`}
                        >
                            {mins}m / Day
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );

    const renderApprovalStep = () => (
        <div className="space-y-8 animate-in fade-in zoom-in-95 duration-500">
            <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-full bg-emerald-50 border border-emerald-100 flex items-center justify-center mx-auto mb-4">
                    <ShieldCheck className="w-6 h-6 text-emerald-600" />
                </div>
                <h3 className="text-2xl font-serif text-stone-800">Human Approval Required</h3>
                <p className="text-sm text-stone-500 font-sans max-w-sm mx-auto">
                    The Cognitive Intelligence Engine has drafted your 90-day arc. Please review the moves on the right.
                </p>
            </div>

            <div className="p-6 bg-stone-50 rounded-2xl border border-stone-100 space-y-4">
                <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-widest text-stone-400">
                    <span>Strategic Summary</span>
                    <Badge variant="outline" className="bg-white border-stone-200 text-stone-500">DRAFT</Badge>
                </div>
                <p className="text-sm text-stone-700 leading-relaxed italic">
                    &ldquo;Based on your goal of <strong>{objective && OBJECTIVE_LABELS[objective].label}</strong> for <strong>{cohortName}</strong>,
                    this arc focuses on {previewMoves[0]?.hypothesis?.split(' ').slice(0, 8).join(' ')}...&rdquo;
                </p>
                <div className="grid grid-cols-2 gap-4 pt-2">
                    <div className="space-y-1">
                        <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Est. ROI</span>
                        <div className="text-lg font-bold text-stone-800">+24%</div>
                    </div>
                    <div className="space-y-1">
                        <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Complexity</span>
                        <div className="text-lg font-bold text-stone-800">Medium</div>
                    </div>
                </div>
            </div>

            <div className="flex items-center space-x-3">
                <Button
                    variant="outline"
                    className="flex-1 rounded-xl h-12 border-stone-200 hover:bg-stone-50"
                    onClick={() => setActiveStep('pace')}
                >
                    <Edit3 className="w-4 h-4 mr-2" /> Refine Setup
                </Button>
                <Button
                    className="flex-1 rounded-xl h-12 bg-stone-900 hover:bg-black text-white"
                    onClick={handleCreate}
                >
                    Approve & Launch
                </Button>
            </div>
        </div>
    );

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-6xl p-0 gap-0 bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-2xl rounded-3xl overflow-hidden transition-all duration-500 h-[85vh]">
                <div className="flex h-full">
                    {/* Left: Input Wizard (40%) */}
                    <div className="w-[450px] border-r border-stone-100 flex flex-col bg-white">
                        {/* Header */}
                        <div className="px-8 py-6 border-b border-stone-50 flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 rounded-xl bg-stone-900 flex items-center justify-center">
                                    <LayoutPanelLeft className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h2 className="text-sm font-bold uppercase tracking-widest text-stone-800">Campaign Wizard</h2>
                                    <p className="text-[10px] text-stone-400 font-sans">BUILDER PHASE</p>
                                </div>
                            </div>
                            <button onClick={() => onOpenChange(false)} className="w-8 h-8 rounded-full hover:bg-stone-50 flex items-center justify-center transition-colors">
                                <X className="w-4 h-4 text-stone-300" />
                            </button>
                        </div>

                        {/* Wizard Content */}
                        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                            {isGenerating ? (
                                <div className="h-full flex flex-col items-center justify-center space-y-4 text-center">
                                    <div className="w-16 h-16 rounded-2xl bg-stone-50 flex items-center justify-center relative overflow-hidden">
                                        <div className="absolute inset-0 bg-stone-900/5 animate-pulse" />
                                        <Sparkles className="w-8 h-8 text-stone-300 animate-bounce" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-serif text-stone-800">Agentic Brainstorming...</h3>
                                        <p className="text-xs text-stone-400 max-w-[200px]">Simulating 90 days of marketing momentum based on your constraints.</p>
                                    </div>
                                </div>
                            ) : (
                                <>
                                    {activeStep === 'objective' && renderObjectiveStep()}
                                    {activeStep === 'audience' && renderAudienceStep()}
                                    {activeStep === 'offer' && renderOfferStep()}
                                    {activeStep === 'channels' && renderChannelsStep()}
                                    {activeStep === 'pace' && renderPaceStep()}
                                    {activeStep === 'approval' && renderApprovalStep()}
                                </>
                            )}
                        </div>

                        {/* Footer Nav */}
                        {activeStep !== 'approval' && !isGenerating && (
                            <div className="px-8 py-6 border-t border-stone-50 flex items-center justify-between bg-stone-50/30">
                                <Button
                                    variant="ghost"
                                    onClick={handleBack}
                                    disabled={activeStep === 'objective'}
                                    className={cn("rounded-lg text-stone-400", activeStep === 'objective' && "invisible")}
                                >
                                    <ArrowLeft className="w-4 h-4 mr-2" /> Back
                                </Button>
                                <Button
                                    onClick={handleNext}
                                    disabled={(activeStep === 'objective' && !objective) ||
                                              (activeStep === 'audience' && !cohortId) ||
                                              (activeStep === 'offer' && !offer) ||
                                              (activeStep === 'channels' && channels.length === 0)}
                                    className="rounded-xl bg-stone-900 text-white hover:bg-black px-6 h-11"
                                >
                                    {activeStep === 'pace' ? 'Generate Arc' : 'Next'} <ArrowRight className="w-4 h-4 ml-2" />
                                </Button>
                            </div>
                        )}
                    </div>

                    {/* Right: Dynamic Preview (60%) */}
                    <div className="flex-1 bg-stone-50/50 p-10 overflow-hidden flex flex-col">
                        <ArcPreview
                            moves={previewMoves}
                            duration={campaignDuration}
                            objective={objective ? OBJECTIVE_LABELS[objective].label : 'your objective'}
                        />
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}

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
        <div className="space-y-6 max-h-[400px] overflow-y-auto">
            <div className="bg-zinc-50 dark:bg-zinc-900/50 p-4 rounded-xl space-y-2 border border-zinc-100 dark:border-zinc-800 sticky top-0">
                <h3 className="font-display font-semibold text-xl text-zinc-900 dark:text-zinc-100">
                    {objective && OBJECTIVE_LABELS[objective].label} Campaign
                </h3>
                <div className="flex flex-wrap gap-2 text-xs text-zinc-500">
                    <span className="bg-white dark:bg-zinc-800 px-2 py-1 rounded border border-zinc-200 dark:border-zinc-700">{cohortName}</span>
                    <span className="bg-white dark:bg-zinc-800 px-2 py-1 rounded border border-zinc-200 dark:border-zinc-700">{channels.map(c => CHANNEL_LABELS[c]).join(' + ')}</span>
                    <span className="bg-white dark:bg-zinc-800 px-2 py-1 rounded border border-zinc-200 dark:border-zinc-700">{campaignDuration} days</span>
                </div>
            </div>

            <div className="space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-widest text-zinc-400">Your First 3 Moves</h4>
                {previewMoves.map((move, i) => (
                    <div key={i} className="p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl">
                        {/* Header */}
                        <div className="flex items-start gap-3 mb-3">
                            <span className="w-7 h-7 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 flex items-center justify-center text-sm font-bold flex-shrink-0">
                                {i + 1}
                            </span>
                            <div className="flex-1">
                                <h5 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100">
                                    {i === 0 && <span className="text-emerald-600 mr-2">●</span>}
                                    {move.name}
                                </h5>
                                <p className="text-[10px] text-zinc-400 uppercase tracking-wide">
                                    {move.duration} days • {move.dailyEffort}m/day • {CHANNEL_LABELS[move.channel]}
                                </p>
                            </div>
                        </div>

                        {/* Hypothesis */}
                        {move.hypothesis && (
                            <div className="mb-3 p-3 bg-zinc-50 dark:bg-zinc-950 rounded-lg border border-zinc-100 dark:border-zinc-800">
                                <p className="text-[10px] text-zinc-400 uppercase tracking-wide mb-1">Hypothesis</p>
                                <p className="text-xs font-sans text-zinc-700 dark:text-zinc-300">{move.hypothesis}</p>
                            </div>
                        )}

                        {/* Control vs Variant */}
                        {move.control && move.variant && (
                            <div className="grid grid-cols-2 gap-2 mb-3">
                                <div className="p-2 bg-zinc-50 dark:bg-zinc-950 rounded-lg border border-zinc-100 dark:border-zinc-800">
                                    <p className="text-[10px] text-red-500 uppercase tracking-wide mb-1">Control (A)</p>
                                    <p className="text-[11px] text-zinc-600 dark:text-zinc-400">{move.control}</p>
                                </div>
                                <div className="p-2 bg-zinc-50 dark:bg-zinc-950 rounded-lg border border-zinc-100 dark:border-zinc-800">
                                    <p className="text-[10px] text-green-500 uppercase tracking-wide mb-1">Variant (B)</p>
                                    <p className="text-[11px] text-zinc-600 dark:text-zinc-400">{move.variant}</p>
                                </div>
                            </div>
                        )}

                        {/* Metrics row */}
                        {move.success_metric && (
                            <div className="flex gap-2 mb-3">
                                <div className="flex-1 p-2 bg-zinc-50 dark:bg-zinc-950 rounded-lg border border-zinc-100 dark:border-zinc-800 text-center">
                                    <p className="text-[10px] text-zinc-400 uppercase tracking-wide">Metric</p>
                                    <p className="text-[11px] font-medium">{move.success_metric}</p>
                                </div>
                                <div className="flex-1 p-2 bg-zinc-50 dark:bg-zinc-950 rounded-lg border border-zinc-100 dark:border-zinc-800 text-center">
                                    <p className="text-[10px] text-zinc-400 uppercase tracking-wide">Sample</p>
                                    <p className="text-[11px] font-medium">{move.sample_size}</p>
                                </div>
                            </div>
                        )}

                        {/* Action Steps */}
                        {move.action_steps && move.action_steps.length > 0 && (
                            <details className="group">
                                <summary className="text-xs text-zinc-500 cursor-pointer hover:text-zinc-700 dark:hover:text-zinc-300 flex items-center gap-1">
                                    <span className="group-open:rotate-90 transition-transform">▶</span>
                                    {move.action_steps.length} Action Steps
                                </summary>
                                <ol className="mt-2 space-y-1 pl-4 text-[11px] text-zinc-600 dark:text-zinc-400 list-decimal list-inside">
                                    {move.action_steps.map((step, si) => (
                                        <li key={si} className="leading-relaxed">{step}</li>
                                    ))}
                                </ol>
                            </details>
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
