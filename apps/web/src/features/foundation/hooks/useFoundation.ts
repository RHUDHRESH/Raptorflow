"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { foundationApi } from "@/lib/api";
import type { QuickScanResult } from "@/lib/api";

export interface FoundationData {
  id?: string;
  orgId: string;
  version: number;
  sections: Record<string, unknown>;
  updatedAt: string;
}

export interface TriggerQuickScanResponse {
  scan: QuickScanResult;
  scannedAt: string;
}

export function useFoundation() {
  return useQuery<FoundationData>({
    queryKey: ["foundation"],
    queryFn: () => foundationApi.get() as Promise<FoundationData>,
    staleTime: 60_000,
    retry: false,
  });
}

export function useSaveFoundation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (fields: Record<string, unknown>) => foundationApi.savePartial(fields, "PATCH"),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["foundation"] });
    },
  });
}

export function useFoundationScan() {
  const queryClient = useQueryClient();

  return useMutation<TriggerQuickScanResponse>({
    mutationFn: () => foundationApi.triggerQuickScan(),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["foundation"] });
    },
  });
}
