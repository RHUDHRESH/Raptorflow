"use client";

import { useState, useEffect, Suspense, lazy } from "react";
import { useParams, useRouter } from "next/navigation";
import { OnboardingShell } from "@/components/onboarding/OnboardingShell";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { Loader2 } from "lucide-react";

// Dynamic imports for all 24 step components (Brand Audit removed)
const Step1EvidenceVault = lazy(() => import("@/components/onboarding/steps/Step1EvidenceVault"));
const Step2AutoExtraction = lazy(() => import("@/components/onboarding/steps/Step2AutoExtraction"));
const Step3Contradictions = lazy(() => import("@/components/onboarding/steps/Step3Contradictions"));
const Step4ValidateTruthSheet = lazy(() => import("@/components/onboarding/steps/Step4ValidateTruthSheet"));
// Step 5 was Brand Audit - REMOVED (no capability to analyze logos)
const Step5OfferPricing = lazy(() => import("@/components/onboarding/steps/Step6OfferPricing"));
const Step6ResearchBrief = lazy(() => import("@/components/onboarding/steps/Step7ResearchBrief"));
const Step7CompetitiveAlternatives = lazy(() => import("@/components/onboarding/steps/Step8CompetitiveAlternatives"));
const Step8CompetitiveLadder = lazy(() => import("@/components/onboarding/steps/Step9CompetitiveLadder"));
const Step9CategorySelection = lazy(() => import("@/components/onboarding/steps/Step10CategorySelection"));
const Step10DifferentiatedCapabilities = lazy(() => import("@/components/onboarding/steps/Step11DifferentiatedCapabilities"));
const Step11CapabilityMatrix = lazy(() => import("@/components/onboarding/steps/Step12CapabilityMatrix"));
const Step12PositioningStatements = lazy(() => import("@/components/onboarding/steps/Step13PositioningStatements"));
const Step13FocusSacrifice = lazy(() => import("@/components/onboarding/steps/Step14FocusSacrifice"));
const Step14ICPProfiles = lazy(() => import("@/components/onboarding/steps/Step15ICPProfiles"));
const Step15BuyingProcess = lazy(() => import("@/components/onboarding/steps/Step16BuyingProcess"));
const Step16MessagingGuardrails = lazy(() => import("@/components/onboarding/steps/Step17MessagingGuardrails"));
const Step17SoundbitesLibrary = lazy(() => import("@/components/onboarding/steps/Step18SoundbitesLibrary"));
const Step18MessageHierarchy = lazy(() => import("@/components/onboarding/steps/Step19MessageHierarchy"));
const Step19BrandAugmentation = lazy(() => import("@/components/onboarding/steps/Step20BrandAugmentation"));
const Step20ChannelMapping = lazy(() => import("@/components/onboarding/steps/Step21ChannelMapping"));
const Step21TAMSAM = lazy(() => import("@/components/onboarding/steps/Step22TAMSAM"));
const Step22ValidationTodos = lazy(() => import("@/components/onboarding/steps/Step23ValidationTodos"));
const Step23FinalSynthesis = lazy(() => import("@/components/onboarding/steps/Step24FinalSynthesis"));
const Step24Export = lazy(() => import("@/components/onboarding/steps/Step25Export"));

// Step component mapping - 24 steps total
const StepComponents: Record<number, React.LazyExoticComponent<React.ComponentType<any>>> = {
  1: Step1EvidenceVault,
  2: Step2AutoExtraction,
  3: Step3Contradictions,
  4: Step4ValidateTruthSheet,
  5: Step5OfferPricing,
  6: Step6ResearchBrief,
  7: Step7CompetitiveAlternatives,
  8: Step8CompetitiveLadder,
  9: Step9CategorySelection,
  10: Step10DifferentiatedCapabilities,
  11: Step11CapabilityMatrix,
  12: Step12PositioningStatements,
  13: Step13FocusSacrifice,
  14: Step14ICPProfiles,
  15: Step15BuyingProcess,
  16: Step16MessagingGuardrails,
  17: Step17SoundbitesLibrary,
  18: Step18MessageHierarchy,
  19: Step19BrandAugmentation,
  20: Step20ChannelMapping,
  21: Step21TAMSAM,
  22: Step22ValidationTodos,
  23: Step23FinalSynthesis,
  24: Step24Export,
};

function StepLoadingFallback() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-12 h-12 rounded-[var(--radius-md)] bg-[var(--blueprint)] flex items-center justify-center mb-4">
        <Loader2 size={24} className="text-[var(--paper)] animate-spin" />
      </div>
      <p className="font-technical text-[var(--muted)]">LOADING STEP...</p>
    </div>
  );
}

export default function OnboardingStepPage() {
  const params = useParams();
  const router = useRouter();
  const { initSession, currentStep, session } = useOnboardingStore();

  const stepId = parseInt(params.stepId as string);
  const StepComponent = StepComponents[stepId] || StepComponents[1];

  useEffect(() => {
    // Initialize session if not already done
    if (!session?.sessionId) {
      initSession(`session-${Date.now()}`, "New Client");
    }
  }, [session, initSession]);

  // Validate step range (now 24 steps)
  if (stepId < 1 || stepId > 24) {
    router.replace("/onboarding/session/step/1");
    return null;
  }

  return (
    <OnboardingShell stepId={stepId}>
      <Suspense fallback={<StepLoadingFallback />}>
        <StepComponent />
      </Suspense>
    </OnboardingShell>
  );
}
