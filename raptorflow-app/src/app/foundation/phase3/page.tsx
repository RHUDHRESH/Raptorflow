'use client';

import { OnboardingScaffold } from '@/components/onboarding/OnboardingScaffold';
import { JTBDCanvas } from '@/components/phase3';
import { useOnboarding } from '@/hooks/useOnboarding';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

export default function Phase3Page() {
    const router = useRouter();
    const { data, isLoading, isSaving, updateData, saveProgress } = useOnboarding();

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

    const handleContinue = async () => {
        const success = await saveProgress();
        if (success) {
            toast.success('Foundation saved.');
            router.push('/foundation/phase4');
        }
    };

    return (
        <OnboardingScaffold
            phase={3}
            title="Foundation & Jobs"
            subtitle="Define exactly why your customers hire your product."
            onContinue={handleContinue}
            isLoading={isLoading}
            isSaving={isSaving}
        >
            <JTBDCanvas
                functional={data.phase3?.jtbd?.functional || ''}
                emotional={data.phase3?.jtbd?.emotional || ''}
                social={data.phase3?.jtbd?.social || ''}
                onChange={handleJobChange}
            />
        </OnboardingScaffold>
    );
}
