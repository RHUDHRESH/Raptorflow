'use client';

import { OnboardingScaffold } from '@/components/onboarding/OnboardingScaffold';
import { useRouter } from 'next/navigation';

export default function Phase4Page() {
    const router = useRouter();

    return (
        <OnboardingScaffold
            phase={4}
            title="Agitation & Identity"
            subtitle="Amplify the pain points that drive real business decisions."
            onContinue={() => router.push('/foundation/phase5')}
        >
            <div className="flex-1 flex flex-col gap-8">
                {/* Research Boards will go here */}
                <div className="p-8 border-2 border-dashed border-[#C0C1BE] rounded-xl text-center text-[#9D9F9F]">
                    Interactive Research Boards (Task 4.1)
                </div>
            </div>
        </OnboardingScaffold>
    );
}
