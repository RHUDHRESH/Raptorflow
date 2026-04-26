"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { strategistApi, StrategistDryRunRequest } from "@/lib/api";

export function useStrategistDefault() {
  return useQuery({
    queryKey: ["strategist", "default"],
    queryFn: () => strategistApi.ensureDefault(),
  });
}

export function useEnsureStrategistDefault() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => strategistApi.ensureDefault(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["strategist", "default"] });
    },
  });
}

export function useStrategistDryRun() {
  return useMutation({
    mutationFn: (body: StrategistDryRunRequest) => strategistApi.dryRun(body),
  });
}
