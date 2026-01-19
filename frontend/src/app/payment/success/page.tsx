"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Check, ArrowRight } from 'lucide-react';
import dynamic from 'next/dynamic';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { useAuth } from '@/contexts/AuthContext';

const BlueprintButton = dynamic(() => import('@/components/ui/BlueprintButton').then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export const runtime = 'edge';

export default function PaymentSuccessPage() {
  const router = useRouter();
  const { refreshProfile } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const refreshAndRedirect = async () => {
      await refreshProfile();
      setLoading(false);
    };

    refreshAndRedirect();
  }, [refreshProfile]);

  const handleStartOnboarding = () => {
    router.push('/onboarding');
  };

  return (
    <div className="min-h-screen bg-[var(--canvas)] relative overflow-hidden">
      {/* Blueprint grid background */}
      <div className="fixed inset-0 blueprint-grid-major pointer-events-none opacity-30" />

      <div className="relative z-20 min-h-screen flex items-center justify-center px-4">
        <BlueprintCard
          figure="FIG. 06"
          code="SUCCESS"
          showCorners
          showMeasurements
          variant="elevated"
          padding="lg"
          className="w-full max-w-md text-center"
        >
          {/* Success Icon */}
          <div className="w-20 h-20 rounded-full bg-[var(--success-light)] flex items-center justify-center mx-auto mb-6">
            <Check size={40} className="text-[var(--success)]" />
          </div>

          {/* Title */}
          <h1 className="font-serif text-3xl text-[var(--ink)] mb-4">
            Payment Successful!
          </h1>

          {/* Message */}
          <p className="text-[var(--secondary)] mb-8">
            Welcome to RaptorFlow! Your subscription is now active. You can start using all the features included in your plan.
          </p>

          {/* Features unlocked message */}
          <div className="bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius)] p-4 mb-8">
            <p className="text-sm text-[var(--ink)] font-technical">
              Your workspace has been configured with all premium features unlocked.
            </p>
          </div>

          {/* CTA Button */}
          <BlueprintButton
            size="lg"
            className="w-full"
            onClick={handleStartOnboarding}
            disabled={loading}
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-[var(--paper)] border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                Start Onboarding
                <ArrowRight size={18} />
              </>
            )}
          </BlueprintButton>

          {/* Additional info */}
          <p className="mt-4 text-xs text-[var(--ink-muted)] font-technical">
            A confirmation email has been sent to your registered email address.
          </p>
        </BlueprintCard>
      </div>
    </div>
  );
}
