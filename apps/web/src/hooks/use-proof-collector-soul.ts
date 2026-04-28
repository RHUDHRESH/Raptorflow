"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { proofCollectorApi, ProofCollectorDryRunRequest } from "@/lib/api";

export function useProofCollectorDefault() {
  return useQuery({
    queryKey: ["proof-collector", "default"],
    queryFn: () => proofCollectorApi.ensureDefault(),
  });
}

export function useEnsureProofCollectorDefault() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => proofCollectorApi.ensureDefault(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proof-collector", "default"] });
    },
  });
}

export function useProofCollectorDryRun() {
  return useMutation({
    mutationFn: (body: ProofCollectorDryRunRequest) => proofCollectorApi.dryRun(body),
  });
}
