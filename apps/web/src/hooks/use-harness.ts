"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { harnessApi } from "@/lib/api";

export function useHarnessRuns() {
  return useQuery({
    queryKey: ["harness", "runs"],
    queryFn: () => harnessApi.listRuns(),
  });
}

export function useHarnessRun(id: string) {
  return useQuery({
    queryKey: ["harness", "runs", id],
    queryFn: () => harnessApi.getRun(id),
    enabled: !!id,
  });
}

export function useHarnessSteps(runId: string) {
  return useQuery({
    queryKey: ["harness", "runs", runId, "steps"],
    queryFn: () => harnessApi.listSteps(runId),
    enabled: !!runId,
  });
}

export function useCreateHarnessRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: Parameters<typeof harnessApi.createRun>[0]) => harnessApi.createRun(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["harness", "runs"] });
    },
  });
}

export function useCancelHarnessRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => harnessApi.cancelRun(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["harness", "runs"] });
      queryClient.invalidateQueries({ queryKey: ["harness", "runs", id] });
    },
  });
}
