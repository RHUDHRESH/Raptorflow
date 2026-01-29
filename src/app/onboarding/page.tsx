"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { clientAuth } from '@/lib/auth-service';
import { Loader2, Zap } from "lucide-react";
import { BlueprintButton } from "@/components/ui/BlueprintButton";

export default function OnboardingPage() {
  const router = useRouter();
  const { session, initSession } = useOnboardingStore();

  useEffect(() => {
    const checkStatus = async () => {
      const user = await clientAuth.getCurrentUser();

      if (!user) {
        router.push("/signin");
        return;
      }

      // If they have a workspace and are active, redirect to dashboard
      if (user.workspaceId && user.onboardingStatus === 'active') {
        router.push("/dashboard");
        return;
      }

      if (user.subscriptionStatus !== 'active') {
        const status = user.subscriptionStatus ?? 'inactive';
        router.push(`/onboarding/plans?paymentStatus=${status}`);
        return;
      }

      // Initialize session if not exists and redirect to first step
      if (!session?.sessionId) {
        initSession(`session-${Date.now()}`, "New Client");
      }

      router.push("/onboarding/session/step/1");
    };

    checkStatus();
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
