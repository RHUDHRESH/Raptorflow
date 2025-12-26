'use client';

import { OnboardingScaffold } from '@/components/onboarding/OnboardingScaffold';
import { useRouter } from 'next/navigation';

export default function Phase6Page() {
    const router = useRouter();

    return (
        <OnboardingScaffold
            phase={6}
            title="Precision Studio"
            subtitle="Forge your final 7 Precision Soundbites for market dominance."
            onContinue={() => router.push('/foundation/results')}
        >
            <div className="flex-1 flex flex-col gap-8">
                {/* Soundbite Studio will go here */}
                <div className="p-8 border-2 border-dashed border-[#C0C1BE] rounded-xl text-center text-[#9D9F9F]">
                    Precision Soundbite Studio (Task 5.1 - 5.3)
                </div>
            </div>
        </OnboardingScaffold>
    );
}
