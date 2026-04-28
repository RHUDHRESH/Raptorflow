"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { analystApi, AnalystDryRunRequest } from "@/lib/api";

export function useAnalystDefault() {
  return useQuery({
    queryKey: ["analyst", "default"],
    queryFn: () => analystApi.ensureDefault(),
  });
}

export function useEnsureAnalystDefault() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => analystApi.ensureDefault(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["analyst", "default"] });
    },
  });
}

export function useAnalystDryRun() {
  return useMutation({
    mutationFn: (body: AnalystDryRunRequest) => analystApi.dryRun(body),
  });
}
