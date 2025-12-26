'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Phase5Data, emptyPhase5, loadFoundationDB, saveFoundation, FoundationData } from '@/lib/foundation';
import { compilePhase5 } from '@/lib/phase5-compiler';
import { PhaseScreen, PhaseStep } from '@/components/phase-shared';
import { Button } from '@/components/ui/button';
import { Check, ArrowRight, Users, User, AlertCircle, Target, MessageCircle, ChevronDown, ChevronUp, Copy } from 'lucide-react';
import { toast } from 'sonner';

type Phase5Screen = 'icps' | 'complete';

// Streamlined: 5 → 2 screens
const STEPS: PhaseStep[] = [
    { id: 'icps', label: 'ICPs' },
    { id: 'complete', label: 'Complete' },
];

const SCREEN_CONTENT: Record<Phase5Screen, { title: string; subtitle: string }> = {
    icps: {
        title: 'Your ICPs',
        subtitle: 'Ideal customer profiles with triggers, objections, and personas.'
    },
    complete: {
        title: 'ICPs Complete',
        subtitle: 'Ready to power your messaging.'
    },
};

function copyToClipboard(text: string, label: string) {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied!`);
}

export function Phase5Wizard() {
    const router = useRouter();
    const [foundation, setFoundation] = useState<FoundationData | null>(null);
    const [phase5, setPhase5] = useState<Phase5Data>(emptyPhase5);
    const [currentScreen, setCurrentScreen] = useState<Phase5Screen>('icps');
    const [selectedICPIndex, setSelectedICPIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [isProcessing, setIsProcessing] = useState(false);
    const [showPersonas, setShowPersonas] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await loadFoundationDB();
                setFoundation(data);

                if (data.phase5) {
                    setPhase5(data.phase5);
                } else if (data.phase4) {
                    setIsProcessing(true);
                    const compiled = await compilePhase5(data.phase4);
                    setPhase5(compiled);
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

    const savePhase5 = useCallback(async (data: Phase5Data) => {
        if (!foundation) return;
        try {
            await saveFoundation({ ...foundation, phase5: data });
        } catch (error) {
            console.error('Error saving phase5:', error);
        }
    }, [foundation]);

    const currentIndex = STEPS.findIndex(s => s.id === currentScreen);
    const currentICP = phase5.icps?.[selectedICPIndex];

    const goNext = () => {
        if (currentIndex < STEPS.length - 1) {
            setCurrentScreen(STEPS[currentIndex + 1].id as Phase5Screen);
            savePhase5(phase5);
        }
    };

    const goBack = () => {
        if (currentIndex > 0) {
            setCurrentScreen(STEPS[currentIndex - 1].id as Phase5Screen);
        } else {
            router.push('/foundation/phase4');
        }
    };

    const handleStepClick = (stepId: string) => {
        const stepIndex = STEPS.findIndex(s => s.id === stepId);
        if (stepIndex <= currentIndex) {
            setCurrentScreen(stepId as Phase5Screen);
        }
    };

    const handleLock = async () => {
        const lockedData = { ...phase5, lockedAt: new Date().toISOString() };
        setPhase5(lockedData);
        await savePhase5(lockedData);
        toast.success('ICPs locked!');
        router.push('/foundation/phase6');
    };

    // Loading
    if (isLoading || isProcessing) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="text-center space-y-6">
                    <div className="w-16 h-16 border-[3px] border-[#2D3538] border-t-transparent rounded-full animate-spin mx-auto" />
                    <p className="font-serif text-2xl text-[#2D3538]">
                        {isProcessing ? 'Compiling ICPs...' : 'Loading...'}
                    </p>
                </div>
            </div>
        );
    }

    if (!foundation?.phase4) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="text-center space-y-8 max-w-md px-8">
                    <AlertCircle className="w-12 h-12 text-[#2D3538] mx-auto" />
                    <h1 className="font-serif text-3xl text-[#2D3538]">Complete Phase 4 First</h1>
                    <Button
                        onClick={() => router.push('/foundation/phase4')}
                        className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-2xl"
                    >
                        Go to Phase 4
                    </Button>
                </div>
            </div>
        );
    }

    const { title, subtitle } = SCREEN_CONTENT[currentScreen];

    return (
        <PhaseScreen
            phaseNumber={5}
            phaseTitle="ICP Engine"
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
            {/* Screen 1: All ICP Content */}
            {currentScreen === 'icps' && (
                <div className="space-y-6">
                    {/* Candidates Info Bar (merged from Candidates screen) */}
                    {phase5.candidateSegments && phase5.candidateSegments.length > 0 && (
                        <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-xl p-4 flex items-center gap-3">
                            <div className="w-2 h-2 rounded-full bg-[#2D3538]" />
                            <p className="text-sm text-[#5B5F61]">
                                {phase5.candidateSegments.filter(c => c.kept).length} of {phase5.candidateSegments.length} candidates selected as ICPs
                            </p>
                        </div>
                    )}

                    {/* ICP Tabs */}
                    {phase5.icps && phase5.icps.length > 1 && (
                        <div className="flex gap-2">
                            {phase5.icps.map((icp, i) => (
                                <button
                                    key={icp.id || i}
                                    onClick={() => setSelectedICPIndex(i)}
                                    className={`px-5 py-2.5 rounded-xl text-sm transition-all ${i === selectedICPIndex
                                        ? 'bg-[#2D3538] text-white'
                                        : 'bg-white border border-[#E5E6E3] text-[#5B5F61] hover:border-[#2D3538]'
                                        }`}
                                >
                                    {icp.name}
                                    {i === 0 && <span className="ml-2 text-[9px] opacity-60">Primary</span>}
                                </button>
                            ))}
                        </div>
                    )}

                    {currentICP && (
                        <>
                            {/* Main ICP Card */}
                            <div className="bg-[#2D3538] rounded-3xl p-10 relative group">
                                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-white/40 block mb-2">
                                    {selectedICPIndex === 0 ? 'Primary ICP' : 'Secondary ICP'}
                                </span>
                                <h3 className="font-serif text-[28px] text-white mb-3">{currentICP.name}</h3>
                                <p className="text-white/70 leading-relaxed">
                                    {currentICP.jtbd?.functional || 'Functional job description'}
                                </p>
                                <button
                                    onClick={() => copyToClipboard(currentICP.name, 'ICP name')}
                                    className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-white/10 rounded-lg"
                                >
                                    <Copy className="w-5 h-5 text-white/60" />
                                </button>
                            </div>

                            {/* Triggers + Objections */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6 group relative">
                                    <div className="flex items-center gap-2 mb-4">
                                        <Target className="w-4 h-4 text-[#9D9F9F]" />
                                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                            Triggers
                                        </span>
                                    </div>
                                    <ul className="space-y-2">
                                        {(currentICP.triggers || ['Trigger event']).slice(0, 3).map((trigger, i) => (
                                            <li key={i} className="flex items-start gap-2 text-sm text-[#2D3538]">
                                                <div className="w-1 h-1 rounded-full bg-[#2D3538] mt-2 flex-shrink-0" />
                                                <span>{trigger}</span>
                                            </li>
                                        ))}
                                    </ul>
                                    <button
                                        onClick={() => copyToClipboard((currentICP.triggers || []).join('\n'), 'Triggers')}
                                        className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-[#F3F4EE] rounded-lg"
                                    >
                                        <Copy className="w-3.5 h-3.5 text-[#9D9F9F]" />
                                    </button>
                                </div>

                                <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6 group relative">
                                    <div className="flex items-center gap-2 mb-4">
                                        <MessageCircle className="w-4 h-4 text-[#9D9F9F]" />
                                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                            Objections
                                        </span>
                                    </div>
                                    <ul className="space-y-2">
                                        {(currentICP.objections || ['Objection']).slice(0, 3).map((obj, i) => (
                                            <li key={i} className="flex items-start gap-2 text-sm text-[#2D3538]">
                                                <div className="w-1 h-1 rounded-full bg-[#2D3538] mt-2 flex-shrink-0" />
                                                <span>{obj}</span>
                                            </li>
                                        ))}
                                    </ul>
                                    <button
                                        onClick={() => copyToClipboard((currentICP.objections || []).join('\n'), 'Objections')}
                                        className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-[#F3F4EE] rounded-lg"
                                    >
                                        <Copy className="w-3.5 h-3.5 text-[#9D9F9F]" />
                                    </button>
                                </div>
                            </div>

                            {/* Personas Accordion (merged from Personas screen) */}
                            <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl overflow-hidden">
                                <button
                                    onClick={() => setShowPersonas(!showPersonas)}
                                    className="w-full flex items-center justify-between p-5 hover:bg-white transition-colors"
                                >
                                    <div className="flex items-center gap-3">
                                        <User className="w-4 h-4 text-[#9D9F9F]" />
                                        <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                            Buying Personas ({(currentICP.personas || []).length})
                                        </span>
                                    </div>
                                    {showPersonas ? <ChevronUp className="w-4 h-4 text-[#9D9F9F]" /> : <ChevronDown className="w-4 h-4 text-[#9D9F9F]" />}
                                </button>

                                {showPersonas && (
                                    <div className="p-5 pt-0 space-y-3">
                                        {(currentICP.personas || [{ id: '1', role: 'Decision Maker', goals: [], kpis: [] }]).map((persona, i) => (
                                            <div key={persona.id || i} className="bg-white rounded-xl p-5 flex items-start gap-4">
                                                <div className="w-10 h-10 bg-[#2D3538] rounded-full flex items-center justify-center flex-shrink-0">
                                                    <User className="w-5 h-5 text-white" />
                                                </div>
                                                <div>
                                                    <h4 className="font-medium text-[#2D3538] mb-1">{persona.role}</h4>
                                                    {persona.goals && persona.goals.length > 0 && (
                                                        <p className="text-sm text-[#5B5F61]">
                                                            {typeof persona.goals[0] === 'string' ? persona.goals[0] : persona.goals[0].text}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            )}

            {/* Screen 2: Complete (simplified) */}
            {currentScreen === 'complete' && (
                <div className="text-center space-y-10 py-8">
                    <div className="w-20 h-20 mx-auto bg-[#2D3538] rounded-full flex items-center justify-center">
                        <Users className="w-10 h-10 text-white" />
                    </div>

                    <div className="max-w-sm mx-auto">
                        <p className="text-lg text-[#5B5F61]">
                            Your ideal customer profiles are ready.
                        </p>
                    </div>

                    <Button
                        onClick={handleLock}
                        className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-12 py-7 rounded-2xl text-lg font-medium transition-all hover:scale-[1.02]"
                    >
                        Continue to Phase 6 <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                </div>
            )}
        </PhaseScreen>
    );
}
