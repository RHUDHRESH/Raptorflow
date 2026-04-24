"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { councilApi, type StartCouncilRequest } from "@/lib/api";

export function useCouncilSessions() {
  return useQuery({
    queryKey: ["council", "sessions"],
    queryFn: () => councilApi.listSessions(),
  });
}

export function useCouncilSession(id: string) {
  return useQuery({
    queryKey: ["council", "sessions", id],
    queryFn: () => councilApi.getSession(id),
    enabled: !!id,
  });
}

export function useCouncilMessages(sessionId: string) {
  return useQuery({
    queryKey: ["council", "sessions", sessionId, "messages"],
    queryFn: () => councilApi.getMessages(sessionId),
    enabled: !!sessionId,
  });
}

export function useStartCouncilSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: StartCouncilRequest) => councilApi.startSession(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["council", "sessions"] });
    },
  });
}
