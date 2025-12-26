'use client';

import { OnboardingScaffold } from '@/components/onboarding/OnboardingScaffold';
import { SoundbiteStudio } from '@/components/phase6';
import { useOnboarding } from '@/hooks/useOnboarding';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { toast } from 'sonner';

export default function Phase6Page() {
    const router = useRouter();
    const { data, isLoading, isSaving, updateData, saveProgress } = useOnboarding();
    const [isGenerating, setIsGenerating] = useState(false);

    const handleGenerate = async () => {
        setIsGenerating(true);
        try {
            const response = await fetch('/api/v1/synthesis/soundbites', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jtbd: data.phase3?.jtbd,
                    hierarchy: data.phase3?.hierarchy,
                    awareness: data.phase3?.awarenessMatrix,
                    proof_points: (data.proof as any)?.evidence?.map((e: any) => e.content) || []
                })
            });

            if (!response.ok) throw new Error('Synthesis failed');
            
            const result = await response.json();
            
            updateData(prev => ({
                ...prev,
                phase6: {
                    ...prev.phase6!,
                    soundbites: result.soundbites.map((sb: any) => ({
                        id: Math.random().toString(36).substr(2, 9),
                        type: sb.type,
                        text: sb.content,
                        isLocked: false,
                        alternatives: [
                            "Alternative version of " + sb.content.substring(0, 30) + "...",
                            "A more direct take on this " + sb.type.replace('_', ' ') + " message."
                        ]
                    }))
                }
            }));
            
            toast.success('Soundbites generated!');
        } catch (error) {
            console.error(error);
            toast.error('Failed to generate soundbites.');
        } finally {
            setIsGenerating(false);
        }
    };

    const handleUpdate = (id: string, text: string) => {
        updateData(prev => ({
            ...prev,
            phase6: {
                ...prev.phase6!,
                soundbites: prev.phase6!.soundbites.map(sb => sb.id === id ? { ...sb, text } : sb)
            }
        }));
    };

    const handleLock = (id: string) => {
        updateData(prev => ({
            ...prev,
            phase6: {
                ...prev.phase6!,
                soundbites: prev.phase6!.soundbites.map(sb => sb.id === id ? { ...sb, isLocked: !sb.isLocked } : sb)
            }
        }));
    };

    const handleSelectVariation = (id: string, text: string) => {
        updateData(prev => ({
            ...prev,
            phase6: {
                ...prev.phase6!,
                soundbites: prev.phase6!.soundbites.map(sb => sb.id === id ? { ...sb, text } : sb)
            }
        }));
    };

    const handleContinue = async () => {
        const lockedCount = data.phase6?.soundbites?.filter(sb => sb.isLocked).length || 0;
        if (lockedCount < 7) {
            toast.error('Validate all 7 soundbites.', { description: 'Each resonance vector must be locked to proceed.' });
            return;
        }

        const success = await saveProgress();
        if (success) {
            toast.success('Precision Soundbites locked.');
            router.push('/foundation/results');
        }
    };

    return (
        <OnboardingScaffold
            phase={6}
            title="Precision Studio"
            subtitle="Forge your final 7 Precision Soundbites for market dominance."
            onContinue={handleContinue}
            isLoading={isLoading}
            isSaving={isSaving}
        >
            <SoundbiteStudio
                soundbites={data.phase6?.soundbites || []}
                onGenerate={handleGenerate}
                onUpdate={handleUpdate}
                onLock={handleLock}
                onSelectVariation={handleSelectVariation}
                isGenerating={isGenerating}
            />
        </OnboardingScaffold>
    );
}