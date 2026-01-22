"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { useAuth } from "@/components/auth/AuthProvider";
import { Loader2, Zap } from "lucide-react";
import { BlueprintButton } from "@/components/ui/BlueprintButton";

export default function OnboardingPage() {
  const router = useRouter();
  const { session, createSession } = useOnboardingStore();
  const { workspace, isLoading, user } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    const checkStatus = async () => {
      const workspaceId = workspace?.workspaceId;

      // If they have a workspace and onboarding is active, redirect to dashboard
      // Note: we check the active status from user profile or metadata if available
      const anyUser = user as any;
      if (workspaceId && (anyUser?.onboardingStatus === 'active' || anyUser?.user_metadata?.onboarding_status === 'active')) {
        console.log("User already onboarded, breaking loop and redirecting to dashboard");
        router.push("/dashboard");
        return;
      }

      if (!workspaceId) {
        return;
      }

      // Initialize session if not exists and redirect to first step
      if (!session?.sessionId) {
        createSession(workspaceId, workspace?.workspaceName || "New Client");
      }

      // Small delay to ensure session is initialized
      const timer = setTimeout(() => {
        router.push("/onboarding/session/step/1");
      }, 150);

      return () => clearTimeout(timer);
    };

    checkStatus();
  }, [session, createSession, router, workspace, isLoading, user]);

  if (!isLoading && !workspace?.workspaceId) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="font-serif text-3xl text-[var(--ink)]">Workspace Required</h1>
          <p className="text-[var(--muted)] text-sm">Create a workspace before starting onboarding.</p>
          <BlueprintButton onClick={() => router.push("/workspace-setup")}>Go to Workspace Setup</BlueprintButton>
        </div>
      </div>
    );
  }

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
