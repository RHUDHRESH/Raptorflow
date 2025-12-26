'use client';

import { OnboardingScaffold } from '@/components/onboarding/OnboardingScaffold';
import { useRouter } from 'next/navigation';

export default function Phase5Page() {
    const router = useRouter();

    return (
        <OnboardingScaffold
            phase={5}
            title="Mechanism & Proof"
            subtitle="Build your unique moat and back it with undeniable evidence."
            onContinue={() => router.push('/foundation/phase6')}
        >
            <div className="flex-1 flex flex-col gap-8">
                {/* Differentiation Auditor will go here */}
                <div className="p-8 border-2 border-dashed border-[#C0C1BE] rounded-xl text-center text-[#9D9F9F]">
                    Technical Differentiation Auditor & Proof Vault (Task 4.2 & 4.3)
                </div>
            </div>
        </OnboardingScaffold>
    );
}
