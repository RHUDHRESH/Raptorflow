"use client";

import { ONBOARDING_STEPS, ONBOARDING_PHASES } from "@/lib/onboarding-tokens";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — OnboardingStepLayout

   Unified wrapper for all step components to ensure consistent footer and spacing.
   ══════════════════════════════════════════════════════════════════════════════ */

interface OnboardingStepLayoutProps {
    children: React.ReactNode;
    stepId: number;
    moduleLabel?: string;  // e.g., "EVIDENCE-VAULT", "AUTO-EXTRACTION"
    itemCount?: number;    // Optional count to show in footer
}

export function OnboardingStepLayout({
    children,
    stepId,
    moduleLabel,
    itemCount
}: OnboardingStepLayoutProps) {
    const stepConfig = ONBOARDING_STEPS.find(s => s.id === stepId);
    const phase = ONBOARDING_PHASES.find(p => p.steps.includes(stepId));

    // Generate module label from step name if not provided
    const label = moduleLabel || stepConfig?.name?.toUpperCase().replace(/\s+/g, '-') || `STEP-${stepId}`;

    return (
        <div className="flex flex-col min-h-0">
            {children}
            <div className="flex justify-center pt-6 pb-2">
                <span className="font-technical text-[var(--muted)] text-[10px] tracking-wider">
                    {label} • STEP {String(stepId).padStart(2, '0')}/25
                    {itemCount !== undefined ? ` • ${itemCount} ITEMS` : ''}
                </span>
            </div>
        </div>
    );
}

export default OnboardingStepLayout;
