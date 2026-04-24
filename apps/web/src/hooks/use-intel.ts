"use client";

import { useQuery } from "@tanstack/react-query";
import { ApiError, apiFetch } from "@/lib/api";

export interface IntelSignal {
  id: string;
  userId: string;
  type: string;
  source: string;
  title: string;
  summary: string;
  detail: string | null;
  severity: string;
  isRead: boolean;
  isArchived: boolean;
  relatedTo: string | null;
  createdAt: string;
}

interface IntelSignalsResponse {
  signals: IntelSignal[];
}

export function useIntelSignals(category?: string) {
  return useQuery({
    queryKey: ["intel", category ?? "all"],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (category) params.set("type_", category);
      const query = params.toString();
      return apiFetch<IntelSignalsResponse>(`/api/v1/intel/signals${query ? `?${query}` : ""}`, {
        auth: true,
      });
    },
    staleTime: 30_000,
  });
}

export function useCompetitorSnapshots() {
  return useQuery({
    queryKey: ["intel", "competitors"],
    queryFn: () => apiFetch<{ snapshots: unknown[] }>("/api/v1/intel/competitors", { auth: true }),
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
