"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { avatarsApi } from "@/lib/api";

export function useAvatars() {
  return useQuery({
    queryKey: ["avatars"],
    queryFn: () => avatarsApi.list(),
  });
}

export function useAvatar(id: string) {
  return useQuery({
    queryKey: ["avatars", id],
    queryFn: () => avatarsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateAvatar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: Parameters<typeof avatarsApi.create>[0]) => avatarsApi.create(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["avatars"] });
    },
  });
}

export function useUpdateAvatar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, patch }: { id: string; patch: Parameters<typeof avatarsApi.update>[1] }) =>
      avatarsApi.update(id, patch),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["avatars"] });
      queryClient.invalidateQueries({ queryKey: ["avatars", id] });
    },
  });
}

export function useDeleteAvatar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => avatarsApi.deactivate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["avatars"] });
    },
  });
}

export function useEnsureAvatarDefaults() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => avatarsApi.ensureDefaults(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["avatars"] });
    },
  });
}
