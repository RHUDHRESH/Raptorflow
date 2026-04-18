"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";

export interface Nudge {
  nudge_id: string;
  nudge_type: string;
  priority: "high" | "medium" | "low" | "system" | string;
  title: string;
  body: string;
  action_type?: string;
  action_data?: any;
  created_at: string;
  dismissed_at?: string | null;
}

export function useNudges() {
  return useQuery({
    queryKey: ["nudges"],
    queryFn: () => apiFetch<Nudge[]>("/api/v1/nudges", { auth: true }),
  });
}

// NOTE: dismissing is not currently in the backend router. 
// We will use standard update or a filtered list on the frontend for now if needed.
// But we should stay TRUTHFUL.
