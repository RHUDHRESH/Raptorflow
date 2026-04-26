"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { copywriterApi, CopywriterDryRunRequest } from "@/lib/api";

export function useCopywriterDefault() {
  return useQuery({
    queryKey: ["copywriter", "default"],
    queryFn: () => copywriterApi.ensureDefault(),
  });
}

export function useEnsureCopywriterDefault() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => copywriterApi.ensureDefault(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["copywriter", "default"] });
    },
  });
}

export function useCopywriterDryRun() {
  return useMutation({
    mutationFn: (body: CopywriterDryRunRequest) => copywriterApi.dryRun(body),
  });
}
