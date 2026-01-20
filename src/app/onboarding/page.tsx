"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { Loader2, Zap } from "lucide-react";
import { BlueprintButton } from "@/components/ui/BlueprintButton";

export default function OnboardingPage() {
  const router = useRouter();
  const { session, initSession } = useOnboardingStore();

  useEffect(() => {
    const checkStatus = async () => {
      const { data: { session: authSession } } = await supabase.auth.getSession();
      
      if (!authSession) {
        router.push("/login");
        return;
      }

      // Check if user already has a workspace or profile is active
      const [{ data: profile }, { data: workspace }] = await Promise.all([
        supabase
          .from('profiles')
          .select('onboarding_status, workspace_id')
          .eq('id', authSession.user.id)
          .single(),
        supabase
          .from('workspaces')
          .select('id')
          .or(`owner_id.eq.${authSession.user.id},user_id.eq.${authSession.user.id}`)
          .limit(1)
          .maybeSingle()
      ]);

      const effectiveWorkspaceId = workspace?.id || profile?.workspace_id;

      // If they have a workspace and are active, redirect to dashboard
      if (effectiveWorkspaceId && profile?.onboarding_status === 'active') {
        // Sync metadata if missing
        if (!authSession.user.user_metadata?.workspace_id) {
          await supabase.auth.updateUser({
            data: { workspace_id: effectiveWorkspaceId, onboarding_status: 'active' }
          });
        }
        router.push("/dashboard");
        return;
      }

      // Initialize session if not exists and redirect to first step
      if (!session?.sessionId) {
        initSession(`session-${Date.now()}`, "New Client");
      }

      // If they have a workspace but not active, they might be mid-onboarding
      // For now, just continue to step 1 or where they left off
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
