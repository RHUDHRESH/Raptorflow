"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { growthOperatorApi, GrowthOperatorDryRunRequest } from "@/lib/api";

export function useGrowthOperatorDefault() {
  return useQuery({
    queryKey: ["growth-operator", "default"],
    queryFn: () => growthOperatorApi.ensureDefault(),
  });
}

export function useEnsureGrowthOperatorDefault() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => growthOperatorApi.ensureDefault(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["growth-operator", "default"] });
    },
  });
}

export function useGrowthOperatorDryRun() {
  return useMutation({
    mutationFn: (body: GrowthOperatorDryRunRequest) => growthOperatorApi.dryRun(body),
  });
}
