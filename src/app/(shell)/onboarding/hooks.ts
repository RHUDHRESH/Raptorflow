"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { workspacesService } from "@/services/workspaces.service";
import { notify } from "@/lib/notifications";

interface UseSaveAndExitProps {
  workspaceId: string | null;
  formData: Record<string, string>;
}

interface UseSaveAndExitReturn {
  handleSaveAndExit: () => Promise<void>;
  isSaving: boolean;
}

export function useSaveAndExit({ workspaceId, formData }: UseSaveAndExitProps): UseSaveAndExitReturn {
  const router = useRouter();
  const [isSaving, setIsSaving] = useState(false);

  const handleSaveAndExit = useCallback(async () => {
    if (!workspaceId) {
      notify.error("No workspace found");
      router.push("/dashboard");
      return;
    }

    setIsSaving(true);

    try {
      // Convert form data to proper format for API
      const payloadAnswers: Record<string, string | string[]> = {};

      Object.entries(formData).forEach(([key, value]) => {
        const listFields = [
          "top_pain_points",
          "top_goals",
          "competitors",
          "brand_tone",
          "banned_phrases",
          "channel_priorities",
          "proof_points",
          "constraints_and_guardrails",
        ];

        if (listFields.includes(key)) {
          payloadAnswers[key] = value
            .split(/[\n,;]+/)
            .map((s) => s.trim())
            .filter(Boolean);
        } else {
          payloadAnswers[key] = value;
        }
      });

      // Save progress to backend
      await workspacesService.upsertOnboardingAnswers(workspaceId, {
        schema_version: "1.0",
        answers: payloadAnswers,
      });

      notify.success("Progress saved!");
    } catch (error: any) {
      notify.error(error?.message || "Failed to save progress");
    } finally {
      // Always navigate to dashboard, even if save fails
      router.push("/dashboard");
    }
  }, [workspaceId, formData, router]);

  return { handleSaveAndExit, isSaving };
}
