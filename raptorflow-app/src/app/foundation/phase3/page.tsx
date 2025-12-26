'use client';

import { OnboardingScaffold } from '@/components/onboarding/OnboardingScaffold';
import { useRouter } from 'next/navigation';

export default function Phase3Page() {
    const router = useRouter();

    return (
        <OnboardingScaffold
            phase={3}
            title="Foundation & Jobs"
            subtitle="Define exactly why your customers hire your product."
            onContinue={() => router.push('/foundation/phase4')}
        >
            <div className="flex-1 flex flex-col gap-8">
                {/* JTBD Canvas will go here */}
                <div className="p-8 border-2 border-dashed border-[#C0C1BE] rounded-xl text-center text-[#9D9F9F]">
                    JTBD Canvas Component (Task 3.1)
                </div>
            </div>
        </OnboardingScaffold>
    );
}
