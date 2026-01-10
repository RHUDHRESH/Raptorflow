"use client";

import { useState, useEffect, Suspense, lazy } from "react";
import { useParams, useRouter } from "next/navigation";
import { OnboardingShell } from "@/components/onboarding/OnboardingShell";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { Loader2 } from "lucide-react";

// Dynamic imports for all 25 step components - matching actual file names
const Step1EvidenceVault = lazy(() => import("@/components/onboarding/steps/Step1EvidenceVault"));
const Step2AutoExtraction = lazy(() => import("@/components/onboarding/steps/Step2AutoExtraction"));
const Step3Contradictions = lazy(() => import("@/components/onboarding/steps/Step3Contradictions"));
const Step4ValidateTruthSheet = lazy(() => import("@/components/onboarding/steps/Step4ValidateTruthSheet"));
const Step5BrandAudit = lazy(() => import("@/components/onboarding/steps/Step5BrandAudit"));
const Step6OfferPricing = lazy(() => import("@/components/onboarding/steps/Step6OfferPricing"));
const Step7ResearchBrief = lazy(() => import("@/components/onboarding/steps/Step7ResearchBrief"));
const Step8CompetitiveAlternatives = lazy(() => import("@/components/onboarding/steps/Step8CompetitiveAlternatives"));
const Step9CompetitiveLadder = lazy(() => import("@/components/onboarding/steps/Step9CompetitiveLadder"));
const Step10CategorySelection = lazy(() => import("@/components/onboarding/steps/Step10CategorySelection"));
const Step11DifferentiatedCapabilities = lazy(() => import("@/components/onboarding/steps/Step11DifferentiatedCapabilities"));
const Step12CapabilityMatrix = lazy(() => import("@/components/onboarding/steps/Step12CapabilityMatrix"));
const Step13PositioningStatements = lazy(() => import("@/components/onboarding/steps/Step13PositioningStatements"));
const Step14FocusSacrifice = lazy(() => import("@/components/onboarding/steps/Step14FocusSacrifice"));
const Step15ICPProfiles = lazy(() => import("@/components/onboarding/steps/Step15ICPProfiles"));
const Step16BuyingProcess = lazy(() => import("@/components/onboarding/steps/Step16BuyingProcess"));
const Step17MessagingGuardrails = lazy(() => import("@/components/onboarding/steps/Step17MessagingGuardrails"));
const Step18SoundbitesLibrary = lazy(() => import("@/components/onboarding/steps/Step18SoundbitesLibrary"));
const Step19MessageHierarchy = lazy(() => import("@/components/onboarding/steps/Step19MessageHierarchy"));
const Step20BrandAugmentation = lazy(() => import("@/components/onboarding/steps/Step20BrandAugmentation"));
const Step21ChannelMapping = lazy(() => import("@/components/onboarding/steps/Step21ChannelMapping"));
const Step22TAMSAM = lazy(() => import("@/components/onboarding/steps/Step22TAMSAM"));
const Step23ValidationTodos = lazy(() => import("@/components/onboarding/steps/Step23ValidationTodos"));
const Step24FinalSynthesis = lazy(() => import("@/components/onboarding/steps/Step24FinalSynthesis"));
const Step25Export = lazy(() => import("@/components/onboarding/steps/Step25Export"));

// Step component mapping
const StepComponents: Record<number, React.LazyExoticComponent<React.ComponentType<any>>> = {
  1: Step1EvidenceVault,
  2: Step2AutoExtraction,
  3: Step3Contradictions,
  4: Step4ValidateTruthSheet,
  5: Step5BrandAudit,
  6: Step6OfferPricing,
  7: Step7ResearchBrief,
  8: Step8CompetitiveAlternatives,
  9: Step9CompetitiveLadder,
  10: Step10CategorySelection,
  11: Step11DifferentiatedCapabilities,
  12: Step12CapabilityMatrix,
  13: Step13PositioningStatements,
  14: Step14FocusSacrifice,
  15: Step15ICPProfiles,
  16: Step16BuyingProcess,
  17: Step17MessagingGuardrails,
  18: Step18SoundbitesLibrary,
  19: Step19MessageHierarchy,
  20: Step20BrandAugmentation,
  21: Step21ChannelMapping,
  22: Step22TAMSAM,
  23: Step23ValidationTodos,
  24: Step24FinalSynthesis,
  25: Step25Export,
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

  // Validate step range
  if (stepId < 1 || stepId > 25) {
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
