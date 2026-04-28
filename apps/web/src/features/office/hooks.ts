/**
 * RaptorFlow Office API Hooks
 *
 * TanStack Query hooks for Office data.
 * No fake data. Honest unavailable states.
 */

import { useQuery } from "@tanstack/react-query";
import { officeApi } from "@/lib/api";
import type { OfficeState } from "./types";

export function useOfficeState() {
  return useQuery<OfficeState>({
    queryKey: ["office", "state"],
    queryFn: async () => {
      const data = await officeApi.getState();
      return {
        activeCampaigns: data.activeCampaigns ?? 0,
        activeCouncilSessions: data.activeCouncilSessions ?? 0,
        openNudges: data.openNudges ?? 0,
        recentMuseConversations: data.recentMuseConversations ?? 0,
      };
    },
    refetchInterval: 30_000,
    staleTime: 15_000,
  });
}

export function useOfficeCampaignFronts() {
  return useQuery({
    queryKey: ["office", "campaigns"],
    queryFn: async () => {
      try {
        const res = await fetch("/api/v1/campaigns", { credentials: "include" });
        if (!res.ok) return null;
        const data = await res.json();
        return Array.isArray(data?.campaigns) ? data.campaigns : null;
      } catch {
        return null;
      }
    },
    staleTime: 30_000,
  });
}

export function useOfficeCouncilActivity() {
  return useQuery({
    queryKey: ["office", "council"],
    queryFn: async () => {
      try {
        const res = await fetch("/api/v1/council", { credentials: "include" });
        if (!res.ok) return null;
        const data = await res.json();
        return Array.isArray(data?.sessions) ? data.sessions.slice(0, 5) : null;
      } catch {
        return null;
      }
    },
    staleTime: 30_000,
  });
}

export function useOfficeRecentArtifacts() {
  return useQuery({
    queryKey: ["office", "artifacts"],
    queryFn: async () => {
      try {
        const res = await fetch("/api/v1/content", { credentials: "include" });
        if (!res.ok) return null;
        const data = await res.json();
        return Array.isArray(data) ? data.slice(0, 5) : null;
      } catch {
        return null;
      }
    },
    staleTime: 60_000,
  });
}
