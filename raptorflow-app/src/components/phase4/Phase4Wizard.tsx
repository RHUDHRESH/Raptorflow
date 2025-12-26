'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Phase4Data, emptyPhase4, loadFoundationDB, saveFoundation, FoundationData } from '@/lib/foundation';
import { compilePhase4 } from '@/lib/phase4-compiler';
import { PhaseScreen, PhaseStep } from '@/components/phase-shared';
import { Button } from '@/components/ui/button';
import { Check, ArrowRight, Target, AlertCircle, Copy, Shield } from 'lucide-react';
import { toast } from 'sonner';
import { ProofVault } from '@/components/shared/ProofVault';
import { useProofVault } from '@/hooks/useProofVault';

type Phase4Screen = 'segments' | 'positioning' | 'complete';

// Streamlined: 6 → 3 screens
const STEPS: PhaseStep[] = [
    { id: 'segments', label: 'Segments' },
    { id: 'positioning', label: 'Positioning' },
    { id: 'complete', label: 'Complete' },
];

const SCREEN_CONTENT: Record<Phase4Screen, { title: string; subtitle: string }> = {
    segments: {
        title: 'Target Segments',
        subtitle: 'Ranked by fit, urgency, and reachability.'
    },
    positioning: {
        title: 'Your Positioning',
        subtitle: 'Statement, pitch, and guardrails.'
    },
    complete: {
        title: 'Position Locked',
        subtitle: 'Ready to power your ICPs.'
    },
};

function copyToClipboard(text: string, label: string) {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied!`, { description: 'Paste it in your pitch deck.' });
}

export function Phase4Wizard() {
    const router = useRouter();
    const [foundation, setFoundation] = useState<FoundationData | null>(null);
    const [phase4, setPhase4] = useState<Phase4Data>(emptyPhase4);
    const [currentScreen, setCurrentScreen] = useState<Phase4Screen>('segments');
    const [isLoading, setIsLoading] = useState(true);
    const [isProcessing, setIsProcessing] = useState(false);
    const [activeTab, setActiveTab] = useState<'statement' | 'pitch'>('statement');
    const [showProofVault, setShowProofVault] = useState(false);
    
    const proofVault = useProofVault(foundation?.proofVault || []);

    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await loadFoundationDB();
                setFoundation(data);

                if (data.phase4) {
                    setPhase4(data.phase4);
                } else if (data.phase3) {
                    setIsProcessing(true);
                    const compiled = await compilePhase4(data.phase3);
                    setPhase4(compiled);
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

    const savePhase4 = useCallback(async (data: Phase4Data) => {
        if (!foundation) return;
        try {
            await saveFoundation({ ...foundation, phase4: data });
        } catch (error) {
            console.error('Error saving phase4:', error);
        }
    }, [foundation]);

    const currentIndex = STEPS.findIndex(s => s.id === currentScreen);

    const goNext = () => {
        if (currentIndex < STEPS.length - 1) {
            setCurrentScreen(STEPS[currentIndex + 1].id as Phase4Screen);
            savePhase4(phase4);
        }
    };

    const goBack = () => {
        if (currentIndex > 0) {
            setCurrentScreen(STEPS[currentIndex - 1].id as Phase4Screen);
        } else {
            router.push('/foundation/phase3');
        }
    };

    const handleStepClick = (stepId: string) => {
        const stepIndex = STEPS.findIndex(s => s.id === stepId);
        if (stepIndex <= currentIndex) {
            setCurrentScreen(stepId as Phase4Screen);
        }
    };

    const handleLock = async () => {
        const lockedData = { ...phase4, lockedAt: new Date().toISOString() };
        setPhase4(lockedData);
        await savePhase4(lockedData);
        toast.success('Positioning locked!');
        router.push('/foundation/phase5');
    };

    // Loading
    if (isLoading || isProcessing) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="text-center space-y-6">
                    <div className="w-16 h-16 border-[3px] border-[#2D3538] border-t-transparent rounded-full animate-spin mx-auto" />
                    <p className="font-serif text-2xl text-[#2D3538]">
                        {isProcessing ? 'Compiling positioning...' : 'Loading...'}
                    </p>
                </div>
            </div>
        );
    }

    if (!foundation?.phase3) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="text-center space-y-8 max-w-md px-8">
                    <AlertCircle className="w-12 h-12 text-[#2D3538] mx-auto" />
                    <h1 className="font-serif text-3xl text-[#2D3538]">Complete Phase 3 First</h1>
                    <Button
                        onClick={() => router.push('/foundation/phase3')}
                        className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-2xl"
                    >
                        Go to Phase 3
                    </Button>
                </div>
            </div>
        );
    }

    const { title, subtitle } = SCREEN_CONTENT[currentScreen];

    const getCategoryLabel = (cat: unknown): string => {
        if (typeof cat === 'string') return cat;
        if (cat && typeof cat === 'object' && 'primary' in cat) return (cat as { primary: string }).primary;
        return 'Select category';
    };

    const positioningStatement = phase4.positioningStatement || 'For [target], we are the [category] that [differentiator] because [proof].';
    const elevatorPitch = typeof phase4.elevatorPitch === 'string'
        ? phase4.elevatorPitch
        : phase4.elevatorPitch?.thirtySec || 'Your 30-second pitch will appear here...';

    return (
        <PhaseScreen
            phaseNumber={4}
            phaseTitle="Positioning Lab"
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
            {/* Screen 1: Segments */}
            {currentScreen === 'segments' && (
                <div className="space-y-4">
                    {(phase4.targetSegments || []).map((segment, i) => (
                        <div
                            key={segment.id || i}
                            className={`bg-white border rounded-2xl p-6 transition-all group ${segment.isPrimary ? 'border-[#2D3538] border-2' : 'border-[#E5E6E3]'
                                }`}
                        >
                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 bg-[#F3F4EE] rounded-full flex items-center justify-center flex-shrink-0">
                                    <span className="font-serif text-lg text-[#2D3538]">{i + 1}</span>
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-1">
                                        <h3 className="font-serif text-lg text-[#2D3538]">{segment.name}</h3>
                                        {segment.isPrimary && (
                                            <span className="text-[9px] font-mono uppercase tracking-wider bg-[#2D3538] text-white px-2 py-0.5 rounded">
                                                Primary
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-[#5B5F61]">
                                        {segment.whyBestFit?.[0] || segment.jtbd || 'Target segment'}
                                    </p>
                                </div>
                                <button
                                    onClick={() => copyToClipboard(segment.name, 'Segment')}
                                    className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-[#F3F4EE] rounded-lg"
                                >
                                    <Copy className="w-4 h-4 text-[#9D9F9F]" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Screen 2: Positioning (merged Category + Statement + Pitch) */}
            {currentScreen === 'positioning' && (
                <div className="space-y-6">
                    {/* Category Selector (merged from separate screen) */}
                    <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-xl p-4">
                        <div className="flex items-center justify-between">
                            <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                Market Category
                            </span>
                            <select
                                value={getCategoryLabel(phase4.marketCategory)}
                                onChange={(e) => setPhase4({ ...phase4, marketCategory: e.target.value as any })}
                                className="text-sm text-[#2D3538] bg-transparent border-none font-medium cursor-pointer focus:outline-none"
                            >
                                {(phase4.categoryOptions || [getCategoryLabel(phase4.marketCategory)]).map((opt, i) => (
                                    <option key={i} value={getCategoryLabel(opt)}>{getCategoryLabel(opt)}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Statement / Pitch Toggle */}
                    <div className="flex gap-2 p-1 bg-[#F3F4EE] rounded-xl w-fit">
                        <button
                            onClick={() => setActiveTab('statement')}
                            className={`px-4 py-2 text-sm rounded-lg transition-all ${activeTab === 'statement' ? 'bg-white text-[#2D3538] shadow-sm' : 'text-[#5B5F61]'
                                }`}
                        >
                            Statement
                        </button>
                        <button
                            onClick={() => setActiveTab('pitch')}
                            className={`px-4 py-2 text-sm rounded-lg transition-all ${activeTab === 'pitch' ? 'bg-white text-[#2D3538] shadow-sm' : 'text-[#5B5F61]'
                                }`}
                        >
                            Pitch
                        </button>
                    </div>

                    {/* Statement View */}
                    {activeTab === 'statement' && (
                        <>
                            <div className="bg-[#2D3538] rounded-3xl p-10 relative group">
                                <p className="font-serif text-[26px] text-white leading-[1.4]">
                                    "{positioningStatement}"
                                </p>
                                <button
                                    onClick={() => copyToClipboard(positioningStatement, 'Statement')}
                                    className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-white/10 rounded-lg"
                                >
                                    <Copy className="w-5 h-5 text-white/60" />
                                </button>
                            </div>

                            {/* We Are / We Are Not */}
                            {phase4.weAreWeAreNot && (
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-4">
                                            We Are
                                        </span>
                                        <ul className="space-y-2">
                                            {(phase4.weAreWeAreNot.weAre || []).slice(0, 3).map((item, i) => (
                                                <li key={i} className="flex items-start gap-2 text-sm text-[#2D3538]">
                                                    <Check className="w-4 h-4 text-[#2D3538] flex-shrink-0 mt-0.5" />
                                                    <span>{item}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                    <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-4">
                                            We Are Not
                                        </span>
                                        <ul className="space-y-2">
                                            {(phase4.weAreWeAreNot.weAreNot || []).slice(0, 3).map((item, i) => (
                                                <li key={i} className="flex items-start gap-2 text-sm text-[#5B5F61]">
                                                    <div className="w-4 h-4 flex items-center justify-center flex-shrink-0 mt-0.5">
                                                        <div className="w-1 h-1 bg-[#9D9F9F] rounded-full" />
                                                    </div>
                                                    <span>{item}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            )}
                        </>
                    )}

                    {/* Pitch View */}
                    {activeTab === 'pitch' && (
                        <div className="bg-white border border-[#E5E6E3] rounded-3xl p-10 relative group">
                            <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-4">
                                30-Second Pitch
                            </span>
                            <p className="font-serif text-[22px] text-[#2D3538] leading-[1.5]">
                                "{elevatorPitch}"
                            </p>
                            <button
                                onClick={() => copyToClipboard(elevatorPitch, 'Pitch')}
                                className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-[#F3F4EE] rounded-lg"
                            >
                                <Copy className="w-5 h-5 text-[#9D9F9F]" />
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Screen 3: Complete (simplified) */}
            {currentScreen === 'complete' && (
                <div className="text-center space-y-10 py-8">
                    <div className="w-20 h-20 mx-auto bg-[#2D3538] rounded-full flex items-center justify-center">
                        <Target className="w-10 h-10 text-white" />
                    </div>

                    <div className="max-w-sm mx-auto">
                        <p className="text-lg text-[#5B5F61]">
                            Your market positioning is ready.
                        </p>
                    </div>

                    <Button
                        onClick={handleLock}
                        className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-12 py-7 rounded-2xl text-lg font-medium transition-all hover:scale-[1.02]"
                    >
                        Continue to Phase 5 <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                </div>
            )}
            
            {/* Proof Vault Sidebar */}
            <div className="fixed right-0 top-0 h-full w-96 bg-white border-l border-gray-200 transform transition-transform duration-300 z-50 overflow-y-auto">
                <div className="p-4 border-b border-gray-200">
                    <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold">Evidence Vault</h3>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowProofVault(!showProofVault)}
                        >
                            <Shield className="w-4 h-4" />
                        </Button>
                    </div>
                </div>
                
                {showProofVault && (
                    <div className="p-4">
                        <ProofVault
                            items={proofVault.items}
                            onAddItem={proofVault.addItem}
                            onUpdateItem={proofVault.updateItem}
                            onDeleteItem={proofVault.deleteItem}
                            currentPhase={4}
                        />
                    </div>
                )}
            </div>
        </PhaseScreen>
    );
}
