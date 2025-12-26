'use client';

import { OnboardingScaffold } from '@/components/onboarding/OnboardingScaffold';
import { ResearchWhiteboard } from '@/components/phase4';
import { useOnboarding } from '@/hooks/useOnboarding';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

export default function Phase4Page() {
    const router = useRouter();
    const { data, isLoading, isSaving, updateData, saveProgress } = useOnboarding();

    const handlePainsChange = (pains: any[]) => {
        updateData(prev => ({
            ...prev,
            phase4: {
                ...prev.phase4!,
                competitiveAlternatives: {
                    ...prev.phase4!.competitiveAlternatives,
                    statusQuo: pains.map(p => ({
                        id: p.id,
                        name: p.text,
                        whatUsedFor: p.category,
                        whatBreaks: 'Current workflow',
                        whyTolerated: 'No better alternative',
                        evidence: [],
                        isConfirmed: true
                    }))
                }
            }
        }));
    };

    const handleContinue = async () => {
        const success = await saveProgress();
        if (success) {
            toast.success('Research aggregated.');
            router.push('/foundation/phase5');
        }
    };

    // Map internal schema to whiteboard schema
    const mappedPains = (data.phase4?.competitiveAlternatives?.statusQuo || []).map(p => ({
        id: p.id,
        text: p.name,
        category: (p.whatUsedFor as any) || 'functional',
        severity: 3
    }));

    return (
        <OnboardingScaffold
            phase={4}
            title="Agitation & Identity"
            subtitle="Amplify the pain points that drive real business decisions."
            onContinue={handleContinue}
            isLoading={isLoading}
            isSaving={isSaving}
        >
            <ResearchWhiteboard
                pains={mappedPains}
                onChange={handlePainsChange}
            />
        </OnboardingScaffold>
    );
}
