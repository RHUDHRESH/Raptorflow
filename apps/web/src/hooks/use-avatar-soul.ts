"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { avatarSoulApi } from "@/lib/api";

export function useAvatarSoul(avatarId: string) {
  return useQuery({
    queryKey: ["avatars", avatarId, "soul"],
    queryFn: () => avatarSoulApi.getSoul(avatarId),
    enabled: !!avatarId,
  });
}

export function useUpdateAvatarSoul() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      avatarId,
      body,
    }: {
      avatarId: string;
      body: Parameters<typeof avatarSoulApi.updateSoul>[1];
    }) => avatarSoulApi.updateSoul(avatarId, body),
    onSuccess: (_, { avatarId }) => {
      queryClient.invalidateQueries({ queryKey: ["avatars", avatarId, "soul"] });
    },
  });
}

export function useAvatarMemoryEdges(avatarId: string) {
  return useQuery({
    queryKey: ["avatars", avatarId, "memory", "edges"],
    queryFn: () => avatarSoulApi.listMemoryEdges(avatarId),
    enabled: !!avatarId,
  });
}

export function useCreateAvatarMemoryEdge() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      avatarId,
      body,
    }: {
      avatarId: string;
      body: Parameters<typeof avatarSoulApi.createMemoryEdge>[1];
    }) => avatarSoulApi.createMemoryEdge(avatarId, body),
    onSuccess: (_, { avatarId }) => {
      queryClient.invalidateQueries({ queryKey: ["avatars", avatarId, "memory", "edges"] });
    },
  });
}

export function useDeleteAvatarMemoryEdge() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ avatarId, edgeId }: { avatarId: string; edgeId: string }) =>
      avatarSoulApi.deleteMemoryEdge(avatarId, edgeId),
    onSuccess: (_, { avatarId }) => {
      queryClient.invalidateQueries({ queryKey: ["avatars", avatarId, "memory", "edges"] });
    },
  });
}

export function useCreateInstinctFrame() {
  return useMutation({
    mutationFn: ({
      avatarId,
      body,
    }: {
      avatarId: string;
      body: Parameters<typeof avatarSoulApi.createInstinctFrame>[1];
    }) => avatarSoulApi.createInstinctFrame(avatarId, body),
  });
}

export function useHarnessPresence(runId: string) {
  return useQuery({
    queryKey: ["harness", "runs", runId, "presence"],
    queryFn: () => avatarSoulApi.listPresenceStates(runId),
    enabled: !!runId,
  });
}

export function useUpsertPresenceState() {
  return useMutation({
    mutationFn: ({
      runId,
      body,
    }: {
      runId: string;
      body: Parameters<typeof avatarSoulApi.upsertPresenceState>[1];
    }) => avatarSoulApi.upsertPresenceState(runId, body),
  });
}

export function useDebateEvents(runId: string) {
  return useQuery({
    queryKey: ["harness", "runs", runId, "debate-events"],
    queryFn: () => avatarSoulApi.listDebateEvents(runId),
    enabled: !!runId,
  });
}

export function useCreateDebateEvent() {
  return useMutation({
    mutationFn: ({
      runId,
      body,
    }: {
      runId: string;
      body: Parameters<typeof avatarSoulApi.createDebateEvent>[1];
    }) => avatarSoulApi.createDebateEvent(runId, body),
  });
}

export function useAvatarArtifactTrail(avatarId: string) {
  return useQuery({
    queryKey: ["avatars", avatarId, "artifact-trail"],
    queryFn: () => avatarSoulApi.getArtifactTrail(avatarId),
    enabled: !!avatarId,
  });
}
