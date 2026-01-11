"use client";

import { useState } from "react";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";
import { ArrowRight, Loader2, Sparkles, Zap, Shield, Box, Crosshair } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   CAMPAIGN ARCHITECT (WIZARD)
   Refactored to "The Brief" -> "The Proposal" flow.
   ══════════════════════════════════════════════════════════════════════════════ */

interface CampaignConstitutionWizardProps {
    isOpen: boolean;
    onClose: () => void;
    onComplete: (data: any) => void;
}

type Step = 'brief' | 'processing' | 'proposal' | 'ratify';

export function CampaignConstitutionWizard({ isOpen, onClose, onComplete }: CampaignConstitutionWizardProps) {
    const [step, setStep] = useState<Step>('brief');
    const [isLoading, setIsLoading] = useState(false);

    // Form State
    const [objective, setObjective] = useState("Product Launch");
    const [duration, setDuration] = useState(12); // Weeks
    const [stakes, setStakes] = useState("");

    // Proposal State
    const [selectedStrategy, setSelectedStrategy] = useState<string>("siege"); // blitz, siege, trojan

    const STRATEGIES = [
        {
            id: 'blitz',
            icon: Zap,
            title: 'The Blitz',
            tagline: 'High volume. Maximum noise. Short duration.',
            risk: 'High',
            idea: "You aren't selling a product; you're creating a moment. Flood the zone."
        },
        {
            id: 'siege',
            icon: Shield,
            title: 'The Siege',
            tagline: 'Slow authority build. Hard backend push.',
            risk: 'Low',
            idea: "They don't trust you yet. Teach them until they beg to buy."
        },
        {
            id: 'trojan',
            icon: Box, // Wooden horse approx
            title: 'The Trojan Horse',
            tagline: 'Lead with entertainment. Sell on the backend.',
            risk: 'Medium',
            idea: "Big Idea: You aren't selling software; you are selling Friday afternoons off."
        }
    ];

    const handleGenerate = async () => {
        setStep('processing');
        await new Promise(resolve => setTimeout(resolve, 2500)); // Simulate Senator thinking
        setStep('proposal');
    };

    const handleRatify = async () => {
        setIsLoading(true);
        await new Promise(resolve => setTimeout(resolve, 1000));
        onComplete({ objective, duration, stakes, strategy: selectedStrategy });
        setIsLoading(false);
        onClose();
    };

    // --- Renders ---

    const renderBrief = () => (
        <div className="space-y-8 animate-in slide-in-from-right-4 duration-300 max-w-md mx-auto">
            <div className="space-y-6">
                {/* Objective */}
                <div className="space-y-2">
                    <label className="font-technical text-[var(--ink)] uppercase text-xs tracking-wider">01 // The Objective</label>
                    <select
                        value={objective}
                        onChange={(e) => setObjective(e.target.value)}
                        className="w-full bg-[var(--surface)] text-[var(--ink)] text-xl p-4 rounded-[var(--radius)] border border-[var(--border)] focus:ring-[var(--blueprint)] focus:outline-none"
                    >
                        <option>Product Launch</option>
                        <option>Brand Re-positioning</option>
                        <option>Crisis Management</option>
                        <option>General Growth</option>
                    </select>
                </div>

                {/* Duration */}
                <div className="space-y-4">
                    <div className="flex justify-between">
                        <label className="font-technical text-[var(--ink)] uppercase text-xs tracking-wider">02 // Duration</label>
                        <span className="font-mono text-[var(--blueprint)] font-bold">{duration} Weeks</span>
                    </div>
                    <input
                        type="range"
                        min="4" max="24" step="4"
                        value={duration}
                        onChange={(e) => setDuration(Number(e.target.value))}
                        className="w-full accent-[var(--blueprint)]"
                    />
                    <div className="flex justify-between text-[10px] text-[var(--muted)] font-mono">
                        <span>4 WKS</span>
                        <span>8 WKS</span>
                        <span>12 WKS (REC)</span>
                        <span>6 MOS</span>
                    </div>
                </div>

                {/* Stakes */}
                <div className="space-y-2">
                    <label className="font-technical text-[var(--ink)] uppercase text-xs tracking-wider">03 // The Stakes</label>
                    <textarea
                        value={stakes}
                        onChange={(e) => setStakes(e.target.value)}
                        placeholder="What happens if this fails? What do they misunderstand about you?"
                        className="w-full bg-[var(--surface)] p-4 rounded-[var(--radius)] border border-[var(--border)] min-h-[120px] focus:ring-[var(--blueprint)] focus:outline-none text-sm resize-none"
                    />
                </div>
            </div>

            <div className="pt-4">
                <button
                    onClick={handleGenerate}
                    className="w-full py-4 bg-[var(--ink)] text-white font-bold tracking-widest rounded-[var(--radius)] hover:scale-[1.01] transition-transform flex items-center justify-center gap-3 shadow-xl"
                >
                    <Sparkles size={18} />
                    GENERATE STRATEGY
                </button>
            </div>
        </div>
    );

    const renderProcessing = () => (
        <div className="flex flex-col items-center justify-center h-[400px] space-y-6 text-center animate-in fade-in duration-500">
            <div className="relative">
                <div className="w-24 h-24 border-4 border-[var(--border)] rounded-full animate-[spin_8s_linear_infinite]" />
                <div className="absolute inset-0 border-t-4 border-[var(--blueprint)] rounded-full animate-[spin_2s_linear_infinite]" />
                <Crosshair className="absolute inset-0 m-auto text-[var(--blueprint)] animate-pulse" size={32} />
            </div>
            <div>
                <h3 className="font-technical text-lg text-[var(--ink)] animate-pulse">SENATOR_AI IS THINKING...</h3>
                <p className="text-[var(--ink-secondary)] font-mono text-xs mt-2">
                    Applying Game Theory...<br />
                    analyzing_competitor_vectors...<br />
                    Simulating 400 outcomes...
                </p>
            </div>
        </div>
    );

    const renderProposal = () => (
        <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
            <div className="text-center mb-8">
                <h2 className="font-serif text-3xl text-[var(--ink)]">Strategy Generated</h2>
                <p className="text-[var(--muted)] text-sm mt-1">Based on your {duration}-week timeline, here are the viable paths.</p>
            </div>

            <div className="grid grid-cols-3 gap-4">
                {STRATEGIES.map(strat => {
                    const isSelected = selectedStrategy === strat.id;
                    return (
                        <div
                            key={strat.id}
                            onClick={() => setSelectedStrategy(strat.id)}
                            className={cn(
                                "relative p-6 rounded-[var(--radius)] border-2 cursor-pointer transition-all duration-300 flex flex-col gap-4 group hover:-translate-y-1 h-[320px]",
                                isSelected
                                    ? "bg-[var(--surface)] border-[var(--blueprint)] shadow-xl ring-1 ring-[var(--blueprint)]"
                                    : "bg-white border-[var(--border)] opacity-80 hover:opacity-100 hover:border-[var(--ink-muted)]"
                            )}
                        >
                            {isSelected && <div className="absolute top-3 right-3 text-[var(--blueprint)] animate-in zoom-in"><CheckCircle2 size={24} /></div>}

                            <div className={cn(
                                "w-12 h-12 rounded-full flex items-center justify-center transition-colors",
                                isSelected ? "bg-[var(--blueprint)] text-white" : "bg-[var(--surface)] text-[var(--ink)]"
                            )}>
                                <strat.icon size={24} />
                            </div>

                            <div>
                                <h3 className="font-bold text-lg text-[var(--ink)]">{strat.title}</h3>
                                <div className={cn(
                                    "text-xs font-mono uppercase mt-1 inline-block px-1.5 py-0.5 rounded",
                                    strat.risk === 'High' ? "bg-red-100 text-red-700" : strat.risk === 'Low' ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                                )}>
                                    {strat.risk} Risk
                                </div>
                            </div>

                            <p className="text-sm text-[var(--ink-secondary)] leading-relaxed">
                                {strat.tagline}
                            </p>

                            {isSelected && (
                                <div className="mt-auto pt-4 border-t border-[var(--border)] animate-in fade-in slide-in-from-bottom-2">
                                    <p className="text-xs font-serif italic text-[var(--ink)]">
                                        "{strat.idea}"
                                    </p>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );

    function CheckCircle2(props: any) { return <svg {...props} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><path d="m9 12 2 2 4-4" /></svg> }

    return (
        <BlueprintModal
            isOpen={isOpen}
            onClose={onClose}
            title={step === 'brief' ? "The Brief" : step === 'proposal' ? "The Proposal" : "System Processing"}
            figure="ARCHITECT"
            code="STRAT-GEN"
            size={step === 'proposal' ? 'xl' : 'lg'}
            footer={
                step === 'proposal' ? (
                    <div className="flex justify-between items-center w-full">
                        <SecondaryButton onClick={() => setStep('brief')}>Back to Brief</SecondaryButton>
                        <BlueprintButton onClick={handleRatify}>
                            Accept Strategy & Initialize
                            <ArrowRight size={16} />
                        </BlueprintButton>
                    </div>
                ) : null
            }
        >
            <div className="min-h-[450px] py-4">
                {step === 'brief' && renderBrief()}
                {step === 'processing' && renderProcessing()}
                {step === 'proposal' && renderProposal()}
            </div>
        </BlueprintModal>
    );
}
