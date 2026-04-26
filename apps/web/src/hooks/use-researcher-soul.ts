"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { researcherApi, ResearcherDryRunRequest } from "@/lib/api";

export function useResearcherDefault() {
  return useQuery({
    queryKey: ["researcher", "default"],
    queryFn: () => researcherApi.ensureDefault(),
  });
}

export function useEnsureResearcherDefault() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => researcherApi.ensureDefault(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["researcher", "default"] });
    },
  });
}

export function useResearcherDryRun() {
  return useMutation({
    mutationFn: (body: ResearcherDryRunRequest) => researcherApi.dryRun(body),
  });
}
