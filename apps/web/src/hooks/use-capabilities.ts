"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { capabilitiesApi } from "@/lib/api";

export function useCapabilities() {
  return useQuery({
    queryKey: ["capabilities"],
    queryFn: () => capabilitiesApi.list(),
  });
}

export function useCapability(id: string) {
  return useQuery({
    queryKey: ["capabilities", id],
    queryFn: () => capabilitiesApi.get(id),
    enabled: !!id,
  });
}

export function useCapabilityByKey(key: string) {
  return useQuery({
    queryKey: ["capabilities", "key", key],
    queryFn: () => capabilitiesApi.getByKey(key),
    enabled: !!key,
  });
}

export function useEnsureDefaultCapabilities() {
  return useMutation({
    mutationFn: () => capabilitiesApi.ensureDefaults(),
  });
}

export function useAvatarCapabilities(avatarId: string) {
  return useQuery({
    queryKey: ["avatars", avatarId, "capabilities"],
    queryFn: () => capabilitiesApi.listAvatarCapabilities(avatarId),
    enabled: !!avatarId,
  });
}

export function useGrantCapabilityToAvatar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      avatarId,
      body,
    }: {
      avatarId: string;
      body: Parameters<typeof capabilitiesApi.grantToAvatar>[1];
    }) => capabilitiesApi.grantToAvatar(avatarId, body),
    onSuccess: (_, { avatarId }) => {
      queryClient.invalidateQueries({ queryKey: ["avatars", avatarId, "capabilities"] });
    },
  });
}

export function useRevokeCapabilityFromAvatar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ avatarId, capabilityId }: { avatarId: string; capabilityId: string }) =>
      capabilitiesApi.revokeFromAvatar(avatarId, capabilityId),
    onSuccess: (_, { avatarId }) => {
      queryClient.invalidateQueries({ queryKey: ["avatars", avatarId, "capabilities"] });
    },
  });
}
