"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";

export interface Nudge {
  id: string;
  userId: string;
  type: string;
  title: string;
  body: string;
  cta: string | null;
  ctaHref: string | null;
  priority: number;
  isDismissed: boolean;
  isActioned: boolean;
  expiresAt: string | null;
  trigger: string;
  createdAt: string;
}

interface NudgesResponse {
  nudges: Nudge[];
  totalCount: number;
}

export function useNudges() {
  return useQuery({
    queryKey: ["nudges"],
    queryFn: () => apiFetch<NudgesResponse>("/api/nudges", { auth: true }),
    staleTime: 30_000,
  });
}

export function useDismissNudge() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (nudgeId: string) =>
      apiFetch(`/api/nudges/${nudgeId}`, {
        method: "PATCH",
        body: { isDismissed: true },
        auth: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["nudges"] });
    },
  });
}
