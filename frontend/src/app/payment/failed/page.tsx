"use client";

import { useRouter } from 'next/navigation';
import { X, RefreshCw } from 'lucide-react';
import dynamic from 'next/dynamic';
import { BlueprintCard } from '@/components/ui/BlueprintCard';

const BlueprintButton = dynamic(() => import('@/components/ui/BlueprintButton').then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import('@/components/ui/BlueprintButton').then(mod => ({ default: mod.SecondaryButton })), { ssr: false });

export const runtime = 'edge';

export default function PaymentFailedPage() {
  const router = useRouter();

  const handleRetryPayment = () => {
    router.push('/pricing');
  };

  const handleGoHome = () => {
    router.push('/');
  };

  return (
    <div className="min-h-screen bg-[var(--canvas)] relative overflow-hidden">
      {/* Blueprint grid background */}
      <div className="fixed inset-0 blueprint-grid-major pointer-events-none opacity-30" />

      <div className="relative z-20 min-h-screen flex items-center justify-center px-4">
        <BlueprintCard
          figure="FIG. 07"
          code="FAILED"
          showCorners
          showMeasurements
          variant="default"
          padding="lg"
          className="w-full max-w-md text-center"
        >
          {/* Failed Icon */}
          <div className="w-20 h-20 rounded-full bg-[var(--error-light)] flex items-center justify-center mx-auto mb-6">
            <X size={40} className="text-[var(--error)]" />
          </div>

          {/* Title */}
          <h1 className="font-serif text-3xl text-[var(--ink)] mb-4">
            Payment Failed
          </h1>

          {/* Message */}
          <p className="text-[var(--secondary)] mb-8">
            We couldn't process your payment. This could be due to a network issue or payment method problem.
          </p>

          {/* Troubleshooting */}
          <div className="bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius)] p-4 mb-8 text-left">
            <p className="text-sm font-semibold text-[var(--ink)] mb-2">What you can do:</p>
            <ul className="text-sm text-[var(--secondary)] space-y-1">
              <li>ΓÇó Check your internet connection</li>
              <li>ΓÇó Ensure sufficient funds in your account</li>
              <li>ΓÇó Try a different payment method</li>
              <li>ΓÇó Contact your bank if the issue persists</li>
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <BlueprintButton
              size="default"
              className="w-full"
              onClick={handleRetryPayment}
            >
              <RefreshCw size={16} />
              Try Again
            </BlueprintButton>

            <SecondaryButton
              size="lg"
              className="w-full"
              onClick={handleGoHome}
            >
              Go to Homepage
            </SecondaryButton>
          </div>

          {/* Support info */}
          <p className="mt-6 text-xs text-[var(--ink-muted)] font-technical">
            Need help? Contact our support team at support@raptorflow.com
          </p>
        </BlueprintCard>
      </div>
    </div>
  );
}
