"use client";

import { useState, useEffect, Suspense, lazy } from "react";
import { useParams, useRouter } from "next/navigation";
import { OnboardingShell } from "@/components/onboarding/OnboardingShell";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { useAuth } from "@/components/auth/AuthProvider";
import { Loader2 } from "lucide-react";

// Dynamic imports for all step components
const Step1EvidenceVault = lazy(() => import("@/components/onboarding/steps/Step1EvidenceVault"));
const Step2AutoExtraction = lazy(() => import("@/components/onboarding/steps/Step2AutoExtraction"));
const Step3Contradictions = lazy(() => import("@/components/onboarding/steps/Step3Contradictions"));
const Step4ValidateTruthSheet = lazy(() => import("@/components/onboarding/steps/Step4ValidateTruthSheet"));
const Step5OfferPricing = lazy(() => import("@/components/onboarding/steps/Step6OfferPricing"));
const Step6ResearchBrief = lazy(() => import("@/components/onboarding/steps/Step7ResearchBrief"));
const Step7CompetitiveAlternatives = lazy(() => import("@/components/onboarding/steps/Step8CompetitiveAlternatives"));
const Step8CompetitiveLadder = lazy(() => import("@/components/onboarding/steps/Step9CompetitiveLadder"));
const Step9CategorySelection = lazy(() => import("@/components/onboarding/steps/Step10CategorySelection"));
const Step10DifferentiatedCapabilities = lazy(() => import("@/components/onboarding/steps/Step11DifferentiatedCapabilities"));
const Step11CapabilityMatrix = lazy(() => import("@/components/onboarding/steps/Step12CapabilityMatrix"));
const Step12PositioningStatements = lazy(() => import("@/components/onboarding/steps/Step12PositioningStatements"));

// Step 13, 14, 15 Refs
const Step13StrategicGap = lazy(() => import("@/components/onboarding/steps/Step13StrategicGap")); // Unused
const Step13FocusSacrifice = lazy(() => import("@/components/onboarding/steps/Step14FocusSacrifice"));
const Step14ICPProfiles = lazy(() => import("@/components/onboarding/steps/Step15ICPProfiles"));

// New Flow
const Step15BuyingProcess = lazy(() => import("@/components/onboarding/steps/Step16BuyingProcess"));
const Step16MessagingGuardrails = lazy(() => import("@/components/onboarding/steps/Step17MessagingGuardrails"));
const Step17SoundbitesLibrary = lazy(() => import("@/components/onboarding/steps/Step18SoundbitesLibrary"));
// Step 18/19 Deleted
const Step20ChannelMapping = lazy(() => import("@/components/onboarding/steps/Step21ChannelMapping"));
const Step21TAMSAM = lazy(() => import("@/components/onboarding/steps/Step22TAMSAM"));
const Step22ValidationTodos = lazy(() => import("@/components/onboarding/steps/Step23ValidationTodos"));
const Step23FinalSynthesis = lazy(() => import("@/components/onboarding/steps/Step24FinalSynthesis"));
// Step 24 Export Deleted

// Step component mapping - Sequential and Corrected
const StepComponents: Record<number, React.LazyExoticComponent<React.ComponentType<any>>> = {
  1: Step1EvidenceVault,
  2: Step2AutoExtraction,
  3: Step3Contradictions,
  4: Step4ValidateTruthSheet,
  5: Step5OfferPricing,
  6: Step6ResearchBrief,
  7: Step7CompetitiveAlternatives,
  8: Step7CompetitiveAlternatives, // Step 8 Reuse
  9: Step8CompetitiveLadder,
  10: Step9CategorySelection,
  11: Step10DifferentiatedCapabilities,
  12: Step12PositioningStatements,
  13: Step11CapabilityMatrix,      // Strategic Grid / Gap
  14: Step13FocusSacrifice,        // Focus
  15: Step14ICPProfiles,           // ICP
  16: Step15BuyingProcess,         // Education
  17: Step16MessagingGuardrails,   // Guardrails
  18: Step17SoundbitesLibrary,     // Soundbites
  19: Step20ChannelMapping,        // Channels
  20: Step21TAMSAM,                // 20: TAM/SAM (Final visual)
  21: Step21TAMSAM,                // 21: Keep mapping if needed, but user said 22 is Validation
  22: Step22ValidationTodos,       // 22: Validation Tasks
  23: Step23FinalSynthesis,        // 23: Completion
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
  const { createSession, session } = useOnboardingStore();
  const { workspace, isLoading } = useAuth();

  const stepId = parseInt(params.stepId as string);
  const StepComponent = StepComponents[stepId] || StepComponents[1];

  useEffect(() => {
    if (isLoading) return;

    const workspaceId = workspace?.workspaceId;
    if (!workspaceId) {
      router.replace("/workspace-setup");
      return;
    }

    // Initialize session if not already done
    if (!session?.sessionId) {
      createSession(workspaceId, workspace?.workspaceName || "New Client");
    }
  }, [session, createSession, workspace, isLoading, router]);

  // Validate step range
  if (stepId < 1 || stepId > 23) {
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
