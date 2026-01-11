"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { Loader2, Zap } from "lucide-react";
import { BlueprintButton } from "@/components/ui/BlueprintButton";

export default function OnboardingPage() {
  const router = useRouter();
  const { session, initSession } = useOnboardingStore();

  useEffect(() => {
    // Initialize session if not exists and redirect to first step
    if (!session?.sessionId) {
      initSession(`session-${Date.now()}`, "New Client");
    }

    // Small delay to ensure session is initialized
    const timer = setTimeout(() => {
      router.push("/onboarding/session/step/1");
    }, 100);

    return () => clearTimeout(timer);
  }, [session, initSession, router]);

  return (
    <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-[var(--blueprint)] rounded-[var(--radius-lg)] flex items-center justify-center mx-auto mb-6">
          <Zap size={32} className="text-[var(--paper)]" />
        </div>
        <h1 className="font-serif text-3xl text-[var(--ink)] mb-4">Initializing Calibration</h1>
        <div className="flex items-center justify-center gap-3 text-[var(--muted)]">
          <Loader2 size={20} className="animate-spin" />
          <span className="font-technical text-sm">Preparing your workspace...</span>
        </div>
      </div>
    </div>
  );
}
