'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Phase6Data, emptyPhase6, loadFoundationDB, saveFoundation, FoundationData } from '@/lib/foundation';
import { forgePhase6, regenerateSoundbite } from '@/lib/phase6-forge';
import { PhaseScreen, PhaseStep } from '@/components/phase-shared';
import { Button } from '@/components/ui/button';
import { Check, ArrowRight, MessageSquare, Sparkles, RefreshCw, Copy, AlertCircle, ChevronLeft, ChevronRight } from 'lucide-react';
import { toast } from 'sonner';
import gsap from 'gsap';
import { RegenWithFeedback } from '@/components/ui/RegenWithFeedback';

type Phase6Screen = 'messaging' | 'complete';

// Streamlined: 4 → 2 screens
const STEPS: PhaseStep[] = [
    { id: 'messaging', label: 'Messaging' },
    { id: 'complete', label: 'Launch' },
];

const SCREEN_CONTENT: Record<Phase6Screen, { title: string; subtitle: string }> = {
    messaging: {
        title: 'Your Messaging',
        subtitle: 'Blueprint, soundbites, and channel variants.'
    },
    complete: {
        title: 'Your Marketing System is Ready',
        subtitle: 'From foundation to messaging — complete.'
    },
};

function copyToClipboard(text: string, label: string) {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied!`);
}

export function Phase6Wizard() {
    const router = useRouter();
    const confettiRef = useRef<HTMLDivElement>(null);
    const [foundation, setFoundation] = useState<FoundationData | null>(null);
    const [phase6, setPhase6] = useState<Phase6Data>(emptyPhase6);
    const [currentScreen, setCurrentScreen] = useState<Phase6Screen>('messaging');
    const [activeTab, setActiveTab] = useState<'blueprint' | 'soundbites' | 'variants'>('blueprint');
    const [selectedSoundbiteIndex, setSelectedSoundbiteIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [isProcessing, setIsProcessing] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await loadFoundationDB();
                setFoundation(data);

                if (data.phase6) {
                    setPhase6(data.phase6);
                } else if (data.phase5) {
                    setIsProcessing(true);
                    const forged = await forgePhase6(data.phase5);
                    setPhase6(forged);
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

    // Celebration animation
    useEffect(() => {
        if (currentScreen === 'complete' && confettiRef.current) {
            gsap.fromTo(
                confettiRef.current.children,
                { scale: 0, opacity: 0, y: 50 },
                { scale: 1, opacity: 1, y: 0, duration: 0.8, stagger: 0.1, ease: 'elastic.out(1, 0.5)' }
            );
        }
    }, [currentScreen]);

    const savePhase6 = useCallback(async (data: Phase6Data) => {
        if (!foundation) return;
        try {
            await saveFoundation({ ...foundation, phase6: data });
        } catch (error) {
            console.error('Error saving phase6:', error);
        }
    }, [foundation]);

    const currentIndex = STEPS.findIndex(s => s.id === currentScreen);
    const currentSoundbite = phase6.soundbites?.[selectedSoundbiteIndex];

    const goNext = () => {
        if (currentIndex < STEPS.length - 1) {
            setCurrentScreen(STEPS[currentIndex + 1].id as Phase6Screen);
            savePhase6(phase6);
        }
    };

    const goBack = () => {
        if (currentIndex > 0) {
            setCurrentScreen(STEPS[currentIndex - 1].id as Phase6Screen);
        } else {
            router.push('/foundation/phase5');
        }
    };

    const handleStepClick = (stepId: string) => {
        const stepIndex = STEPS.findIndex(s => s.id === stepId);
        if (stepIndex <= currentIndex) {
            setCurrentScreen(stepId as Phase6Screen);
        }
    };

    const handleRegenerate = (soundbiteId: string, feedback?: string) => {
        if (!foundation?.phase5) return;
        const soundbite = phase6.soundbites?.find(s => s.id === soundbiteId);
        if (!soundbite) return;
        const regenerated = regenerateSoundbite(soundbite, foundation.phase5);
        setPhase6({
            ...phase6,
            soundbites: phase6.soundbites?.map(s => s.id === soundbiteId ? regenerated : s) || []
        });
        toast.success(feedback ? `Regenerated: ${feedback}` : 'Soundbite regenerated');
    };

    const handleLaunch = async () => {
        const lockedData = { ...phase6, lockedAt: new Date().toISOString() };
        setPhase6(lockedData);
        await savePhase6(lockedData);
        toast.success('🎉 Marketing system complete!');
        router.push('/foundation/results');
    };

    // Loading
    if (isLoading || isProcessing) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="text-center space-y-6">
                    <div className="w-16 h-16 border-[3px] border-[#2D3538] border-t-transparent rounded-full animate-spin mx-auto" />
                    <p className="font-serif text-2xl text-[#2D3538]">
                        {isProcessing ? 'Forging messaging...' : 'Loading...'}
                    </p>
                </div>
            </div>
        );
    }

    if (!foundation?.phase5) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="text-center space-y-8 max-w-md px-8">
                    <AlertCircle className="w-12 h-12 text-[#2D3538] mx-auto" />
                    <h1 className="font-serif text-3xl text-[#2D3538]">Complete Phase 5 First</h1>
                    <Button
                        onClick={() => router.push('/foundation/phase5')}
                        className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-2xl"
                    >
                        Go to Phase 5
                    </Button>
                </div>
            </div>
        );
    }

    const { title, subtitle } = SCREEN_CONTENT[currentScreen];

    return (
        <PhaseScreen
            phaseNumber={6}
            phaseTitle="Soundbite Forge"
            currentStepId={currentScreen}
            steps={STEPS}
            title={title}
            subtitle={subtitle}
            onBack={goBack}
            onStepClick={handleStepClick}
            showContinue={currentScreen !== 'complete'}
            continueText="Complete Setup"
            onContinue={goNext}
        >
            {/* Screen 1: All Messaging Content */}
            {currentScreen === 'messaging' && (
                <div className="space-y-6">
                    {/* Tabs */}
                    <div className="flex gap-2 p-1 bg-[#F3F4EE] rounded-xl w-fit">
                        <button
                            onClick={() => setActiveTab('blueprint')}
                            className={`px-4 py-2 text-sm rounded-lg transition-all ${activeTab === 'blueprint' ? 'bg-white text-[#2D3538] shadow-sm' : 'text-[#5B5F61]'}`}
                        >
                            Blueprint
                        </button>
                        <button
                            onClick={() => setActiveTab('soundbites')}
                            className={`px-4 py-2 text-sm rounded-lg transition-all ${activeTab === 'soundbites' ? 'bg-white text-[#2D3538] shadow-sm' : 'text-[#5B5F61]'}`}
                        >
                            Soundbites
                        </button>
                        <button
                            onClick={() => setActiveTab('variants')}
                            className={`px-4 py-2 text-sm rounded-lg transition-all ${activeTab === 'variants' ? 'bg-white text-[#2D3538] shadow-sm' : 'text-[#5B5F61]'}`}
                        >
                            Variants
                        </button>
                    </div>

                    {/* Blueprint Tab */}
                    {activeTab === 'blueprint' && (
                        <div className="space-y-6">
                            <div className="bg-[#2D3538] rounded-3xl p-10 relative group">
                                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-white/40 block mb-3">
                                    Controlling Idea
                                </span>
                                <p className="font-serif text-[26px] text-white leading-[1.4]">
                                    "{phase6.blueprint?.controllingIdea || phase6.blueprint?.coreMessage || 'Your core message'}"
                                </p>
                                <button
                                    onClick={() => copyToClipboard(phase6.blueprint?.controllingIdea || phase6.blueprint?.coreMessage || '', 'Core message')}
                                    className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-white/10 rounded-lg"
                                >
                                    <Copy className="w-5 h-5 text-white/60" />
                                </button>
                            </div>

                            {phase6.blueprint?.pillars && phase6.blueprint.pillars.length > 0 && (
                                <div className="grid grid-cols-3 gap-4">
                                    {phase6.blueprint.pillars.map((pillar, i) => {
                                        const pillarName = typeof pillar === 'string' ? pillar : pillar.name;
                                        return (
                                            <div key={i} className="bg-white border border-[#E5E6E3] rounded-2xl p-5 group relative">
                                                <span className="text-[10px] font-mono text-[#9D9F9F] block mb-2">Pillar #{i + 1}</span>
                                                <p className="font-medium text-[#2D3538]">{pillarName}</p>
                                                <button
                                                    onClick={() => copyToClipboard(pillarName, 'Pillar')}
                                                    className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-[#F3F4EE] rounded"
                                                >
                                                    <Copy className="w-3 h-3 text-[#9D9F9F]" />
                                                </button>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Soundbites Tab */}
                    {activeTab === 'soundbites' && (
                        <div className="space-y-4">
                            {phase6.soundbites && phase6.soundbites.length > 0 ? (
                                <>
                                    {/* Soundbite Selector */}
                                    <div className="flex items-center justify-between">
                                        <div className="flex gap-2">
                                            {phase6.soundbites.slice(0, 5).map((sb, i) => (
                                                <button
                                                    key={sb.id || i}
                                                    onClick={() => setSelectedSoundbiteIndex(i)}
                                                    className={`w-8 h-8 rounded-lg text-sm transition-all ${i === selectedSoundbiteIndex ? 'bg-[#2D3538] text-white' : 'bg-white border border-[#E5E6E3] text-[#5B5F61]'}`}
                                                >
                                                    {i + 1}
                                                </button>
                                            ))}
                                        </div>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => setSelectedSoundbiteIndex(Math.max(0, selectedSoundbiteIndex - 1))}
                                                disabled={selectedSoundbiteIndex === 0}
                                                className="p-2 hover:bg-[#F3F4EE] rounded-lg disabled:opacity-30"
                                            >
                                                <ChevronLeft className="w-4 h-4 text-[#5B5F61]" />
                                            </button>
                                            <button
                                                onClick={() => setSelectedSoundbiteIndex(Math.min((phase6.soundbites?.length || 1) - 1, selectedSoundbiteIndex + 1))}
                                                disabled={selectedSoundbiteIndex >= (phase6.soundbites?.length || 1) - 1}
                                                className="p-2 hover:bg-[#F3F4EE] rounded-lg disabled:opacity-30"
                                            >
                                                <ChevronRight className="w-4 h-4 text-[#5B5F61]" />
                                            </button>
                                        </div>
                                    </div>

                                    {/* Current Soundbite */}
                                    {currentSoundbite && (
                                        <div className="bg-white border border-[#E5E6E3] rounded-3xl p-8 relative group">
                                            <div className="flex items-center gap-2 mb-4">
                                                <MessageSquare className="w-4 h-4 text-[#9D9F9F]" />
                                                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                                    {(currentSoundbite as any).context || 'Soundbite'}
                                                </span>
                                            </div>
                                            <p className="font-serif text-xl text-[#2D3538] mb-6">
                                                "{(currentSoundbite as any).copy || (currentSoundbite as any).text || 'Soundbite'}"
                                            </p>
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() => copyToClipboard((currentSoundbite as any).copy || (currentSoundbite as any).text || '', 'Soundbite')}
                                                    className="flex items-center gap-2 px-4 py-2 bg-[#F3F4EE] hover:bg-[#E5E6E3] rounded-lg text-sm text-[#5B5F61] transition-colors"
                                                >
                                                    <Copy className="w-3.5 h-3.5" /> Copy
                                                </button>
                                                <RegenWithFeedback
                                                    onRegenerate={(feedback) => handleRegenerate(currentSoundbite.id, feedback)}
                                                />
                                            </div>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <div className="bg-white border border-[#E5E6E3] rounded-2xl p-8 text-center">
                                    <p className="text-[#5B5F61]">Soundbites will be generated from your messaging.</p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Variants Tab */}
                    {activeTab === 'variants' && (
                        <div className="space-y-4">
                            {(phase6 as any).channelVariants && (phase6 as any).channelVariants.length > 0 ? (
                                (phase6 as any).channelVariants.map((variant: any, i: number) => (
                                    <div key={variant.channel || i} className="bg-white border border-[#E5E6E3] rounded-2xl p-6 group relative">
                                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-3">
                                            {variant.channel}
                                        </span>
                                        <p className="text-[#2D3538]">
                                            {variant.headline || variant.body || 'Channel variant'}
                                        </p>
                                        <button
                                            onClick={() => copyToClipboard(variant.headline || variant.body || '', 'Variant')}
                                            className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-[#F3F4EE] rounded-lg"
                                        >
                                            <Copy className="w-4 h-4 text-[#9D9F9F]" />
                                        </button>
                                    </div>
                                ))
                            ) : (
                                <div className="bg-white border border-[#E5E6E3] rounded-2xl p-8 text-center">
                                    <p className="text-[#5B5F61]">Channel variants will be generated.</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Screen 2: Complete (celebration) */}
            {currentScreen === 'complete' && (
                <div className="text-center space-y-10 py-8" ref={confettiRef}>
                    <div className="w-24 h-24 mx-auto bg-[#2D3538] rounded-full flex items-center justify-center">
                        <Sparkles className="w-12 h-12 text-white" />
                    </div>

                    <div className="max-w-md mx-auto">
                        <p className="text-lg text-[#5B5F61] mb-6">
                            From foundation to messaging — your complete marketing operating system is ready.
                        </p>
                        <div className="flex justify-center gap-3 flex-wrap">
                            {['Foundation', 'Differentiation', 'Positioning', 'ICPs', 'Messaging'].map((phase) => (
                                <span key={phase} className="px-3 py-1.5 bg-white border border-[#E5E6E3] rounded-lg text-sm text-[#2D3538]">
                                    <Check className="w-3 h-3 inline mr-1.5 text-[#2D3538]" />
                                    {phase}
                                </span>
                            ))}
                        </div>
                    </div>

                    <Button
                        onClick={handleLaunch}
                        className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-14 py-8 rounded-2xl text-xl font-medium transition-all hover:scale-[1.02]"
                    >
                        Launch Dashboard <ArrowRight className="ml-3 h-6 w-6" />
                    </Button>
                </div>
            )}
        </PhaseScreen>
    );
}
