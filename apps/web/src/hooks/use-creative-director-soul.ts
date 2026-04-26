"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { creativeDirectorApi, CreativeDirectorDryRunRequest } from "@/lib/api";

export function useCreativeDirectorDefault() {
  return useQuery({
    queryKey: ["creative-director", "default"],
    queryFn: () => creativeDirectorApi.ensureDefault(),
  });
}

export function useEnsureCreativeDirectorDefault() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => creativeDirectorApi.ensureDefault(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["creative-director", "default"] });
    },
  });
}

export function useCreativeDirectorDryRun() {
  return useMutation({
    mutationFn: (body: CreativeDirectorDryRunRequest) => creativeDirectorApi.dryRun(body),
  });
}
