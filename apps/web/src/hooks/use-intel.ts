"use client";

import { useQuery } from "@tanstack/react-query";
import { ApiError, apiFetch } from "@/lib/api";

export interface IntelSignal {
  id: string;
  user_id: string;
  type: string;
  source: string;
  title: string;
  summary: string;
  detail: string | null;
  severity: string;
  is_read: boolean;
  is_archived: boolean;
  related_to: string | null;
  created_at: string;
}

interface IntelSignalsResponse {
  signals: IntelSignal[];
}

export function useIntelSignals(category?: string) {
  return useQuery({
    queryKey: ["intel", category ?? "all"],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (category) params.set("type", category);
      const query = params.toString();
      return apiFetch<IntelSignalsResponse>(`/api/v1/intel/signals${query ? `?${query}` : ""}`, {
        auth: true,
      });
    },
    staleTime: 30_000,
  });
}

interface CompetitorSnapshotsResponse {
  competitor_snapshots: CompetitorSnapshot[];
}

export interface CompetitorSnapshot {
  id: string;
  user_id: string;
  competitor_name: string;
  website: string | null;
  snapshot: unknown;
  last_analyzed_at: string;
  created_at: string;
}

export function useCompetitorSnapshots() {
  return useQuery({
    queryKey: ["intel", "competitors"],
    queryFn: () =>
      apiFetch<CompetitorSnapshotsResponse>("/api/v1/intel/competitors", { auth: true }),
    staleTime: 30_000,
  });
}

export function useIntelOverview() {
  return useQuery({
    queryKey: ["intel", "overview"],
    queryFn: () => apiFetch<{ signals: IntelSignal[] }>("/api/v1/intel", { auth: true }),
    staleTime: 30_000,
  });
}

export function useResearchRuns() {
  return useQuery({
    queryKey: ["intel", "runs"],
    queryFn: () => apiFetch<{ runs: unknown[] }>("/api/v1/intel/runs", { auth: true }),
    staleTime: 60_000,
  });
}

export function useIntelDocuments() {
  return useQuery({
    queryKey: ["intel", "documents"],
    queryFn: () => apiFetch<{ documents: unknown[] }>("/api/v1/intel/documents", { auth: true }),
    staleTime: 60_000,
  });
}
