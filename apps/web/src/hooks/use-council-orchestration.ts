"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  councilOrchestrationApi,
  CreateCouncilOrchestrationRequest,
  CouncilOrchestrationResponse,
  CouncilOrchestrationRun,
  CouncilAvatarTurn,
} from "@/lib/api";

export function useCouncilOrchestrationCreate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateCouncilOrchestrationRequest): Promise<CouncilOrchestrationResponse> =>
      councilOrchestrationApi.create(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["council-orchestrations"] });
    },
  });
}

export function useCouncilOrchestrationList(limit?: number) {
  return useQuery({
    queryKey: ["council-orchestrations", limit],
    queryFn: (): Promise<CouncilOrchestrationRun[]> => councilOrchestrationApi.list(limit),
  });
}

export function useCouncilOrchestrationGet(id: string) {
  return useQuery({
    queryKey: ["council-orchestrations", id],
    queryFn: (): Promise<CouncilOrchestrationRun> => councilOrchestrationApi.get(id),
    enabled: !!id,
  });
}

export function useCouncilOrchestrationTurns(id: string) {
  return useQuery({
    queryKey: ["council-orchestrations", id, "turns"],
    queryFn: (): Promise<CouncilAvatarTurn[]> => councilOrchestrationApi.listTurns(id),
    enabled: !!id,
  });
}

export function useCouncilOrchestrationPresence(id: string) {
  return useQuery({
    queryKey: ["council-orchestrations", id, "presence"],
    queryFn: () => councilOrchestrationApi.listPresence(id),
    enabled: !!id,
  });
}

export function useCouncilOrchestrationDebateEvents(id: string) {
  return useQuery({
    queryKey: ["council-orchestrations", id, "debate-events"],
    queryFn: () => councilOrchestrationApi.listDebateEvents(id),
    enabled: !!id,
  });
}
