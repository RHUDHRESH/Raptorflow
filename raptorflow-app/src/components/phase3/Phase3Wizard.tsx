'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Phase3Data, emptyPhase3, loadFoundationDB, saveFoundation, FoundationData } from '@/lib/foundation';
import { derivePhase3, derivePhase3FromQuestionnaire } from '@/lib/phase3-derivation';
import { PhaseScreen, PhaseStep } from '@/components/phase-shared';
import { Button } from '@/components/ui/button';
import { Check, ArrowRight, Minus, Plus, Star, AlertCircle, ChevronDown, ChevronUp, Copy, Zap } from 'lucide-react';
import { toast } from 'sonner';

type Phase3Screen = 'differentiators' | 'claims' | 'complete';

const STEPS: PhaseStep[] = [
    { id: 'differentiators', label: 'Differentiators' },
    { id: 'claims', label: 'Claims' },
    { id: 'complete', label: 'Complete' },
];

const SCREEN_CONTENT: Record<Phase3Screen, { title: string; subtitle: string }> = {
    differentiators: {
        title: 'Your Differentiators',
        subtitle: 'What makes you meaningfully different.'
    },
    claims: {
        title: 'Your Claims',
        subtitle: 'Positioning statements forged from differentiation.'
    },
    complete: {
        title: 'Blueprint Complete',
        subtitle: 'Ready to power your positioning.'
    },
};

// Proof Strength calculation
function getProofStrength(proof: string[] | undefined): { score: number; label: string; color: string } {
    if (!proof || proof.length === 0) return { score: 0, label: 'UNPROVEN', color: '#DC2626' };
    if (proof.length === 1) return { score: 30, label: 'WEAK', color: '#F59E0B' };
    if (proof.length === 2) return { score: 60, label: 'MEDIUM', color: '#9D9F9F' };
    return { score: 100, label: 'STRONG', color: '#2D3538' };
}

// Copy to clipboard helper
function copyToClipboard(text: string, label: string) {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied!`, { description: 'Paste it in your pitch deck.' });
}

// Generic competitor claims by industry
function getCompetitorClaim(industry?: string): string {
    const genericClaims = [
        "We help businesses grow faster with our solution.",
        "The all-in-one platform for modern teams.",
        "Trusted by thousands of companies worldwide.",
        "Save time and money with our innovative approach.",
        "The easiest way to manage your workflow."
    ];
    return genericClaims[Math.floor(Math.random() * genericClaims.length)];
}

export function Phase3Wizard() {
    const router = useRouter();
    const [foundation, setFoundation] = useState<FoundationData | null>(null);
    const [phase3, setPhase3] = useState<Phase3Data>(emptyPhase3);
    const [currentScreen, setCurrentScreen] = useState<Phase3Screen>('differentiators');
    const [isLoading, setIsLoading] = useState(true);
    const [isProcessing, setIsProcessing] = useState(false);
    const [showErrc, setShowErrc] = useState(false);
    const [competitorClaim] = useState(getCompetitorClaim());

    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await loadFoundationDB();
                setFoundation(data);

                if (data.phase3) {
                    setPhase3(data.phase3);
                } else if (data.completedAt || data.phase1) {
                    setIsProcessing(true);
                    const derived = data.phase1
                        ? await derivePhase3(data.phase1)
                        : await derivePhase3FromQuestionnaire(data);
                    setPhase3(derived);
                    setIsProcessing(false);
                }

                setIsLoading(false);
            } catch (error) {
                console.error('Error loading foundation:', error);
                toast.error('Failed to load data');
                setIsLoading(false);
            }
        };

        loadData();
    }, []);

    const savePhase3 = useCallback(async (data: Phase3Data) => {
        if (!foundation) return;
        try {
            await saveFoundation({ ...foundation, phase3: data });
        } catch (error) {
            console.error('Error saving phase3:', error);
        }
    }, [foundation]);

    const currentIndex = STEPS.findIndex(s => s.id === currentScreen);

    const goNext = () => {
        if (currentIndex < STEPS.length - 1) {
            setCurrentScreen(STEPS[currentIndex + 1].id as Phase3Screen);
            savePhase3(phase3);
        }
    };

    const goBack = () => {
        if (currentIndex > 0) {
            setCurrentScreen(STEPS[currentIndex - 1].id as Phase3Screen);
        } else {
            router.push('/foundation');
        }
    };

    const handleStepClick = (stepId: string) => {
        const stepIndex = STEPS.findIndex(s => s.id === stepId);
        if (stepIndex <= currentIndex) {
            setCurrentScreen(stepId as Phase3Screen);
        }
    };

    const handleLock = async () => {
        const lockedData = { ...phase3, lockedAt: new Date().toISOString() };
        setPhase3(lockedData);
        await savePhase3(lockedData);
        toast.success('Blueprint locked!');
        router.push('/foundation/phase4');
    };

    if (isLoading || isProcessing) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="text-center space-y-6">
                    <div className="w-16 h-16 border-[3px] border-[#2D3538] border-t-transparent rounded-full animate-spin mx-auto" />
                    <p className="font-serif text-2xl text-[#2D3538]">
                        {isProcessing ? 'Deriving blueprint...' : 'Loading...'}
                    </p>
                </div>
            </div>
        );
    }

    if (!foundation?.phase1 && !foundation?.completedAt) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="text-center space-y-8 max-w-md px-8">
                    <AlertCircle className="w-12 h-12 text-[#2D3538] mx-auto" />
                    <h1 className="font-serif text-3xl text-[#2D3538]">Complete Foundation First</h1>
                    <Button
                        onClick={() => router.push('/foundation')}
                        className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-2xl"
                    >
                        Go to Foundation
                    </Button>
                </div>
            </div>
        );
    }

    const { title, subtitle } = SCREEN_CONTENT[currentScreen];

    const getContextString = () => {
        if (typeof phase3.primaryContext === 'string') return phase3.primaryContext;
        if (phase3.primaryContext?.youSell) {
            return `You sell ${phase3.primaryContext.youSell} to ${phase3.primaryContext.to}`;
        }
        return null;
    };

    const primaryClaim = phase3.claims?.find(c => c.id === phase3.primaryClaimId)?.promise || phase3.claims?.[0]?.promise || 'Your positioning claim';

    return (
        <PhaseScreen
            phaseNumber={3}
            phaseTitle="Differentiation Blueprint"
            currentStepId={currentScreen}
            steps={STEPS}
            title={title}
            subtitle={subtitle}
            onBack={goBack}
            onStepClick={handleStepClick}
            showContinue={currentScreen !== 'complete'}
            continueText="Continue"
            onContinue={goNext}
        >
            {/* Screen 1: Differentiators */}
            {currentScreen === 'differentiators' && (
                <div className="space-y-6">
                    {/* Context Card */}
                    {getContextString() && (
                        <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-xl p-4 flex items-center gap-3">
                            <div className="w-2 h-2 rounded-full bg-[#2D3538]" />
                            <p className="text-sm text-[#5B5F61]">{getContextString()}</p>
                        </div>
                    )}

                    {/* Differentiators with Proof Strength Bar */}
                    <div className="space-y-4">
                        {(phase3.differentiators || [
                            { id: '1', capability: 'Unique capability', mechanism: 'How it works', proof: [], status: 'unproven' },
                        ]).map((diff, i) => {
                            const proofStrength = getProofStrength(diff.proof);
                            return (
                                <div
                                    key={diff.id || i}
                                    className="bg-white border border-[#E5E6E3] rounded-2xl p-8 transition-all hover:shadow-lg group"
                                >
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="flex items-center gap-3">
                                            <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                                #{i + 1}
                                            </span>
                                        </div>
                                        {/* Copy Button */}
                                        <button
                                            onClick={() => copyToClipboard(`${diff.capability}: ${diff.mechanism}`, 'Differentiator')}
                                            className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-[#F3F4EE] rounded-lg"
                                        >
                                            <Copy className="w-4 h-4 text-[#9D9F9F]" />
                                        </button>
                                    </div>

                                    <h3 className="font-serif text-xl text-[#2D3538] mb-2">{diff.capability}</h3>
                                    <p className="text-[#5B5F61] mb-4">{diff.mechanism}</p>

                                    {/* Proof Strength Bar */}
                                    <div className="pt-4 border-t border-[#E5E6E3]">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-[10px] font-mono uppercase tracking-[0.1em] text-[#9D9F9F]">
                                                Proof Strength
                                            </span>
                                            <span
                                                className="text-[10px] font-mono uppercase tracking-[0.1em] font-medium"
                                                style={{ color: proofStrength.color }}
                                            >
                                                {proofStrength.label}
                                            </span>
                                        </div>
                                        {/* Proof Strength Bar - Improved visibility */}
                                        <div className="relative h-3 bg-[#E5E6E3] rounded-full overflow-hidden">
                                            {/* Segment markers */}
                                            <div className="absolute inset-0 flex">
                                                <div className="w-1/4 border-r border-white/30" />
                                                <div className="w-1/4 border-r border-white/30" />
                                                <div className="w-1/4 border-r border-white/30" />
                                                <div className="w-1/4" />
                                            </div>
                                            {/* Fill bar */}
                                            <div
                                                className="h-full rounded-full transition-all duration-700 relative z-10"
                                                style={{
                                                    width: `${proofStrength.score}%`,
                                                    backgroundColor: proofStrength.color
                                                }}
                                            />
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* ERRC Accordion */}
                    <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl overflow-hidden">
                        <button
                            onClick={() => setShowErrc(!showErrc)}
                            className="w-full flex items-center justify-between p-5 hover:bg-white transition-colors"
                        >
                            <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                Strategic Actions
                            </span>
                            {showErrc ? <ChevronUp className="w-4 h-4 text-[#9D9F9F]" /> : <ChevronDown className="w-4 h-4 text-[#9D9F9F]" />}
                        </button>

                        {showErrc && (
                            <div className="grid grid-cols-2 gap-3 p-5 pt-0">
                                <div className="p-4 bg-white rounded-xl">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Minus className="w-3 h-3 text-[#5B5F61]" />
                                        <span className="text-xs font-mono uppercase text-[#9D9F9F]">Eliminate</span>
                                    </div>
                                    <ul className="text-sm text-[#2D3538] space-y-1">
                                        {(phase3.errc?.eliminate || [{ factor: 'Factor' }]).slice(0, 2).map((item, i) => (
                                            <li key={i}>{typeof item === 'string' ? item : item.factor}</li>
                                        ))}
                                    </ul>
                                </div>
                                <div className="p-4 bg-white rounded-xl">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Plus className="w-3 h-3 text-[#5B5F61]" />
                                        <span className="text-xs font-mono uppercase text-[#9D9F9F]">Create</span>
                                    </div>
                                    <ul className="text-sm text-[#2D3538] space-y-1">
                                        {(phase3.errc?.create || [{ factor: 'Factor' }]).slice(0, 2).map((item, i) => (
                                            <li key={i}>{typeof item === 'string' ? item : item.factor}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Screen 2: Claims with Battle Mode */}
            {currentScreen === 'claims' && (
                <div className="space-y-8">
                    {phase3.claims && phase3.claims.length > 0 ? (
                        <>
                            {/* Claim Battle: You vs. Competitor */}
                            <div className="relative">
                                <div className="grid grid-cols-2 gap-4">
                                    {/* Competitor Claim (Generic) */}
                                    <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl p-6 opacity-60">
                                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-3">
                                            Generic Competitor
                                        </span>
                                        <p className="text-[#5B5F61] text-sm italic">
                                            "{competitorClaim}"
                                        </p>
                                    </div>

                                    {/* Your Claim */}
                                    <div className="bg-[#2D3538] rounded-2xl p-6 relative group">
                                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-white/50 block mb-3">
                                            Your Claim
                                        </span>
                                        <p className="text-white font-medium">
                                            "{primaryClaim}"
                                        </p>
                                        {/* Copy Button */}
                                        <button
                                            onClick={() => copyToClipboard(primaryClaim, 'Claim')}
                                            className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-white/10 rounded-lg"
                                        >
                                            <Copy className="w-4 h-4 text-white/60" />
                                        </button>
                                    </div>
                                </div>

                                {/* VS Badge */}
                                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
                                    <div className="w-10 h-10 bg-white border-2 border-[#2D3538] rounded-full flex items-center justify-center shadow-lg">
                                        <Zap className="w-4 h-4 text-[#2D3538]" />
                                    </div>
                                </div>
                            </div>

                            {/* Why Yours Wins */}
                            <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-xl p-5">
                                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-3">
                                    Why Yours Wins
                                </span>
                                <ul className="space-y-2">
                                    <li className="flex items-center gap-2 text-sm text-[#2D3538]">
                                        <Check className="w-4 h-4 text-[#2D3538]" />
                                        Specific to your differentiation
                                    </li>
                                    <li className="flex items-center gap-2 text-sm text-[#2D3538]">
                                        <Check className="w-4 h-4 text-[#2D3538]" />
                                        Backed by proof (not generic claims)
                                    </li>
                                    <li className="flex items-center gap-2 text-sm text-[#2D3538]">
                                        <Check className="w-4 h-4 text-[#2D3538]" />
                                        Clear outcome for the customer
                                    </li>
                                </ul>
                            </div>

                            {/* Primary Claim Card with Star */}
                            <div className="bg-[#2D3538] rounded-3xl p-10 relative group">
                                <div className="flex items-center gap-2 mb-4">
                                    <Star className="w-4 h-4 text-white/50" />
                                    <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-white/50">
                                        Primary Claim
                                    </span>
                                </div>
                                <p className="font-serif text-[26px] text-white leading-[1.4]">
                                    "{primaryClaim}"
                                </p>
                                {/* Copy Button */}
                                <button
                                    onClick={() => copyToClipboard(primaryClaim, 'Primary claim')}
                                    className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-white/10 rounded-lg"
                                >
                                    <Copy className="w-5 h-5 text-white/60" />
                                </button>
                            </div>

                            {/* Alt Claims */}
                            {phase3.claims.length > 1 && (
                                <div className="grid grid-cols-2 gap-4">
                                    {phase3.claims.filter(c => c.id !== phase3.primaryClaimId).slice(0, 2).map((claim) => (
                                        <div key={claim.id} className="bg-white border border-[#E5E6E3] rounded-2xl p-6 relative group">
                                            <p className="text-[#2D3538] text-sm">"{claim.promise}"</p>
                                            <button
                                                onClick={() => copyToClipboard(claim.promise, 'Claim')}
                                                className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-[#F3F4EE] rounded-lg"
                                            >
                                                <Copy className="w-3 h-3 text-[#9D9F9F]" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="bg-white border border-[#E5E6E3] rounded-3xl p-10 text-center">
                            <p className="text-[#5B5F61]">Claims will be generated from your differentiation.</p>
                        </div>
                    )}
                </div>
            )}

            {/* Screen 3: Complete */}
            {currentScreen === 'complete' && (
                <div className="text-center space-y-10 py-8">
                    <div className="w-20 h-20 mx-auto bg-[#2D3538] rounded-full flex items-center justify-center">
                        <Check className="w-10 h-10 text-white" />
                    </div>

                    <div className="max-w-sm mx-auto">
                        <p className="text-lg text-[#5B5F61]">
                            Your differentiation blueprint is ready.
                        </p>
                    </div>

                    <Button
                        onClick={handleLock}
                        className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-12 py-7 rounded-2xl text-lg font-medium transition-all hover:scale-[1.02]"
                    >
                        Continue to Phase 4 <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                </div>
            )}
        </PhaseScreen>
    );
}
