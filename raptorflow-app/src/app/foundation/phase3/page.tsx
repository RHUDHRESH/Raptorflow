'use client';

import { OnboardingScaffold } from '@/components/onboarding/OnboardingScaffold';
import { JTBDCanvas, MessageHierarchyPyramid, AwarenessMatrix } from '@/components/phase3';
import { useOnboarding } from '@/hooks/useOnboarding';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { toast } from 'sonner';

export default function Phase3Page() {
    const router = useRouter();
    const { data, isLoading, isSaving, updateData, saveProgress } = useOnboarding();
    const [step, setStep] = useState<'jtbd' | 'hierarchy' | 'awareness'>('jtbd');

    const handleJobChange = (field: 'functional' | 'emotional' | 'social', value: string) => {
        updateData(prev => ({
            ...prev,
            phase3: {
                ...prev.phase3!,
                jtbd: {
                    ...prev.phase3!.jtbd,
                    [field]: value
                }
            }
        }));
    };

    const handleHierarchyChange = (field: string, value: any) => {
        updateData(prev => ({
            ...prev,
            phase3: {
                ...prev.phase3!,
                hierarchy: {
                    ...prev.phase3!.hierarchy!,
                    [field]: value
                }
            }
        }));
    };

    const handleAwarenessChange = (field: string, value: string) => {
        updateData(prev => ({
            ...prev,
            phase3: {
                ...prev.phase3!,
                awarenessMatrix: {
                    ...prev.phase3!.awarenessMatrix!,
                    [field]: value
                }
            }
        }));
    };

    const handleContinue = async () => {
        if (step === 'jtbd') {
            setStep('hierarchy');
            return;
        }
        if (step === 'hierarchy') {
            setStep('awareness');
            return;
        }

        const success = await saveProgress();
        if (success) {
            toast.success('Foundation saved.');
            router.push('/foundation/phase4');
        }
    };

    const handleBack = () => {
        if (step === 'awareness') {
            setStep('hierarchy');
            return;
        }
        if (step === 'hierarchy') {
            setStep('jtbd');
            return;
        }
        router.back();
    };

    return (
        <OnboardingScaffold
            phase={3}
            title={step === 'jtbd' ? "Foundation & Jobs" : step === 'hierarchy' ? "Brand Hierarchy" : "Awareness Matrix"}
            subtitle={step === 'jtbd' ? "Define exactly why your customers hire your product." : step === 'hierarchy' ? "Structure your brand message from essence to pillars." : "Map your strategy across the customer awareness tiers."}
            onContinue={handleContinue}
            onBack={handleBack}
            isLoading={isLoading}
            isSaving={isSaving}
        >
            {step === 'jtbd' && (
                <JTBDCanvas
                    functional={data.phase3?.jtbd?.functional || ''}
                    emotional={data.phase3?.jtbd?.emotional || ''}
                    social={data.phase3?.jtbd?.social || ''}
                    onChange={handleJobChange}
                />
            )}
            {step === 'hierarchy' && (
                <MessageHierarchyPyramid
                    essence={data.phase3?.hierarchy?.essence || ''}
                    coreMessage={data.phase3?.hierarchy?.coreMessage || ''}
                    pillars={data.phase3?.hierarchy?.pillars || []}
                    onChange={handleHierarchyChange}
                />
            )}
            {step === 'awareness' && (
                <AwarenessMatrix
                    matrix={data.phase3?.awarenessMatrix || { unaware: '', problem: '', solution: '', product: '', most: '' }}
                    onChange={handleAwarenessChange}
                />
            )}
        </OnboardingScaffold>
    );
}
