'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { GoalSelector } from './GoalSelector';
import { RiskSlider } from './RiskSlider';
import { GoalType, RiskLevel, ChannelType, Experiment, ExperimentStatus } from '@/lib/blackbox-types';
import { ArrowLeft, ArrowRight, Sparkles, Box, X, Mail, Linkedin, Twitter, MessageSquare, Video, Globe, RefreshCcw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { generateExperiments } from '@/lib/blackbox/generator';
import { addExperiment } from '@/lib/blackbox';
import { toast } from 'sonner';

interface BlackBoxWizardProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onComplete: (experiments: Experiment[]) => void;
}

type WizardStep = 'goal' | 'risk' | 'channel' | 'generating' | 'results';

const CHANNELS = [
    { id: 'email' as ChannelType, label: 'Email', icon: Mail },
    { id: 'linkedin' as ChannelType, label: 'LinkedIn', icon: Linkedin },
    { id: 'twitter' as ChannelType, label: 'Twitter/X', icon: Twitter },
    { id: 'whatsapp' as ChannelType, label: 'WhatsApp', icon: MessageSquare },
    { id: 'youtube' as ChannelType, label: 'YouTube', icon: Video },
    { id: 'other' as ChannelType, label: 'Other', icon: Globe },
];

const EXPERIMENT_TEMPLATES = {
    friction: [
        { title: 'Ask for a reply, not a click', bet: 'Remove all links. Ask them to reply with a number instead.', why: 'Reduces friction + increases commitment' },
        { title: 'One-line signup', bet: 'Strip your CTA to a single sentence with zero navigation.', why: 'Less choices = more action' },
    ],
    pattern_interrupt: [
        { title: 'The Anti-Design Confession', bet: 'Send a plain-text email with one embarrassing business truth.', why: 'Pattern interrupt + authenticity signal' },
        { title: 'Ugly ad experiment', bet: 'Use deliberately low-fi creative that looks unpolished.', why: 'Stands out in polished content' },
    ],
    social_proof: [
        { title: 'Steal My Template Hook', bet: 'Offer a high-value checklist in exchange for a specific comment.', why: 'Social proof + reciprocity' },
        { title: 'What 17 founders did', bet: 'Lead with aggregated proof from real people.', why: 'Herd effect reduces perceived risk' },
    ],
    identity: [
        { title: 'People like you do X', bet: 'Open with identity-based framing that makes reader self-select.', why: 'Identity triggers are powerful' },
        { title: 'Founder Confession', bet: 'Share a real mistake you made and what you learned.', why: 'Vulnerability builds trust' },
    ],
    loss_aversion: [
        { title: 'You are leaking money here', bet: 'Lead with what they are losing, not what they will gain.', why: 'Loss aversion is 2x stronger than gain' },
        { title: 'Most teams miss this', bet: 'Frame around regret prevention, not opportunity.', why: 'Fear of missing out drives action' },
    ],
    commitment: [
        { title: 'Micro-yes ladder', bet: 'Ask a tiny yes-or-no question before the real ask.', why: 'Small commitments lead to bigger ones' },
        { title: '2-step ask', bet: 'First ask for advice, then follow up with the real request.', why: 'Consistency principle' },
    ],
};

const PRINCIPLES = Object.keys(EXPERIMENT_TEMPLATES) as Array<keyof typeof EXPERIMENT_TEMPLATES>;

export function BlackBoxWizard({ open, onOpenChange, onComplete }: BlackBoxWizardProps) {
    const [step, setStep] = useState<WizardStep>('goal');
    const [goal, setGoal] = useState<GoalType | null>(null);
    const [risk, setRisk] = useState<RiskLevel | null>(null);
    const [channel, setChannel] = useState<ChannelType | null>(null);
    const [generatedExperiments, setGeneratedExperiments] = useState<Experiment[]>([]);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        if (open) {
            setStep('goal');
            setGoal(null);
            setRisk(null);
            setChannel(null);
            setGeneratedExperiments([]);
            setProgress(0);
        }
    }, [open]);

    const handleGenerate = () => {
        if (!goal || !risk || !channel) return;
        setStep('generating');
        setProgress(0);

        const interval = setInterval(() => {
            setProgress(prev => prev >= 100 ? (clearInterval(interval), 100) : prev + 12);
        }, 150);

        setTimeout(() => {
            clearInterval(interval);

            // Use real generator
            const experiments = generateExperiments({
                goal,
                risk_level: risk,
                channel
            }, 3);

            setGeneratedExperiments(experiments);
            setStep('results');
        }, 1800);
    };

    const handleNext = () => {
        if (step === 'goal' && goal) setStep('risk');
        else if (step === 'risk' && risk) setStep('channel');
        else if (step === 'channel' && channel) handleGenerate();
    };

    const handleBack = () => {
        if (step === 'risk') setStep('goal');
        else if (step === 'channel') setStep('risk');
    };

    const handleComplete = () => {
        try {
            generatedExperiments.forEach(e => addExperiment(e));
            toast.success('Experiments added to draft');
            onComplete(generatedExperiments);
            onOpenChange(false);
        } catch (err) {
            toast.error('Failed to save experiments');
        }
    };

    const canProceed = (step === 'goal' && !!goal) || (step === 'risk' && !!risk) || (step === 'channel' && !!channel);
    const stepNum = step === 'goal' ? 1 : step === 'risk' ? 2 : 3;

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-xl p-0 gap-0 bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-xl rounded-2xl overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-100 dark:border-zinc-900">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-zinc-900 dark:bg-white flex items-center justify-center">
                            <Box className="w-4 h-4 text-white dark:text-zinc-900" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-sm font-sans">New Black Box</h3>
                            <p className="text-[10px] text-zinc-400 font-sans">
                                {step === 'generating' ? 'Generating...' : step === 'results' ? 'Ready' : `Step ${stepNum} of 3`}
                            </p>
                        </div>
                    </div>
                    <button onClick={() => onOpenChange(false)} className="w-6 h-6 rounded flex items-center justify-center hover:bg-zinc-100 dark:hover:bg-zinc-900">
                        <X className="w-4 h-4 text-zinc-400" />
                    </button>
                </div>

                {/* Progress */}
                <div className="h-0.5 bg-zinc-100 dark:bg-zinc-900">
                    <div className="h-full bg-zinc-900 dark:bg-white transition-all" style={{ width: step === 'results' ? '100%' : step === 'generating' ? `${progress}%` : `${stepNum * 33}%` }} />
                </div>

                {/* Content */}
                <div className="p-6 min-h-[340px] flex items-center justify-center">
                    {step === 'goal' && <GoalSelector selectedGoal={goal} onSelect={setGoal} />}
                    {step === 'risk' && <RiskSlider value={risk} onChange={setRisk} />}

                    {step === 'channel' && (
                        <div className="w-full space-y-5 text-center">
                            <div>
                                <h2 className="text-xl font-semibold mb-1 font-sans">Where will you run these?</h2>
                                <p className="text-sm text-zinc-500 font-sans">Pick your primary channel.</p>
                            </div>
                            <div className="grid grid-cols-3 gap-2 max-w-md mx-auto">
                                {CHANNELS.map((ch) => {
                                    const Icon = ch.icon;
                                    return (
                                        <button
                                            key={ch.id}
                                            onClick={() => setChannel(ch.id)}
                                            className={cn(
                                                "flex flex-col items-center gap-1.5 p-4 rounded-xl border-2 transition-all",
                                                channel === ch.id
                                                    ? "bg-zinc-900 border-zinc-900 text-white dark:bg-white dark:text-zinc-900"
                                                    : "border-zinc-200 hover:border-zinc-400 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400"
                                            )}
                                        >
                                            <Icon className="w-5 h-5" />
                                            <span className="text-xs font-medium font-sans">{ch.label}</span>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {step === 'generating' && (
                        <div className="text-center space-y-4">
                            <div className="w-14 h-14 mx-auto rounded-xl bg-zinc-900 dark:bg-white flex items-center justify-center">
                                <Sparkles className="w-7 h-7 text-white dark:text-zinc-900 animate-pulse" />
                            </div>
                            <p className="text-sm text-zinc-500 font-sans">Generating experiments...</p>
                        </div>
                    )}

                    {step === 'results' && (
                        <div className="w-full space-y-4">
                            <div className="text-center">
                                <h2 className="text-xl font-semibold mb-1 font-sans">Ready</h2>
                                <p className="text-sm text-zinc-500 font-sans">3 experiments for <span className="font-medium text-zinc-700 dark:text-zinc-300">{goal}</span> via <span className="font-medium text-zinc-700 dark:text-zinc-300">{channel}</span></p>
                            </div>
                            <div className="space-y-2">
                                {generatedExperiments.map((e, i) => (
                                    <div key={e.id} className="flex items-center gap-3 p-3 bg-zinc-50 dark:bg-zinc-900 rounded-lg border border-zinc-100 dark:border-zinc-800">
                                        <span className="w-6 h-6 rounded bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 flex items-center justify-center text-xs font-bold font-mono">{i + 1}</span>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium truncate font-sans">{e.title}</p>
                                            <p className="text-[10px] text-zinc-400 uppercase tracking-wide font-sans">{e.principle.replace('_', ' ')}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between px-6 py-4 border-t border-zinc-100 dark:border-zinc-900 bg-zinc-50/50 dark:bg-zinc-900/50">
                    <Button variant="ghost" onClick={handleBack} disabled={step === 'goal' || step === 'generating'} className={cn("rounded-lg font-sans", step === 'goal' && "invisible")}>
                        <ArrowLeft className="w-4 h-4 mr-1" /> Back
                    </Button>

                    {step !== 'results' && step !== 'generating' && (
                        <Button onClick={handleNext} disabled={!canProceed} className="rounded-lg bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 px-5 font-sans">
                            {step === 'channel' ? 'Generate' : 'Next'} <ArrowRight className="w-4 h-4 ml-1" />
                        </Button>
                    )}

                    {step === 'results' && (
                        <Button onClick={handleComplete} className="rounded-lg bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 px-5 font-sans">
                            <Sparkles className="w-4 h-4 mr-1.5" /> Start Experiments
                        </Button>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
