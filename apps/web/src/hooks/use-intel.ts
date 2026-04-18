"use client";

import { useQuery } from "@tanstack/react-query";
import { intelApi } from "@/lib/api";

export function useIntelSignals(category?: string, competitorId?: string) {
  return useQuery({
    queryKey: ["intel", "signals", { category, competitorId }],
    queryFn: () => intelApi.getSignals({ category, competitorId }),
  });
}

export function useIntelStats() {
  return useQuery({
    queryKey: ["intel", "stats"],
    queryFn: () => intelApi.getSignalStats(),
  });
}

export function useCompetitors() {
  return useQuery({
    queryKey: ["intel", "competitors"],
    queryFn: () => intelApi.getCompetitors(),
  });
}

export function useIntelOverview() {
  return useQuery({
    queryKey: ["intel", "overview"],
    queryFn: () => intelApi.getOverview(),
  });
}

export function useResearchRuns() {
  return useQuery({
    queryKey: ["intel", "runs"],
    queryFn: () => intelApi.listRuns(),
  });
}

export function useIntelDocuments() {
  return useQuery({
    queryKey: ["intel", "documents"],
    queryFn: () => intelApi.listDocuments(),
  });
}
