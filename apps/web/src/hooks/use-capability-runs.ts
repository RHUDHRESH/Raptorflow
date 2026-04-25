"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { capabilitiesApi, CreateCapabilityRunRequest } from "@/lib/api";

export function useCapabilityRuns(limit = 50) {
  return useQuery({
    queryKey: ["capability-runs", limit],
    queryFn: () => capabilitiesApi.listRuns(limit),
  });
}

export function useCapabilityRun(id: string) {
  return useQuery({
    queryKey: ["capability-runs", id],
    queryFn: () => capabilitiesApi.getRun(id),
    enabled: !!id,
  });
}

export function useCreateCapabilityRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateCapabilityRunRequest) => capabilitiesApi.createRun(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["capability-runs"] });
    },
  });
}
