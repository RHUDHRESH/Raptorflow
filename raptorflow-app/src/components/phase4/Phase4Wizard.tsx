'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
    Phase4Data,
    emptyPhase4,
    loadFoundationDB,
    saveFoundation,
    FoundationData
} from '@/lib/foundation';
import { compilePhase4 } from '@/lib/phase4-compiler';
import { PhaseScreen, PhaseStep } from '@/components/phase-shared';
import { Button } from '@/components/ui/button';
import { AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

// Import all screen components
import { PositioningStudioHome } from './PositioningStudioHome';
import { MarketFrameScreen } from './MarketFrameScreen';
import { CompetitionScreen } from './CompetitionScreen';
import { UniqueAttributesScreen } from './UniqueAttributesScreen';
import { ValueTranslationScreen } from './ValueTranslationScreen';
import { WhoCareScreen } from './WhoCareScreen';
import { PositioningStatementBuilder } from './PositioningStatementBuilder';
import { PerceptualMapScreen } from './PerceptualMapScreen';
import { ProofIntegrityScreen } from './ProofIntegrityScreen';
import { LockExportScreen } from './LockExportScreen4';

// All Phase 4 screens following Dunford flow
type Phase4Screen =
    | 'home'         // 4.0 - Executive Cockpit
    | 'market-frame' // 4.1 - Category & Context
    | 'alternatives' // 4.2 - Competition
    | 'attributes'   // 4.3 - Unique Attributes
    | 'value'        // 4.4 - Value Translation
    | 'who-cares'    // 4.5 - Segment Filter
    | 'statement'    // 4.6 - Positioning Statement
    | 'perceptual-map' // 4.7 - 2x2 Map
    | 'proof'        // 4.11 - Proof Integrity
    | 'lock';        // 4.12 - Lock & Export

const STEPS: PhaseStep[] = [
    { id: 'market-frame', label: 'Market Frame' },
    { id: 'alternatives', label: 'Alternatives' },
    { id: 'attributes', label: 'Differentiation' },
    { id: 'value', label: 'Value' },
    { id: 'who-cares', label: 'Who Cares' },
    { id: 'statement', label: 'Statement' },
    { id: 'perceptual-map', label: 'Maps' },
    { id: 'proof', label: 'Proof' },
    { id: 'lock', label: 'Lock' },
];

const SCREEN_CONTENT: Record<Phase4Screen, { title: string; subtitle: string }> = {
    home: {
        title: 'Positioning Studio',
        subtitle: 'Your marketing source of truth.'
    },
    'market-frame': {
        title: 'Market Frame',
        subtitle: 'What category are you in? What are you NOT?'
    },
    alternatives: {
        title: 'Alternatives & Competition',
        subtitle: 'Status quo, indirect, and direct competitors.'
    },
    attributes: {
        title: 'Unique Attributes',
        subtitle: 'What you have that others don\'t.'
    },
    value: {
        title: 'Value Translation',
        subtitle: 'Turn attributes into customer value.'
    },
    'who-cares': {
        title: 'Who Cares?',
        subtitle: 'Identify segments that care most.'
    },
    statement: {
        title: 'Positioning Statement',
        subtitle: 'Lock your canonical positioning.'
    },
    'perceptual-map': {
        title: 'Perceptual Map',
        subtitle: 'Visualize your position vs competitors.'
    },
    proof: {
        title: 'Proof Integrity',
        subtitle: 'Verify claims have evidence.'
    },
    lock: {
        title: 'Lock & Export',
        subtitle: 'Finalize your positioning pack.'
    },
};

export function Phase4Wizard() {
    const router = useRouter();
    const [foundation, setFoundation] = useState<FoundationData | null>(null);
    const [phase4, setPhase4] = useState<Phase4Data>(emptyPhase4);
    const [currentScreen, setCurrentScreen] = useState<Phase4Screen>('home');
    const [isLoading, setIsLoading] = useState(true);
    const [isProcessing, setIsProcessing] = useState(false);
    const [evidenceDrawerOpen, setEvidenceDrawerOpen] = useState(false);
    const [activeEvidenceId, setActiveEvidenceId] = useState<string | null>(null);

    // Load data on mount
    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await loadFoundationDB();
                setFoundation(data);

                if (data.phase4 && data.phase4.marketCategory?.primary) {
                    // Use existing Phase 4 data
                    setPhase4(data.phase4);
                } else if (data.phase3) {
                    // Derive from Phase 3
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

    // Auto-save phase4 data
    const savePhase4 = useCallback(async (data: Phase4Data) => {
        if (!foundation) return;
        try {
            await saveFoundation({ ...foundation, phase4: data });
        } catch (error) {
            console.error('Error saving phase4:', error);
        }
    }, [foundation]);

    // Handle phase4 updates
    const handleUpdate = useCallback((updates: Partial<Phase4Data>) => {
        const updated = { ...phase4, ...updates };
        setPhase4(updated);
        savePhase4(updated);
    }, [phase4, savePhase4]);

    // Navigation helpers
    const screenOrder: Phase4Screen[] = [
        'home', 'market-frame', 'alternatives', 'attributes', 'value',
        'who-cares', 'statement', 'perceptual-map', 'proof', 'lock'
    ];

    const currentIndex = screenOrder.indexOf(currentScreen);

    const goNext = () => {
        if (currentIndex < screenOrder.length - 1) {
            setCurrentScreen(screenOrder[currentIndex + 1]);
            savePhase4(phase4);
        }
    };

    const goBack = () => {
        if (currentIndex > 0) {
            setCurrentScreen(screenOrder[currentIndex - 1]);
        } else {
            router.push('/foundation/phase3');
        }
    };

    const handleNavigate = (screenId: string) => {
        if (screenOrder.includes(screenId as Phase4Screen)) {
            setCurrentScreen(screenId as Phase4Screen);
        }
    };

    const handleStepClick = (stepId: string) => {
        const stepIndex = screenOrder.indexOf(stepId as Phase4Screen);
        if (stepIndex >= 0 && stepIndex <= currentIndex) {
            setCurrentScreen(stepId as Phase4Screen);
        }
    };

    const handleShowEvidence = (claimId: string) => {
        setActiveEvidenceId(claimId);
        setEvidenceDrawerOpen(true);
    };

    const handleLock = async () => {
        const lockedData = { ...phase4, lockedAt: new Date().toISOString() };
        setPhase4(lockedData);
        await savePhase4(lockedData);
        toast.success('Positioning locked!');
        router.push('/foundation/phase5');
    };

    // Loading states
    if (isLoading || isProcessing) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="text-center space-y-6">
                    <div className="w-16 h-16 border-[3px] border-[#2D3538] border-t-transparent rounded-full animate-spin mx-auto" />
                    <p className="font-serif text-2xl text-[#2D3538]">
                        {isProcessing ? 'Compiling positioning from Phase 3...' : 'Loading...'}
                    </p>
                </div>
            </div>
        );
    }

    // Check if Phase 3 is complete
    if (!foundation?.phase3) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="text-center space-y-8 max-w-md px-8">
                    <AlertCircle className="w-12 h-12 text-[#2D3538] mx-auto" />
                    <h1 className="font-serif text-3xl text-[#2D3538]">Complete Phase 3 First</h1>
                    <p className="text-[#5B5F61]">
                        Phase 4 requires your value proposition data from Phase 3.
                    </p>
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

    // Home screen has its own layout
    if (currentScreen === 'home') {
        return (
            <PositioningStudioHome
                phase4={phase4}
                onNavigate={handleNavigate}
                onShowEvidence={handleShowEvidence}
            />
        );
    }

    const { title, subtitle } = SCREEN_CONTENT[currentScreen];

    return (
        <PhaseScreen
            phaseNumber={4}
            phaseTitle="Positioning Studio"
            currentStepId={currentScreen}
            steps={STEPS}
            title={title}
            subtitle={subtitle}
            onBack={goBack}
            onStepClick={handleStepClick}
            showContinue={false}
        >
            {/* Screen: Market Frame */}
            {currentScreen === 'market-frame' && (
                <MarketFrameScreen
                    phase4={phase4}
                    onUpdate={handleUpdate}
                    onContinue={goNext}
                    onBack={goBack}
                />
            )}

            {/* Screen: Competition */}
            {currentScreen === 'alternatives' && (
                <CompetitionScreen
                    phase4={phase4}
                    onUpdate={handleUpdate}
                    onShowEvidence={handleShowEvidence}
                    onContinue={goNext}
                    onBack={goBack}
                />
            )}

            {/* Screen: Unique Attributes */}
            {currentScreen === 'attributes' && (
                <UniqueAttributesScreen
                    phase4={phase4}
                    onUpdate={handleUpdate}
                    onShowEvidence={handleShowEvidence}
                    onContinue={goNext}
                    onBack={goBack}
                />
            )}

            {/* Screen: Value Translation */}
            {currentScreen === 'value' && (
                <ValueTranslationScreen
                    phase4={phase4}
                    onUpdate={handleUpdate}
                    onContinue={goNext}
                    onBack={goBack}
                />
            )}

            {/* Screen: Who Cares */}
            {currentScreen === 'who-cares' && (
                <WhoCareScreen
                    phase4={phase4}
                    onUpdate={handleUpdate}
                    onContinue={goNext}
                    onBack={goBack}
                />
            )}

            {/* Screen: Positioning Statement */}
            {currentScreen === 'statement' && (
                <PositioningStatementBuilder
                    phase4={phase4}
                    onUpdate={handleUpdate}
                    onContinue={goNext}
                    onBack={goBack}
                />
            )}

            {/* Screen: Perceptual Map */}
            {currentScreen === 'perceptual-map' && (
                <PerceptualMapScreen
                    phase4={phase4}
                    onUpdate={handleUpdate}
                    onContinue={goNext}
                    onBack={goBack}
                />
            )}

            {/* Screen: Proof Integrity */}
            {currentScreen === 'proof' && (
                <ProofIntegrityScreen
                    phase4={phase4}
                    onUpdate={handleUpdate}
                    onContinue={goNext}
                    onBack={goBack}
                />
            )}

            {/* Screen: Lock & Export */}
            {currentScreen === 'lock' && (
                <LockExportScreen
                    phase4={phase4}
                    onLock={handleLock}
                    onBack={goBack}
                />
            )}
        </PhaseScreen>
    );
}
