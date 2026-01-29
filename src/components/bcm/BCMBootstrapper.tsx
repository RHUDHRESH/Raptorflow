"use client";

import { useAuth } from "@/components/auth/AuthProvider";
import { useBcmSync } from "@/hooks/useBcmSync";

export function BCMBootstrapper() {
  const { profileStatus } = useAuth();
  useBcmSync(profileStatus.workspaceId ?? undefined);
  return null;
}
