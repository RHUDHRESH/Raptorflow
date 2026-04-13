"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { prlApi } from "@/lib/api";
import type {
  CreateRippleRequest,
  UpdateRippleRequest,
  CreateEdgeRequest,
  CreateEssenceRequest,
  UpdateEssenceRequest,
} from "@/lib/api";

export function useRipples() {
  return useQuery({
    queryKey: ["prl", "ripples"],
    queryFn: () => prlApi.listRipples(),
  });
}

export function useRipple(id: string) {
  return useQuery({
    queryKey: ["prl", "ripples", id],
    queryFn: () => prlApi.getRipple(id),
    enabled: !!id,
  });
}

export function useRippleEdges(rippleId: string) {
  return useQuery({
    queryKey: ["prl", "ripples", rippleId, "edges"],
    queryFn: () => prlApi.getRippleEdges(rippleId),
    enabled: !!rippleId,
  });
}

export function useCreateRipple() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateRippleRequest) => prlApi.createRipple(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prl", "ripples"] });
    },
  });
}

export function useUpdateRipple() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateRippleRequest }) =>
      prlApi.updateRipple(id, body),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["prl", "ripples"] });
      queryClient.invalidateQueries({ queryKey: ["prl", "ripples", id] });
    },
  });
}

export function useDeleteRipple() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => prlApi.deleteRipple(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prl", "ripples"] });
    },
  });
}

export function useRealizeRipple() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => prlApi.realizeRipple(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prl", "ripples"] });
    },
  });
}

export function useCreateRippleEdge() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: CreateEdgeRequest }) =>
      prlApi.createRippleEdge(id, body),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["prl", "ripples", id, "edges"] });
    },
  });
}

export function useDeleteRippleEdge() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ rippleId, edgeId }: { rippleId: string; edgeId: string }) =>
      prlApi.deleteRippleEdge(edgeId),
    onSuccess: (_, { rippleId }) => {
      queryClient.invalidateQueries({ queryKey: ["prl", "ripples", rippleId, "edges"] });
    },
  });
}

export function useEssences() {
  return useQuery({
    queryKey: ["prl", "essences"],
    queryFn: () => prlApi.listEssences(),
  });
}

export function useEssence(id: string) {
  return useQuery({
    queryKey: ["prl", "essences", id],
    queryFn: () => prlApi.getEssence(id),
    enabled: !!id,
  });
}

export function useCreateEssence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateEssenceRequest) => prlApi.createEssence(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prl", "essences"] });
    },
  });
}

export function useUpdateEssence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateEssenceRequest }) =>
      prlApi.updateEssence(id, body),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["prl", "essences"] });
      queryClient.invalidateQueries({ queryKey: ["prl", "essences", id] });
    },
  });
}

export function useRunDecay() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => prlApi.runDecay(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prl"] });
    },
  });
}
