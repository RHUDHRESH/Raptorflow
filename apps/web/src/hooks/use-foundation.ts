"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { foundationApi } from "@/lib/api";

export function useFoundation() {
  return useQuery({
    queryKey: ["foundation"],
    queryFn: () => foundationApi.get(),
    staleTime: 30_000,
  });
}

export function useFoundationSnapshots() {
  return useQuery({
    queryKey: ["foundation", "snapshots"],
    queryFn: () => foundationApi.listSnapshots(),
  });
}

export function useFoundationSnapshot(id: string) {
  return useQuery({
    queryKey: ["foundation", "snapshots", id],
    queryFn: () => foundationApi.getSnapshot(id),
    enabled: !!id,
  });
}

export function useUpdateFoundationSection() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ section, value }: { section: string; value: unknown }) =>
      foundationApi.updateSection(section, { value }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["foundation"] });
    },
  });
}

export function useCreateFoundationSnapshot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => foundationApi.createSnapshot(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["foundation", "snapshots"] });
    },
  });
}

export function useRestoreFoundationSnapshot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => foundationApi.restoreSnapshot(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["foundation"] });
      queryClient.invalidateQueries({ queryKey: ["foundation", "snapshots"] });
    },
  });
}

export function useTriggerFoundationScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (mode: "quick" | "deep") => foundationApi.triggerScan(mode),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["foundation"] });
    },
  });
}

export function useFoundationScanStatus(jobId: string) {
  return useQuery({
    queryKey: ["foundation", "scan", jobId],
    queryFn: () => foundationApi.getScanStatus(jobId),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed") return false;
      return 2_000;
    },
  });
}
